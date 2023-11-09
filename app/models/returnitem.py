from enum import Enum as PyEnum
from sqlalchemy import Column, Integer, ForeignKey, DateTime, Enum, func
from sqlalchemy.orm import relationship
from database import db

class ReturnStatus(PyEnum):
    CONFIRM = "Menunggu Konfirmasi"
    ACCEPTED = "Disetujui"
    REJECTED = "Ditolak"

class Return(db.Model):
    __tablename__ = 'returns'

    id = Column(Integer, primary_key=True)

    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    product_id = Column(Integer, ForeignKey('products.id'), nullable=False)
    loan_id = Column(Integer, ForeignKey('loans.id'), nullable=False)
    returned_quantity = Column(Integer, nullable=False)
    status = Column(Enum(ReturnStatus), default=ReturnStatus.CONFIRM, nullable=False)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())

    user = relationship('User', backref='users')
    loan = relationship('Loan', backref='loans')
    product = relationship('Product', backref='products')