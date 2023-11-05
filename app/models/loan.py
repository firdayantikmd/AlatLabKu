from enum import Enum as PyEnum
from sqlalchemy import Column, Integer, ForeignKey, DateTime, Enum, func
from sqlalchemy.orm import relationship
from database import db

class LoanStatus(PyEnum):
    CONFIRM = "Menunggu Konfirmasi"
    ACCEPTED = "Disetujui"
    REJECTED = "Ditolak"
    ON_LOAN = 'Sedang Dipinjam'

class Loan(db.Model):
    __tablename__ = 'loans'

    id = Column(Integer, primary_key=True)
    
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    product_id = Column(Integer, ForeignKey('products.id'), nullable=False)
    quantity = Column(Integer, nullable=False)
    status = Column(Enum(LoanStatus), default=LoanStatus.CONFIRM, nullable=False)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())

    user = relationship('User', backref='loans')
    product = relationship('Product', backref='loans')
