"""
Database models using SQLAlchemy ORM
File: database.py
"""

from datetime import datetime
from typing import Optional, List
from sqlalchemy import create_engine, String, Integer, Float, DateTime, ForeignKey, Text, BigInteger, Boolean
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship, Session, sessionmaker
from contextlib import contextmanager

from config import DATABASE_FILE

# Database URL - Change this single line to switch databases
# For SQLite (development):
DATABASE_URL = f"sqlite:///{DATABASE_FILE}"

# For PostgreSQL (production):
# DATABASE_URL = "postgresql://user:password@localhost/dbname"

# For MySQL (production):
# DATABASE_URL = "mysql+pymysql://user:password@localhost/dbname"

# Create engine
engine = create_engine(DATABASE_URL, echo=False)

# Create session factory
SessionLocal = sessionmaker(bind=engine, expire_on_commit=False)


class Base(DeclarativeBase):
    """Base class for all models"""
    pass


@contextmanager
def get_db():
    """Get database session"""
    session = SessionLocal()
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()


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
    def get_by_telegram_id(session: Session, telegram_id: int) -> Optional["User"]:
        """Get user by telegram ID"""
        return session.query(User).filter(User.telegram_id == telegram_id).first()
    
    @staticmethod
    def get_by_id(session: Session, user_id: int) -> Optional["User"]:
        """Get user by ID"""
        return session.query(User).filter(User.id == user_id).first()
    
    @staticmethod
    def create(session: Session, telegram_id: int, phone_number: str, first_name: str, 
               last_name: str = "", username: str = "") -> "User":
        """Create new user"""
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


class Category(Base):
    """Category model"""
    __tablename__ = "categories"
    
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100), unique=True)
    description: Mapped[Optional[str]] = mapped_column(Text)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    
    # Relationships
    subcategories: Mapped[List["Subcategory"]] = relationship(back_populates="category", cascade="all, delete-orphan")
    
    @staticmethod
    def get_all(session: Session) -> List["Category"]:
        """Get all active categories"""
        return session.query(Category).filter(Category.is_active == True).order_by(Category.name).all()
    
    @staticmethod
    def get_by_id(session: Session, category_id: int) -> Optional["Category"]:
        """Get category by ID"""
        return session.query(Category).filter(Category.id == category_id).first()
    
    @staticmethod
    def create(session: Session, name: str, description: str = "") -> "Category":
        """Create new category"""
        category = Category(name=name, description=description)
        session.add(category)
        session.flush()
        return category


class Subcategory(Base):
    """Subcategory model"""
    __tablename__ = "subcategories"
    
    id: Mapped[int] = mapped_column(primary_key=True)
    category_id: Mapped[int] = mapped_column(ForeignKey("categories.id"))
    name: Mapped[str] = mapped_column(String(100))
    description: Mapped[Optional[str]] = mapped_column(Text)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    
    # Relationships
    category: Mapped["Category"] = relationship(back_populates="subcategories")
    products: Mapped[List["Product"]] = relationship(back_populates="subcategory", cascade="all, delete-orphan")
    
    @staticmethod
    def get_by_category(session: Session, category_id: int) -> List["Subcategory"]:
        """Get all active subcategories in a category"""
        return session.query(Subcategory).filter(
            Subcategory.category_id == category_id,
            Subcategory.is_active == True
        ).order_by(Subcategory.name).all()
    
    @staticmethod
    def get_by_id(session: Session, subcategory_id: int) -> Optional["Subcategory"]:
        """Get subcategory by ID"""
        return session.query(Subcategory).filter(Subcategory.id == subcategory_id).first()
    
    @staticmethod
    def create(session: Session, category_id: int, name: str, description: str = "") -> "Subcategory":
        """Create new subcategory"""
        subcategory = Subcategory(category_id=category_id, name=name, description=description)
        session.add(subcategory)
        session.flush()
        return subcategory


class Product(Base):
    """Product model"""
    __tablename__ = "products"
    
    id: Mapped[int] = mapped_column(primary_key=True)
    subcategory_id: Mapped[int] = mapped_column(ForeignKey("subcategories.id"))
    name: Mapped[str] = mapped_column(String(200))
    description: Mapped[str] = mapped_column(Text)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    
    # Relationships
    subcategory: Mapped["Subcategory"] = relationship(back_populates="products")
    variants: Mapped[List["ProductVariant"]] = relationship(back_populates="product", cascade="all, delete-orphan")
    images: Mapped[List["ProductImage"]] = relationship(back_populates="product", cascade="all, delete-orphan")
    
    @staticmethod
    def get_by_subcategory(session: Session, subcategory_id: int) -> List["Product"]:
        """Get all active products in a subcategory"""
        return session.query(Product).filter(
            Product.subcategory_id == subcategory_id,
            Product.is_active == True
        ).order_by(Product.name).all()
    
    @staticmethod
    def get_by_id(session: Session, product_id: int) -> Optional["Product"]:
        """Get product by ID"""
        return session.query(Product).filter(Product.id == product_id).first()
    
    @staticmethod
    def create(session: Session, subcategory_id: int, name: str, description: str = "") -> "Product":
        """Create new product"""
        product = Product(subcategory_id=subcategory_id, name=name, description=description)
        session.add(product)
        session.flush()
        return product


class ProductVariant(Base):
    """Product variant model (sizes, colors, etc.)"""
    __tablename__ = "product_variants"
    
    id: Mapped[int] = mapped_column(primary_key=True)
    product_id: Mapped[int] = mapped_column(ForeignKey("products.id"))
    variant_name: Mapped[str] = mapped_column(String(100))
    price: Mapped[float] = mapped_column(Float)
    stock: Mapped[int] = mapped_column(Integer, default=0)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    
    # Relationships
    product: Mapped["Product"] = relationship(back_populates="variants")
    cart_items: Mapped[List["Cart"]] = relationship(back_populates="variant")
    order_items: Mapped[List["OrderItem"]] = relationship(back_populates="variant")
    
    @staticmethod
    def get_by_product(session: Session, product_id: int) -> List["ProductVariant"]:
        """Get all active variants for a product"""
        return session.query(ProductVariant).filter(
            ProductVariant.product_id == product_id,
            ProductVariant.is_active == True
        ).order_by(ProductVariant.id).all()
    
    @staticmethod
    def get_by_id(session: Session, variant_id: int) -> Optional["ProductVariant"]:
        """Get variant by ID"""
        return session.query(ProductVariant).filter(ProductVariant.id == variant_id).first()
    
    @staticmethod
    def create(session: Session, product_id: int, variant_name: str, price: float, stock: int = 0) -> "ProductVariant":
        """Create new product variant"""
        variant = ProductVariant(
            product_id=product_id,
            variant_name=variant_name,
            price=price,
            stock=stock
        )
        session.add(variant)
        session.flush()
        return variant


class ProductImage(Base):
    """Product image model"""
    __tablename__ = "product_images"
    
    id: Mapped[int] = mapped_column(primary_key=True)
    product_id: Mapped[int] = mapped_column(ForeignKey("products.id"))
    file_id: Mapped[str] = mapped_column(String(200))
    position: Mapped[int] = mapped_column(Integer, default=0)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    
    # Relationships
    product: Mapped["Product"] = relationship(back_populates="images")
    
    @staticmethod
    def get_by_product(session: Session, product_id: int) -> List["ProductImage"]:
        """Get all images for a product, ordered by position"""
        return session.query(ProductImage).filter(
            ProductImage.product_id == product_id
        ).order_by(ProductImage.position, ProductImage.id).all()
    
    @staticmethod
    def create(session: Session, product_id: int, file_id: str, position: int = 0) -> "ProductImage":
        """Create new product image"""
        image = ProductImage(product_id=product_id, file_id=file_id, position=position)
        session.add(image)
        session.flush()
        return image


class Cart(Base):
    """Shopping cart model"""
    __tablename__ = "cart"
    
    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    variant_id: Mapped[int] = mapped_column(ForeignKey("product_variants.id"))
    quantity: Mapped[int] = mapped_column(Integer, default=1)
    added_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    
    # Relationships
    user: Mapped["User"] = relationship(back_populates="cart_items")
    variant: Mapped["ProductVariant"] = relationship(back_populates="cart_items")
    
    @staticmethod
    def get_user_cart(session: Session, user_id: int) -> List["Cart"]:
        """Get user's cart with product and variant details"""
        return session.query(Cart).filter(Cart.user_id == user_id).all()
    
    @staticmethod
    def get_item(session: Session, user_id: int, variant_id: int) -> Optional["Cart"]:
        """Get specific cart item"""
        return session.query(Cart).filter(
            Cart.user_id == user_id,
            Cart.variant_id == variant_id
        ).first()
    
    @staticmethod
    def add_item(session: Session, user_id: int, variant_id: int, quantity: int = 1):
        """Add item to cart"""
        cart_item = Cart.get_item(session, user_id, variant_id)
        if cart_item:
            cart_item.quantity += quantity
        else:
            cart_item = Cart(user_id=user_id, variant_id=variant_id, quantity=quantity)
            session.add(cart_item)
        session.flush()
    
    @staticmethod
    def clear_cart(session: Session, user_id: int):
        """Clear user's cart"""
        session.query(Cart).filter(Cart.user_id == user_id).delete()


class Order(Base):
    """Order model"""
    __tablename__ = "orders"
    
    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    total_price: Mapped[float] = mapped_column(Float)
    status: Mapped[str] = mapped_column(String(20), default="pending")
    delivery_latitude: Mapped[float] = mapped_column(Float)
    delivery_longitude: Mapped[float] = mapped_column(Float)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    user: Mapped["User"] = relationship(back_populates="orders")
    items: Mapped[List["OrderItem"]] = relationship(back_populates="order", cascade="all, delete-orphan")
    
    @staticmethod
    def create(session: Session, user_id: int, total_price: float, latitude: float, longitude: float) -> "Order":
        """Create new order"""
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
        """Get order by ID"""
        return session.query(Order).filter(Order.id == order_id).first()


class OrderItem(Base):
    """Order items model"""
    __tablename__ = "order_items"
    
    id: Mapped[int] = mapped_column(primary_key=True)
    order_id: Mapped[int] = mapped_column(ForeignKey("orders.id"))
    variant_id: Mapped[int] = mapped_column(ForeignKey("product_variants.id"))
    quantity: Mapped[int] = mapped_column(Integer)
    price: Mapped[float] = mapped_column(Float)
    product_name: Mapped[str] = mapped_column(String(200))
    variant_name: Mapped[str] = mapped_column(String(100))
    
    # Relationships
    order: Mapped["Order"] = relationship(back_populates="items")
    variant: Mapped["ProductVariant"] = relationship(back_populates="order_items")
    
    @staticmethod
    def create(session: Session, order_id: int, variant_id: int, quantity: int, 
               price: float, product_name: str, variant_name: str) -> "OrderItem":
        """Create order item"""
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
        """Get all items in an order"""
        return session.query(OrderItem).filter(OrderItem.order_id == order_id).all()


def init_db():
    """Initialize database and create tables"""
    Base.metadata.create_all(engine)
    
    # Add sample data if database is empty
    with get_db() as session:
        if session.query(Category).count() == 0:
            add_sample_data(session)



def add_sample_data(session: Session):
    """Add sample categories, subcategories, products and variants"""
    # Create categories
    electronics = Category.create(session, "Electronics", "Electronic devices and gadgets")
    clothing = Category.create(session, "Clothing", "Fashion and apparel")
    food = Category.create(session, "Food & Beverages", "Food and drinks")

    # Create subcategories
    phones_subcat = Subcategory.create(session, electronics.id, "Smartphones", "Mobile phones")
    laptops_subcat = Subcategory.create(session, electronics.id, "Laptops", "Portable computers")

    mens_clothing = Subcategory.create(session, clothing.id, "Men's Clothing", "Clothing for men")
    womens_clothing = Subcategory.create(session, clothing.id, "Women's Clothing", "Clothing for women")

    pizza_subcat = Subcategory.create(session, food.id, "Pizza", "Various pizzas")
    drinks_subcat = Subcategory.create(session, food.id, "Beverages", "Drinks and beverages")

    # Create products
    iphone = Product.create(session, phones_subcat.id, "iPhone 15", "Latest iPhone model with advanced features")
    samsung = Product.create(session, phones_subcat.id, "Samsung Galaxy S24", "Premium Samsung smartphone")

    macbook = Product.create(session, laptops_subcat.id, "MacBook Pro", "Apple's professional laptop")
    dell = Product.create(session, laptops_subcat.id, "Dell XPS", "Premium Dell laptop")

    tshirt = Product.create(session, mens_clothing.id, "Cotton T-Shirt", "Comfortable cotton t-shirt")
    jeans = Product.create(session, mens_clothing.id, "Denim Jeans", "Classic blue jeans")

    # Create variants
    # iPhone variants (storage sizes)
    ProductVariant.create(session, iphone.id, "128GB", 999.99, 10)
    ProductVariant.create(session, iphone.id, "256GB", 1099.99, 8)
    ProductVariant.create(session, iphone.id, "512GB", 1299.99, 5)

    # Samsung variants
    ProductVariant.create(session, samsung.id, "256GB", 899.99, 12)
    ProductVariant.create(session, samsung.id, "512GB", 999.99, 7)

    # MacBook variants
    ProductVariant.create(session, macbook.id, "13-inch M3", 1599.99, 5)
    ProductVariant.create(session, macbook.id, "14-inch M3 Pro", 1999.99, 3)
    ProductVariant.create(session, macbook.id, "16-inch M3 Max", 2499.99, 2)

    # T-Shirt variants (sizes)
    ProductVariant.create(session, tshirt.id, "Small", 19.99, 50)
    ProductVariant.create(session, tshirt.id, "Medium", 19.99, 50)
    ProductVariant.create(session, tshirt.id, "Large", 19.99, 50)
    ProductVariant.create(session, tshirt.id, "X-Large", 19.99, 30)

    # Jeans variants (sizes)
    ProductVariant.create(session, jeans.id, "30x32", 49.99, 20)
    ProductVariant.create(session, jeans.id, "32x32", 49.99, 25)
    ProductVariant.create(session, jeans.id, "34x32", 49.99, 20)
    ProductVariant.create(session, jeans.id, "36x34", 49.99, 15)

    print("Sample data with subcategories and variants added successfully!")


