"""
Subcategory model and logic
"""
from datetime import datetime
from typing import Optional, List
from sqlalchemy import String, Text, Boolean, DateTime, ForeignKey, Integer
from sqlalchemy.orm import Mapped, mapped_column, relationship, Session
from .base import Base

from .category import Category
from .product import Product

class Subcategory(Base):
    __tablename__ = "subcategories"
    id: Mapped[int] = mapped_column(primary_key=True)
    category_id: Mapped[int] = mapped_column(ForeignKey("categories.id"))
    name: Mapped[str] = mapped_column(String(100))
    description: Mapped[Optional[str]] = mapped_column(Text)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    category: Mapped["Category"] = relationship(back_populates="subcategories")
    products: Mapped[List["Product"]] = relationship(back_populates="subcategory", cascade="all, delete-orphan")

    @staticmethod
    def get_by_category(session: Session, category_id: int) -> List["Subcategory"]:
        return session.query(Subcategory).filter(
            Subcategory.category_id == category_id,
            Subcategory.is_active == True
        ).order_by(Subcategory.name).all()

    @staticmethod
    def get_by_id(session: Session, subcategory_id: int) -> Optional["Subcategory"]:
        return session.query(Subcategory).filter(Subcategory.id == subcategory_id).first()

    @staticmethod
    def create(session: Session, category_id: int, name: str, description: str = "") -> "Subcategory":
        subcategory = Subcategory(category_id=category_id, name=name, description=description)
        session.add(subcategory)
        session.flush()
        return subcategory
