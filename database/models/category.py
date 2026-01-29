"""
Category model and logic
"""
from datetime import datetime
from typing import Optional, List
from sqlalchemy import String, Text, Boolean, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship, Session
from .base import Base

class Category(Base):
    __tablename__ = "categories"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100), unique=True)
    description: Mapped[Optional[str]] = mapped_column(Text)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    products: Mapped[List["Product"]] = relationship(back_populates="category", cascade="all, delete-orphan")

    @staticmethod
    def get_all(session: Session) -> List["Category"]:
        return session.query(Category).filter(Category.is_active == True).order_by(Category.name).all()

    @staticmethod
    def get_by_id(session: Session, category_id: int) -> Optional["Category"]:
        return session.query(Category).filter(Category.id == category_id).first()

    @staticmethod
    def create(session: Session, name: str, description: str = "") -> "Category":
        category = Category(name=name, description=description)
        session.add(category)
        session.flush()
        return category
