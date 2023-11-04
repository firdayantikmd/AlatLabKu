from sqlalchemy import Column, Integer, String, Enum, DateTime, func
from database import db

UserRole = Enum('Mahasiswa', 'Admin Lab', name="user_role")

class User(db.Model):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True)
    username = Column(String, unique=True)
    password = Column(String)
    full_name = Column(String)
    email = Column(String, unique=True)
    no_hp = Column(String, unique=True)
    self_photo = Column(String)
    card_photo = Column(String)
    student_id = Column(String, unique=True)
    role = Column(UserRole)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
