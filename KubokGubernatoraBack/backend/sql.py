
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

# Пример модели
class User(db.Model):
    email = db.Column(db.String(120), primary_key=True, nullable=False)
    password = db.Column(db.String(128), nullable=False)
    user_type = db.Column(db.String(40), nullable=False)


    def __repr__(self):
        return f'<User {self.email}>'


class UserInfo(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)  # Добавляем уникальный идентификатор для UserInfo
    email = db.Column(db.String(120), db.ForeignKey('user.email'), nullable=False)  # Связываем с таблицей User
    full_name = db.Column(db.String(100), nullable=False)  # Поле для ФИО
    birth_date = db.Column(db.Date, nullable=False)  # Поле для даты рождения
    city = db.Column(db.String(100))  # Поле для города проживания

    user = db.relationship('User', backref='user_info')  # Создаем обратное отношение

    def __repr__(self):
        return f'<UserInfo {self.email}>'


class FreelancerInfo(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    email = db.Column(db.String(120), db.ForeignKey('user.email'), nullable=False)
    full_name = db.Column(db.String(100), nullable=False)  # Поле для ФИО
    nickname = db.Column(db.String(50))  # Поле для псевдонима
    experience_years = db.Column(db.String(20))  # Поле для количества лет опыта
    skills = db.Column(db.String(255))  # Поле для ключевых навыков
    telegram = db.Column(db.String(50))  # Поле для никнейма в Telegram
    github = db.Column(db.String(50))  # Поле для репозитория на GitHub
    resume_link = db.Column(db.String(255))  # Поле для ссылки на резюме

    user = db.relationship('User', backref='freelancer_info')  # Создаем обратное отношение

    def __repr__(self):
        return f'<FreelancerInfo {self.full_name}>'

class Company(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), db.ForeignKey('user.email'), nullable=False)
    company_name = db.Column(db.String(255))
    inn = db.Column(db.String(10))
    registration_date = db.Column(db.Date)
    legal_address = db.Column(db.String(255))
    director_name = db.Column(db.String(255))
    contact = db.Column(db.String(255))

    user = db.relationship('User', backref='company_info')  # Создаем обратное отношение

def init_db(app):
    with app.app_context():
        db.create_all()

