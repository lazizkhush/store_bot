"""
Order model and logic
"""
from datetime import datetime
from typing import List, Optional
from sqlalchemy import Float, String, DateTime, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship, Session
from .base import Base
from .order_item import OrderItem
from .user import User

class Order(Base):
    __tablename__ = "orders"
    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    total_price: Mapped[float] = mapped_column(Float)
    status: Mapped[str] = mapped_column(String(20), default="pending")
    delivery_latitude: Mapped[float] = mapped_column(Float)
    delivery_longitude: Mapped[float] = mapped_column(Float)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    user: Mapped["User"] = relationship(back_populates="orders")
    items: Mapped[List["OrderItem"]] = relationship(back_populates="order", cascade="all, delete-orphan")

    @staticmethod
    def create(session: Session, user_id: int, total_price: float, latitude: float, longitude: float) -> "Order":
        order = Order(
            user_id=user_id,
            total_price=total_price,
            delivery_latitude=latitude,
            delivery_longitude=longitude
        )
        session.add(order)
        session.flush()
        return order

    @staticmethod
    def get_by_id(session: Session, order_id: int) -> Optional["Order"]:
        return session.query(Order).filter(Order.id == order_id).first()
