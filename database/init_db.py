"""
Database initialization and session management
"""

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from contextlib import contextmanager
from config import DATABASE_FILE

DATABASE_URL = f"sqlite:///{DATABASE_FILE}"
engine = create_engine(DATABASE_URL, echo=False)
SessionLocal = sessionmaker(bind=engine, expire_on_commit=False)

@contextmanager
def get_db():
    session = SessionLocal()
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()

def init_db():
    # Import models so that metadata is available
    from database.models import user, category, product, product_variant, product_image, cart, order, order_item
    user.Base.metadata.create_all(engine)
    # Add sample data if database is empty
    with get_db() as session:
        from database.models.category import Category
        if session.query(Category).count() == 0:
            add_sample_data(session)

def add_sample_data(session: Session):
    """Add sample categories, products and variants (no subcategories)"""
    from database.models.category import Category
    from database.models.product import Product
    from database.models.product_variant import ProductVariant
    electronics = Category.create(session, "Electronics", "Electronic devices and gadgets")
    clothing = Category.create(session, "Clothing", "Fashion and apparel")
    food = Category.create(session, "Food & Beverages", "Food and drinks")

    # Create products directly under categories
    iphone = Product.create(session, electronics.id, "iPhone 15", "Latest iPhone model with advanced features")
    samsung = Product.create(session, electronics.id, "Samsung Galaxy S24", "Premium Samsung smartphone")
    macbook = Product.create(session, electronics.id, "MacBook Pro", "Apple's professional laptop")
    dell = Product.create(session, electronics.id, "Dell XPS", "Premium Dell laptop")

    tshirt = Product.create(session, clothing.id, "Cotton T-Shirt", "Comfortable cotton t-shirt")
    jeans = Product.create(session, clothing.id, "Denim Jeans", "Classic blue jeans")

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

    print("Sample data with categories and variants added successfully!")
