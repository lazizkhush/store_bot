"""
User model and logic
"""
from datetime import datetime
from typing import Optional, List
from sqlalchemy import BigInteger, String, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship, Session
from .base import Base

from .order import Order
from .cart import Cart

class User(Base):
    __tablename__ = "users"
    id: Mapped[int] = mapped_column(primary_key=True)
    telegram_id: Mapped[int] = mapped_column(BigInteger, unique=True, index=True)
    phone_number: Mapped[Optional[str]] = mapped_column(String(20))
    first_name: Mapped[str] = mapped_column(String(100))
    last_name: Mapped[Optional[str]] = mapped_column(String(100))
    username: Mapped[Optional[str]] = mapped_column(String(100))
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    orders: Mapped[List["Order"]] = relationship(back_populates="user", cascade="all, delete-orphan")
    cart_items: Mapped[List["Cart"]] = relationship(back_populates="user", cascade="all, delete-orphan")

    @staticmethod
    def get_by_telegram_id(session: Session, telegram_id: int) -> Optional["User"]:
        return session.query(User).filter(User.telegram_id == telegram_id).first()

    @staticmethod
    def get_by_id(session: Session, user_id: int) -> Optional["User"]:
        return session.query(User).filter(User.id == user_id).first()

    @staticmethod
    def create(session: Session, telegram_id: int, phone_number: str, first_name: str, last_name: str = "", username: str = "") -> "User":
        user = User(
            telegram_id=telegram_id,
            phone_number=phone_number,
            first_name=first_name,
            last_name=last_name,
            username=username
        )
        session.add(user)
        session.flush()
        return user
