"""
Cart model and logic
"""
from datetime import datetime
from typing import List, Optional
from sqlalchemy import Integer, DateTime, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship, Session
from .base import Base


class Cart(Base):
    __tablename__ = "cart"
    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    variant_id: Mapped[int] = mapped_column(ForeignKey("product_variants.id"))
    quantity: Mapped[int] = mapped_column(Integer, default=1)
    added_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    user: Mapped["User"] = relationship(back_populates="cart_items")
    variant: Mapped["ProductVariant"] = relationship(back_populates="cart_items")

    @staticmethod
    def get_user_cart(session: Session, user_id: int) -> List["Cart"]:
        return session.query(Cart).filter(Cart.user_id == user_id).all()

    @staticmethod
    def get_item(session: Session, user_id: int, variant_id: int) -> Optional["Cart"]:
        return session.query(Cart).filter(
            Cart.user_id == user_id,
            Cart.variant_id == variant_id
        ).first()

    @staticmethod
    def add_item(session: Session, user_id: int, variant_id: int, quantity: int = 1):
        cart_item = Cart.get_item(session, user_id, variant_id)
        if cart_item:
            cart_item.quantity += quantity
        else:
            cart_item = Cart(user_id=user_id, variant_id=variant_id, quantity=quantity)
            session.add(cart_item)
        session.flush()

    @staticmethod
    def clear_cart(session: Session, user_id: int):
        session.query(Cart).filter(Cart.user_id == user_id).delete()
