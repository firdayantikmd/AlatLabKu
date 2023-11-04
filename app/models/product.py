from sqlalchemy import Column, Integer, String, Enum, DateTime, func
from database import db

ProductType = Enum('Bahan', 'Alat', name="product_type")

class Product(db.Model):
    __tablename__ = 'products'

    id = Column(Integer, primary_key=True)
    product_name = Column(String)
    product_image = Column(String)
    category = Column(ProductType)
    storage = Column(String)
    stock = Column(Integer, default=0)
    details = Column(String)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())