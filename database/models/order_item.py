"""
OrderItem model and logic
"""
from sqlalchemy import Integer, Float, String, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship, Session
from .base import Base
from typing import List
## Removed direct import to avoid circular import
from .product_variant import ProductVariant

class OrderItem(Base):
    __tablename__ = "order_items"
    id: Mapped[int] = mapped_column(primary_key=True)
    order_id: Mapped[int] = mapped_column(ForeignKey("orders.id"))
    variant_id: Mapped[int] = mapped_column(ForeignKey("product_variants.id"))
    quantity: Mapped[int] = mapped_column(Integer)
    price: Mapped[float] = mapped_column(Float)
    product_name: Mapped[str] = mapped_column(String(200))
    variant_name: Mapped[str] = mapped_column(String(100))
    order: Mapped["Order"] = relationship(back_populates="items")
    variant: Mapped["ProductVariant"] = relationship(back_populates="order_items")

    @staticmethod
    def create(session: Session, order_id: int, variant_id: int, quantity: int, price: float, product_name: str, variant_name: str) -> "OrderItem":
        item = OrderItem(
            order_id=order_id,
            variant_id=variant_id,
            quantity=quantity,
            price=price,
            product_name=product_name,
            variant_name=variant_name
        )
        session.add(item)
        session.flush()
        return item

    @staticmethod
    def get_by_order(session: Session, order_id: int) -> List["OrderItem"]:
        return session.query(OrderItem).filter(OrderItem.order_id == order_id).all()
