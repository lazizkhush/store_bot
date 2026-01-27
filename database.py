"""
Database models and configuration using SQLAlchemy
File: database.py
"""

from datetime import datetime
from contextlib import asynccontextmanager
from typing import Optional, List

from sqlalchemy import String, Integer, Float, DateTime, ForeignKey, Text, BigInteger, Boolean
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship, selectinload
from sqlalchemy import select

# Database URL - Change this single line to switch databases
# For SQLite (development):
DATABASE_URL = "sqlite+aiosqlite:///store.db"

# For PostgreSQL (production):
# DATABASE_URL = "postgresql+asyncpg://user:password@localhost/dbname"

# For MySQL (production):
# DATABASE_URL = "mysql+aiomysql://user:password@localhost/dbname"

# Create async engine
engine = create_async_engine(DATABASE_URL, echo=False)

# Create session factory
async_session_maker = async_sessionmaker(
    engine, class_=AsyncSession, expire_on_commit=False
)


class Base(DeclarativeBase):
    """Base class for all models"""
    pass


class User(Base):
    """User model"""
    __tablename__ = "users"
    
    id: Mapped[int] = mapped_column(primary_key=True)
    telegram_id: Mapped[int] = mapped_column(BigInteger, unique=True, index=True)
    phone_number: Mapped[Optional[str]] = mapped_column(String(20))
    first_name: Mapped[str] = mapped_column(String(100))
    last_name: Mapped[Optional[str]] = mapped_column(String(100))
    username: Mapped[Optional[str]] = mapped_column(String(100))
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    
    # Relationships
    orders: Mapped[List["Order"]] = relationship(back_populates="user", cascade="all, delete-orphan")
    cart_items: Mapped[List["Cart"]] = relationship(back_populates="user", cascade="all, delete-orphan")
    
    @staticmethod
    async def get_by_telegram_id(session: AsyncSession, telegram_id: int) -> Optional["User"]:
        """Get user by telegram ID"""
        result = await session.execute(
            select(User).where(User.telegram_id == telegram_id)
        )
        return result.scalar_one_or_none()
    
    @staticmethod
    async def get_by_id(session: AsyncSession, user_id: int) -> Optional["User"]:
        """Get user by ID"""
        result = await session.execute(
            select(User).where(User.id == user_id)
        )
        return result.scalar_one_or_none()


class Category(Base):
    """Product category model"""
    __tablename__ = "categories"
    
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100), unique=True)
    description: Mapped[Optional[str]] = mapped_column(Text)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    
    # Relationships
    products: Mapped[List["Product"]] = relationship(back_populates="category", cascade="all, delete-orphan")
    
    @staticmethod
    async def get_all(session: AsyncSession) -> List["Category"]:
        """Get all active categories"""
        result = await session.execute(
            select(Category)
            .where(Category.is_active == True)
            .order_by(Category.name)
        )
        return list(result.scalars().all())
    
    @staticmethod
    async def get_by_id(session: AsyncSession, category_id: int) -> Optional["Category"]:
        """Get category by ID"""
        result = await session.execute(
            select(Category).where(Category.id == category_id)
        )
        return result.scalar_one_or_none()


class Product(Base):
    """Product model"""
    __tablename__ = "products"
    
    id: Mapped[int] = mapped_column(primary_key=True)
    category_id: Mapped[int] = mapped_column(ForeignKey("categories.id"))
    name: Mapped[str] = mapped_column(String(200))
    description: Mapped[str] = mapped_column(Text)
    price: Mapped[float] = mapped_column(Float)
    stock: Mapped[int] = mapped_column(Integer, default=0)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    
    # Relationships
    category: Mapped["Category"] = relationship(back_populates="products")
    order_items: Mapped[List["OrderItem"]] = relationship(back_populates="product")
    cart_items: Mapped[List["Cart"]] = relationship(back_populates="product")
    
    @staticmethod
    async def get_by_category(session: AsyncSession, category_id: int) -> List["Product"]:
        """Get all active products in a category"""
        result = await session.execute(
            select(Product)
            .where(Product.category_id == category_id, Product.is_active == True)
            .order_by(Product.name)
        )
        return list(result.scalars().all())
    
    @staticmethod
    async def get_by_id(session: AsyncSession, product_id: int) -> Optional["Product"]:
        """Get product by ID"""
        result = await session.execute(
            select(Product).where(Product.id == product_id)
        )
        return result.scalar_one_or_none()


class Order(Base):
    """Order model"""
    __tablename__ = "orders"
    
    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    total_price: Mapped[float] = mapped_column(Float)
    status: Mapped[str] = mapped_column(String(20), default="pending")  # pending, confirmed, cancelled, delivered
    delivery_latitude: Mapped[float] = mapped_column(Float)
    delivery_longitude: Mapped[float] = mapped_column(Float)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    user: Mapped["User"] = relationship(back_populates="orders")
    items: Mapped[List["OrderItem"]] = relationship(back_populates="order", cascade="all, delete-orphan")
    
    @staticmethod
    async def get_by_id(session: AsyncSession, order_id: int) -> Optional["Order"]:
        """Get order by ID with user relationship loaded"""
        result = await session.execute(
            select(Order)
            .options(selectinload(Order.user))
            .where(Order.id == order_id)
        )
        return result.scalar_one_or_none()
    
    @staticmethod
    async def get_user_orders(session: AsyncSession, user_id: int) -> List["Order"]:
        """Get all orders for a user"""
        result = await session.execute(
            select(Order)
            .where(Order.user_id == user_id)
            .order_by(Order.created_at.desc())
        )
        return list(result.scalars().all())


class OrderItem(Base):
    """Order item model"""
    __tablename__ = "order_items"
    
    id: Mapped[int] = mapped_column(primary_key=True)
    order_id: Mapped[int] = mapped_column(ForeignKey("orders.id"))
    product_id: Mapped[int] = mapped_column(ForeignKey("products.id"))
    quantity: Mapped[int] = mapped_column(Integer)
    price: Mapped[float] = mapped_column(Float)  # Price at time of order
    
    # Relationships
    order: Mapped["Order"] = relationship(back_populates="items")
    product: Mapped["Product"] = relationship(back_populates="order_items")
    
    @staticmethod
    async def get_by_order(session: AsyncSession, order_id: int) -> List["OrderItem"]:
        """Get all items in an order"""
        result = await session.execute(
            select(OrderItem)
            .options(selectinload(OrderItem.product))
            .where(OrderItem.order_id == order_id)
        )
        return list(result.scalars().all())


class Cart(Base):
    """Shopping cart model"""
    __tablename__ = "cart"
    
    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    product_id: Mapped[int] = mapped_column(ForeignKey("products.id"))
    quantity: Mapped[int] = mapped_column(Integer, default=1)
    added_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    
    # Relationships
    user: Mapped["User"] = relationship(back_populates="cart_items")
    product: Mapped["Product"] = relationship(back_populates="cart_items")
    
    @staticmethod
    async def get_user_cart(session: AsyncSession, user_id: int) -> List["Cart"]:
        """Get all items in user's cart"""
        result = await session.execute(
            select(Cart)
            .options(selectinload(Cart.product))
            .where(Cart.user_id == user_id)
        )
        return list(result.scalars().all())
    
    @staticmethod
    async def get_item(session: AsyncSession, user_id: int, product_id: int) -> Optional["Cart"]:
        """Get specific cart item"""
        result = await session.execute(
            select(Cart)
            .where(Cart.user_id == user_id, Cart.product_id == product_id)
        )
        return result.scalar_one_or_none()
    
    @staticmethod
    async def clear_cart(session: AsyncSession, user_id: int):
        """Clear user's cart"""
        result = await session.execute(
            select(Cart).where(Cart.user_id == user_id)
        )
        items = result.scalars().all()
        for item in items:
            await session.delete(item)


@asynccontextmanager
async def get_session():
    """Get database session"""
    async with async_session_maker() as session:
        try:
            yield session
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


async def init_db():
    """Initialize database and create tables"""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    # Add sample data if database is empty
    async with async_session_maker() as session:
        result = await session.execute(select(Category))
        if not result.first():
            await add_sample_data(session)


async def add_sample_data(session: AsyncSession):
    """Add sample categories and products"""
    # Categories
    electronics = Category(name="Electronics", description="Electronic devices and gadgets")
    clothing = Category(name="Clothing", description="Fashion and apparel")
    food = Category(name="Food & Beverages", description="Food and drinks")
    
    session.add_all([electronics, clothing, food])
    await session.flush()
    
    # Products
    products = [
        Product(category_id=electronics.id, name="Smartphone", description="Latest model smartphone with great features", price=599.99, stock=10),
        Product(category_id=electronics.id, name="Laptop", description="High-performance laptop for work and gaming", price=1299.99, stock=5),
        Product(category_id=electronics.id, name="Headphones", description="Wireless noise-cancelling headphones", price=199.99, stock=15),
        
        Product(category_id=clothing.id, name="T-Shirt", description="Comfortable cotton t-shirt", price=19.99, stock=50),
        Product(category_id=clothing.id, name="Jeans", description="Classic blue jeans", price=49.99, stock=30),
        Product(category_id=clothing.id, name="Sneakers", description="Comfortable running sneakers", price=79.99, stock=20),
        
        Product(category_id=food.id, name="Pizza", description="Large pepperoni pizza", price=12.99, stock=100),
        Product(category_id=food.id, name="Burger", description="Delicious cheeseburger", price=8.99, stock=100),
        Product(category_id=food.id, name="Coffee", description="Premium coffee blend", price=4.99, stock=200),
    ]
    
    session.add_all(products)
    await session.commit()
    print("Sample data added successfully!")