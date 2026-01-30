"""
ProductVariant model and logic
"""
from datetime import datetime
from typing import List, Optional
from sqlalchemy import String, Float, Integer, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship, Session
from .base import Base

class ProductVariant(Base):
    __tablename__ = "product_variants"
    id: Mapped[int] = mapped_column(primary_key=True)
    product_id: Mapped[int] = mapped_column(ForeignKey("products.id"))
    variant_name: Mapped[str] = mapped_column(String(100))
    price: Mapped[float] = mapped_column(Float)
    stock: Mapped[int] = mapped_column(Integer, default=0)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    product: Mapped["Product"] = relationship(back_populates="variants")
    cart_items: Mapped[List["Cart"]] = relationship(back_populates="variant")
    order_items: Mapped[List["OrderItem"]] = relationship(back_populates="variant")

    @staticmethod
    def get_by_product(session: Session, product_id: int) -> List["ProductVariant"]:
        return session.query(ProductVariant).filter(
            ProductVariant.product_id == product_id,
            ProductVariant.is_active == True
        ).order_by(ProductVariant.id).all()

    @staticmethod
    def get_by_id(session: Session, variant_id: int) -> Optional["ProductVariant"]:
        return session.query(ProductVariant).filter(ProductVariant.id == variant_id).first()

    @staticmethod
    def create(session: Session, product_id: int, variant_name: str, price: float, stock: int = 0) -> "ProductVariant":
        variant = ProductVariant(
            product_id=product_id,
            variant_name=variant_name,
            price=price,
            stock=stock
        )
        session.add(variant)
        session.flush()
        return variant
