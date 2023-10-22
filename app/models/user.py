from sqlalchemy import Column, Integer, String, Enum
from database import db

UserRole = Enum('Mahasiswa', 'Admin Lab', name="user_role")

class User(db.Model):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True)
    username = Column(String, unique=True)
    email = Column(String, unique=True)
    password = Column(String)
    role = Column(UserRole)
    personal_data = Column(String)
    photo = Column(String)
    self_photo = Column(String)
