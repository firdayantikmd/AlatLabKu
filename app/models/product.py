from sqlalchemy import Column, Integer, String, Enum, DateTime, func
from database import db

ProductType = Enum('Bahan', 'Alat', name="product_type")
ProductStatus = Enum('Tersedia', 'Tidak Tersedia', name='product_status')

class Product(db.Model):
    __tablename__ = 'products'

    id = Column(Integer, primary_key=True)
    product_name = Column(String)
    product_image = Column(String)
    category = Column(ProductType)
    storage = Column(String)
    created_at = Column(DateTime, default=func.now())
    stock = Column(Integer)
    details = Column(String)
    status = Column(ProductStatus)