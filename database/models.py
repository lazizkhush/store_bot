from sqlalchemy import Column, Integer, String, Float, ForeignKey, DateTime, Boolean, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime

Base = declarative_base()


class User(Base):
    """User model for storing customer information"""
    __tablename__ = 'users'
    
    id = Column(Integer, primary_key=True)
    telegram_id = Column(Integer, unique=True, nullable=False, index=True)
    phone_number = Column(String(20), nullable=False)
    username = Column(String(100))
    first_name = Column(String(100))
    last_name = Column(String(100))
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    orders = relationship('Order', back_populates='user', cascade='all, delete-orphan')
    cart_items = relationship('CartItem', back_populates='user', cascade='all, delete-orphan')

    def __repr__(self):
        return f"<User {self.telegram_id} - {self.phone_number}>"


class Category(Base):
    """Category model for product organization"""
    __tablename__ = 'categories'
    
    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    description = Column(Text)
    is_active = Column(Boolean, default=True)
    order = Column(Integer, default=0)  # For custom ordering
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    products = relationship('Product', back_populates='category', cascade='all, delete-orphan')

    def __repr__(self):
        return f"<Category {self.name}>"


class Product(Base):
    """Product model"""
    __tablename__ = 'products'
    
    id = Column(Integer, primary_key=True)
    category_id = Column(Integer, ForeignKey('categories.id'), nullable=False)
    name = Column(String(200), nullable=False)
    description = Column(Text)
    is_active = Column(Boolean, default=True)
    order = Column(Integer, default=0)  # For custom ordering
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    category = relationship('Category', back_populates='products')
    variants = relationship('ProductVariant', back_populates='product', cascade='all, delete-orphan')

    def __repr__(self):
        return f"<Product {self.name}>"


class ProductVariant(Base):
    """Product variant model (e.g., different sizes, colors)"""
    __tablename__ = 'product_variants'
    
    id = Column(Integer, primary_key=True)
    product_id = Column(Integer, ForeignKey('products.id'), nullable=False)
    name = Column(String(200), nullable=False)
    description = Column(Text)
    price = Column(Float, nullable=False)
    image_file_id = Column(String(500))  # Telegram file_id for the image
    is_active = Column(Boolean, default=True)
    stock_quantity = Column(Integer, default=0)
    order = Column(Integer, default=0)  # For custom ordering
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    product = relationship('Product', back_populates='variants')
    cart_items = relationship('CartItem', back_populates='variant')
    order_items = relationship('OrderItem', back_populates='variant')

    def __repr__(self):
        return f"<Variant {self.name} - ${self.price}>"


class CartItem(Base):
    """Shopping cart items"""
    __tablename__ = 'cart_items'
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    variant_id = Column(Integer, ForeignKey('product_variants.id'), nullable=False)
    quantity = Column(Integer, default=1)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    user = relationship('User', back_populates='cart_items')
    variant = relationship('ProductVariant', back_populates='cart_items')

    def __repr__(self):
        return f"<CartItem User:{self.user_id} Variant:{self.variant_id} Qty:{self.quantity}>"


class Order(Base):
    """Order model"""
    __tablename__ = 'orders'
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    total_amount = Column(Float, nullable=False)
    note = Column(Text)
    location_latitude = Column(Float)
    location_longitude = Column(Float)
    location_address = Column(String(500))
    status = Column(String(50), default='pending')  # pending, confirmed, cancelled, delivered
    admin_message_id = Column(Integer)  # Message ID in admin chat
    channel_message_id = Column(Integer)  # Message ID in channel
    created_at = Column(DateTime, default=datetime.utcnow)
    confirmed_at = Column(DateTime)
    
    # Relationships
    user = relationship('User', back_populates='orders')
    items = relationship('OrderItem', back_populates='order', cascade='all, delete-orphan')

    def __repr__(self):
        return f"<Order #{self.id} - ${self.total_amount} - {self.status}>"


class OrderItem(Base):
    """Order items (products in an order)"""
    __tablename__ = 'order_items'
    
    id = Column(Integer, primary_key=True)
    order_id = Column(Integer, ForeignKey('orders.id'), nullable=False)
    variant_id = Column(Integer, ForeignKey('product_variants.id'), nullable=False)
    quantity = Column(Integer, nullable=False)
    price_at_purchase = Column(Float, nullable=False)  # Store price at time of order
    variant_name = Column(String(200))  # Store name in case variant is deleted
    product_name = Column(String(200))  # Store product name
    
    # Relationships
    order = relationship('Order', back_populates='items')
    variant = relationship('ProductVariant', back_populates='order_items')

    def __repr__(self):
        return f"<OrderItem {self.product_name} - {self.variant_name} x{self.quantity}>"
    