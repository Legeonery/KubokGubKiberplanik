
from flask import Flask, request, jsonify
from flask_restful import Api, Resource
from config import Config
from sql import db, init_db, User, UserInfo, FreelancerInfo, Company
import re
from datetime import datetime, timedelta  
import config
from flask_cors import CORS
from flask_jwt_extended import jwt_required, JWTManager, create_access_token, get_jwt_identity

from datetime import datetime


app = Flask(__name__)
CORS(app)
app.config.from_object(Config)

db.init_app(app)

api = Api(app)

app.config['JWT_SECRET_KEY'] = config.Secrets.api  
app.config['JWT_TOKEN_LOCATION'] = ['headers']  # Укажите, где ищется токен (заголовки, куки и т.д.)
app.config['JWT_HEADER_TYPE'] = 'Bearer'  # Укажите тип заголовка
jwt = JWTManager(app)

def validate_password(password):
    if (
        len(password) < 8 or
        not re.search(r'[A-Z]', password) or
        not re.search(r'[a-z]', password) or
        not re.search(r'[0-9]', password) or
        not re.search(r'[!@#$%^&*(),.?":{}|<>]', password)
    ):
        return False
    return True

class UserRegistration(Resource):
    def post(self):
        data = request.get_json()
        email = data.get('email')
        password = data.get('password')
        user_type = data.get('userType')
        if not email or not password or not user_type:
            return {'message': 'Email, password and user_type are required.'}, 400

        if not validate_password(password):
            return {'message': 'Password must be at least 8 characters long, '
                               'contain at least one uppercase letter, one lowercase letter, '
                               'one digit, and one special character.'}, 400

        existing_user = User.query.filter_by(email=email).first()
        if existing_user:
            return {'message': 'User with that email already exists.'}, 400

        # # Хэширование пароля перед сохранением (необходимо для безопасности)
        # hashed_password = hash_password(password)  # Обязательно реализуйте функцию hash_password
        
        new_user = User(email=email, password=password, user_type=user_type)
        db.session.add(new_user)
        db.session.commit()
        token = create_access_token(
            identity=email,
            expires_delta=timedelta(hours=12)  # Используйте timedelta здесь
        )
        return {'message': 'User registered successfully.', 'token': token}, 201

class UserLogin(Resource):
    def post(self):
        data = request.get_json()
        email = data.get('email')
        password = data.get('password')
        if not email or not password:
            return {'message': 'Email and password are required.'}, 400

        # Проверка существующего пользователя
        existing_user = User.query.filter_by(email=email).first()
        if existing_user and existing_user.password == password:  
            # Генерация JWT
            token = create_access_token(
            identity=email,
            expires_delta=timedelta(hours=12)  # Используйте timedelta здесь
        )

            return {'message': 'User registered successfully.', 'token': token, 'userType': existing_user.user_type}, 201

        return {'message': 'Invalid email or password.'}, 401



class UserInfoAdd(Resource):
    @jwt_required()
    def post(self):
        data = request.get_json()
        email = data.get('email')
        full_name = data.get('fullName')
        birth_date_str = data.get('birthDate')

        if birth_date_str:  # Проверяем, что строка не пустая
            birth_date = datetime.strptime(birth_date_str, '%Y-%m-%d').date()  # Преобразование
        else:
            birth_date = None  # Или любое другое значение по умолчанию
        city = data.get('city')

        if not email or not full_name or not birth_date or not city:
            return {'message': 'Email, ФИО, дата рождения и город проживания обязательны.'}, 400

        existing_user = User.query.filter_by(email=email).first()
        if not existing_user:
            return {'message': 'Пользователь с таким email не найден.'}, 404

        user_info = UserInfo.query.filter_by(email=email).first()

        if user_info:
            # Если запись существует, обновляем её
            user_info.full_name = full_name
            user_info.birth_date = birth_date
            user_info.city = city
        else:
            # Если записи нет, создаем новую
            user_info = UserInfo(
                email=email,
                full_name=full_name,
                birth_date=birth_date,
                city=city,
            )
            db.session.add(user_info)

        db.session.commit()

        return {'message': 'Данные пользователя успешно обновлены.'}, 200


    @jwt_required()
    def get(self):
        current_user_email = get_jwt_identity()
        user_info = UserInfo.query.filter_by(email=current_user_email).first()
        if user_info:
            return {
                'email': user_info.email,
                'fullName': user_info.full_name,
                'birthDate': user_info.birth_date.strftime('%Y-%m-%d'),  # Преобразование формата даты
                'city': user_info.city,
            }, 200
        return {'message': 'Пользователь не найден.'}, 404

class FreelancerInfoAdd(Resource):
    
    @jwt_required()
    def post(self):
        current_user_email = get_jwt_identity()
        data = request.get_json()

        full_name = data.get('fullName')
        nickname = data.get('nickname')
        experience_years = data.get('experienceYears')
        skills = data.get('skills')
        telegram = data.get('telegram')
        github = data.get('github')
        resume_link = data.get('resumeLink')

        # Проверка обязательных полей
        if not full_name or not experience_years or not skills:
            return {'message': 'ФИО, количество лет опыта и ключевые навыки обязательны.'}, 400

        # Проверка существования пользователя
        existing_user = User.query.filter_by(email=current_user_email).first()
        if not existing_user:
            return {'message': 'Пользователь с таким email не найден.'}, 404

        # Получение информации о фрилансере
        freelancer_info = FreelancerInfo.query.filter_by(email=current_user_email).first()

        if freelancer_info:
            # Обновление записи
            freelancer_info.full_name = full_name
            freelancer_info.nickname = nickname
            freelancer_info.experience_years = experience_years
            freelancer_info.skills = skills
            freelancer_info.telegram = telegram
            freelancer_info.github = github
            freelancer_info.resume_link = resume_link
        else:
            # Создание новой записи
            freelancer_info = FreelancerInfo(
                email=current_user_email,
                full_name=full_name,
                nickname=nickname,
                experience_years=experience_years,
                skills=skills,
                telegram=telegram,
                github=github,
                resume_link=resume_link
            )
            db.session.add(freelancer_info)

        try:
            db.session.commit()
            return {'message': 'Информация о фрилансере успешно обновлена.'}, 200
        except Exception as e:
            db.session.rollback()
            return {'message': 'Ошибка при обновлении информации о фрилансере: ' + str(e)}, 500



    @jwt_required()
    def get(self):
        current_user_email = get_jwt_identity()
        print(current_user_email)
        freelancer_info = FreelancerInfo.query.filter_by(email=current_user_email).first()

        if freelancer_info:
            return {
                'email': freelancer_info.email,
                'fullName': freelancer_info.full_name,
                'nickname': freelancer_info.nickname,
                'experienceYears': freelancer_info.experience_years,
                'skills': freelancer_info.skills,
                'telegram': freelancer_info.telegram,
                'github': freelancer_info.github,
                'resumeLink': freelancer_info.resume_link,
            }, 200
        return {'message': 'Информация о фрилансере не найдена.'}, 404

class CompanyInfoAdd(Resource):
    @jwt_required()
    def post(self):
        current_user_email = get_jwt_identity()
        data = request.get_json()
        
        company_name = data.get('company_name')
        inn = data.get('inn')  
        registration_date_str = data.get('registration_date')
        legal_address = data.get('legal_address')
        director_name = data.get('director_name')
        contacts = data.get('contacts')

        if not registration_date_str:
            return {'message': 'Заполните дату регистрации'}, 400

        try:
            registration_date = datetime.strptime(registration_date_str, '%Y-%m-%d').date()
        except ValueError as e:
            return {'message': 'Ошибка в формате даты: ' + str(e)}, 400

        # Проверка обязательных полей
        if not company_name or not inn or not registration_date or not legal_address or not director_name:
            return {'message': 'Название компании, ИНН, дата регистрации, юридический адрес и имя директора обязательны.'}, 400

        # Проверка существования пользователя
        existing_user = User.query.filter_by(email=current_user_email).first()
        if not existing_user:
            return {'message': 'Пользователь с таким email не найден.'}, 404

        # Получение информации о компании
        company_info = Company.query.filter_by(email=current_user_email).first()

        if company_info:
            # Обновление записи
            company_info.company_name = company_name
            company_info.inn = inn
            company_info.registration_date = registration_date
            company_info.legal_address = legal_address
            company_info.director_name = director_name
            company_info.contact = contacts
        else:
            # Создание новой записи
            company_info = Company(
                email=current_user_email,
                company_name=company_name,
                inn=inn,
                registration_date=registration_date,
                legal_address=legal_address,
                director_name=director_name,
                contact=contacts
            )
            db.session.add(company_info)

        try:
            db.session.commit()
            return {'message': 'Информация о компании успешно обновлена.'}, 200
        except Exception as e:
            db.session.rollback()
            return {'message': 'Ошибка при обновлении информации о компании', 'error': str(e)}, 500



    @jwt_required()
    def get(self):
        current_user_email = get_jwt_identity()
        company_info = CompanyInfo.query.filter_by(email=current_user_email).first()  # Предполагается, что у вас есть связь между пользователем и компанией по email
        result = {}
        if company_info:
            result['companyName'] = company_info.company_name
            result['inn'] = company_info.inn
            result['registrationDate'] = company_info.registration_date
            result['legalAddress'] = company_info.legal_address
            result['directorName'] = company_info.director_name
            result['contact'] = company_info.contacts

        if result:
            return result, 200

        return {'message': 'Информация о фрилансере и компании не найдена.'}, 404


api.add_resource(UserRegistration, '/user/registration')
api.add_resource(UserLogin, '/user/login')
api.add_resource(UserInfoAdd, '/user/account/profile/addinfo')
api.add_resource(FreelancerInfoAdd, '/user/account/freelancer/addinfo')
api.add_resource(CompanyInfoAdd, '/user/account/company/addinfo')



if __name__ == '__main__':
    init_db(app)
    app.run(debug=True)


