"""
ProductImage model and logic
"""
from datetime import datetime
from typing import List
from sqlalchemy import String, Integer, DateTime, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship, Session
from .base import Base

class ProductImage(Base):
    __tablename__ = "product_images"
    id: Mapped[int] = mapped_column(primary_key=True)
    product_id: Mapped[int] = mapped_column(ForeignKey("products.id"))
    file_id: Mapped[str] = mapped_column(String(200))
    position: Mapped[int] = mapped_column(Integer, default=0)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    product: Mapped["Product"] = relationship(back_populates="images")

    @staticmethod
    def get_by_product(session: Session, product_id: int) -> List["ProductImage"]:
        return session.query(ProductImage).filter(
            ProductImage.product_id == product_id
        ).order_by(ProductImage.position, ProductImage.id).all()

    @staticmethod
    def create(session: Session, product_id: int, file_id: str, position: int = 0) -> "ProductImage":
        image = ProductImage(product_id=product_id, file_id=file_id, position=position)
        session.add(image)
        session.flush()
        return image
