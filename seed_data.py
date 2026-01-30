"""
Script to populate database with sample data for testing
"""
from database import init_db, get_session
from database.models import Category, Product, ProductVariant

def seed_database():
    """Add sample categories, products, and variants"""
    
    # Initialize database
    init_db()
    
    session = get_session()
    
    try:
        # Check if data already exists
        existing = session.query(Category).first()
        if existing:
            print("Database already has data. Skipping seed.")
            return
        
        # Create categories
        electronics = Category(
            name="Electronics",
            description="Electronic devices and gadgets",
            is_active=True,
            order=1
        )
        
        clothing = Category(
            name="Clothing",
            description="Fashion and apparel",
            is_active=True,
            order=2
        )
        
        food = Category(
            name="Food & Beverages",
            description="Food items and drinks",
            is_active=True,
            order=3
        )
        
        session.add_all([electronics, clothing, food])
        session.flush()
        
        # Create products for Electronics
        smartphone = Product(
            category_id=electronics.id,
            name="Smartphone X",
            description="Latest flagship smartphone",
            is_active=True,
            order=1
        )
        
        laptop = Product(
            category_id=electronics.id,
            name="Laptop Pro",
            description="High-performance laptop",
            is_active=True,
            order=2
        )
        
        # Create products for Clothing
        tshirt = Product(
            category_id=clothing.id,
            name="Cotton T-Shirt",
            description="Comfortable cotton t-shirt",
            is_active=True,
            order=1
        )
        
        jeans = Product(
            category_id=clothing.id,
            name="Denim Jeans",
            description="Classic denim jeans",
            is_active=True,
            order=2
        )
        
        # Create products for Food
        pizza = Product(
            category_id=food.id,
            name="Pizza",
            description="Delicious pizza",
            is_active=True,
            order=1
        )
        
        session.add_all([smartphone, laptop, tshirt, jeans, pizza])
        session.flush()
        
        # Create variants for Smartphone
        phone_variants = [
            ProductVariant(
                product_id=smartphone.id,
                name="128GB Black",
                description="128GB storage, Black color",
                price=699.99,
                is_active=True,
                stock_quantity=50,
                order=1
            ),
            ProductVariant(
                product_id=smartphone.id,
                name="256GB White",
                description="256GB storage, White color",
                price=799.99,
                is_active=True,
                stock_quantity=30,
                order=2
            ),
            ProductVariant(
                product_id=smartphone.id,
                name="512GB Blue",
                description="512GB storage, Blue color",
                price=999.99,
                is_active=True,
                stock_quantity=20,
                order=3
            )
        ]
        
        # Create variants for Laptop
        laptop_variants = [
            ProductVariant(
                product_id=laptop.id,
                name="13-inch i5",
                description="13-inch, Intel Core i5, 8GB RAM",
                price=1299.99,
                is_active=True,
                stock_quantity=25,
                order=1
            ),
            ProductVariant(
                product_id=laptop.id,
                name="15-inch i7",
                description="15-inch, Intel Core i7, 16GB RAM",
                price=1799.99,
                is_active=True,
                stock_quantity=15,
                order=2
            )
        ]
        
        # Create variants for T-Shirt
        tshirt_variants = [
            ProductVariant(
                product_id=tshirt.id,
                name="Small - Red",
                description="Size: Small, Color: Red",
                price=19.99,
                is_active=True,
                stock_quantity=100,
                order=1
            ),
            ProductVariant(
                product_id=tshirt.id,
                name="Medium - Blue",
                description="Size: Medium, Color: Blue",
                price=19.99,
                is_active=True,
                stock_quantity=100,
                order=2
            ),
            ProductVariant(
                product_id=tshirt.id,
                name="Large - Green",
                description="Size: Large, Color: Green",
                price=19.99,
                is_active=True,
                stock_quantity=80,
                order=3
            )
        ]
        
        # Create variants for Jeans
        jeans_variants = [
            ProductVariant(
                product_id=jeans.id,
                name="Size 30",
                description="Waist size: 30 inches",
                price=49.99,
                is_active=True,
                stock_quantity=60,
                order=1
            ),
            ProductVariant(
                product_id=jeans.id,
                name="Size 32",
                description="Waist size: 32 inches",
                price=49.99,
                is_active=True,
                stock_quantity=70,
                order=2
            ),
            ProductVariant(
                product_id=jeans.id,
                name="Size 34",
                description="Waist size: 34 inches",
                price=49.99,
                is_active=True,
                stock_quantity=50,
                order=3
            )
        ]
        
        # Create variants for Pizza
        pizza_variants = [
            ProductVariant(
                product_id=pizza.id,
                name="Margherita - Small",
                description="Classic Margherita, 10 inch",
                price=9.99,
                is_active=True,
                stock_quantity=999,
                order=1
            ),
            ProductVariant(
                product_id=pizza.id,
                name="Margherita - Large",
                description="Classic Margherita, 14 inch",
                price=14.99,
                is_active=True,
                stock_quantity=999,
                order=2
            ),
            ProductVariant(
                product_id=pizza.id,
                name="Pepperoni - Large",
                description="Pepperoni pizza, 14 inch",
                price=16.99,
                is_active=True,
                stock_quantity=999,
                order=3
            )
        ]
        
        # Add all variants
        all_variants = phone_variants + laptop_variants + tshirt_variants + jeans_variants + pizza_variants
        session.add_all(all_variants)
        
        # Commit all changes
        session.commit()
        
        print("✅ Database seeded successfully!")
        print(f"   - {len([electronics, clothing, food])} categories")
        print(f"   - {len([smartphone, laptop, tshirt, jeans, pizza])} products")
        print(f"   - {len(all_variants)} variants")
        
    except Exception as e:
        session.rollback()
        print(f"❌ Error seeding database: {e}")
    finally:
        session.close()


if __name__ == "__main__":
    seed_database()