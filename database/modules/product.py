"""
Product model and logic
"""
from datetime import datetime
from typing import List
from sqlalchemy import String, Text, Boolean, DateTime, ForeignKey, Integer
from sqlalchemy.orm import Mapped, mapped_column, relationship, Session
from .base import Base
from .subcategory import Subcategory
from .product_variant import ProductVariant
from .product_image import ProductImage

class Product(Base):
    __tablename__ = "products"
    id: Mapped[int] = mapped_column(primary_key=True)
    subcategory_id: Mapped[int] = mapped_column(ForeignKey("subcategories.id"))
    name: Mapped[str] = mapped_column(String(200))
    description: Mapped[str] = mapped_column(Text)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    subcategory: Mapped["Subcategory"] = relationship(back_populates="products")
    variants: Mapped[List["ProductVariant"]] = relationship(back_populates="product", cascade="all, delete-orphan")
    images: Mapped[List["ProductImage"]] = relationship(back_populates="product", cascade="all, delete-orphan")

    @staticmethod
    def get_by_subcategory(session: Session, subcategory_id: int) -> List["Product"]:
        return session.query(Product).filter(
            Product.subcategory_id == subcategory_id,
            Product.is_active == True
        ).order_by(Product.name).all()

    @staticmethod
    def get_by_id(session: Session, product_id: int):
        return session.query(Product).filter(Product.id == product_id).first()

    @staticmethod
    def create(session: Session, subcategory_id: int, name: str, description: str = ""):
        product = Product(subcategory_id=subcategory_id, name=name, description=description)
        session.add(product)
        session.flush()
        return product
