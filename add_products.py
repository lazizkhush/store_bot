"""
Admin tool to add products and images to the database
File: add_products.py

This script helps admins add products with images to the store.
Run this script to add your products interactively.
"""

from database import (Category, Product, ProductVariant, 
                      ProductImage, init_db, get_db)


def list_categories():
    """List all categories"""
    with get_db() as session:
        categories = Category.get_all(session)
        print("\n=== Categories ===")
        for cat in categories:
            print(f"{cat.id}. {cat.name}")
        return categories





def add_category():
    """Add a new category"""
    print("\n=== Add Category ===")
    name = input("Category name: ")
    description = input("Description: ")
    
    with get_db() as session:
        category = Category.create(session, name, description)
        print(f"✅ Category created with ID: {category.id}")
        return category.id





def add_product():
    """Add a new product with variants"""
    list_categories()
    category_id = int(input("\nSelect category ID: "))
    
    print("\n=== Add Product ===")
    name = input("Product name: ")
    description = input("Description: ")
    
    with get_db() as session:
        product = Product.create(session, category_id, name, description)
        print(f"✅ Product created with ID: {product.id}")
        
        # Add variants
        print("\n=== Add Product Variants ===")
        print("Enter variants (e.g., sizes, colors, storage). Type 'done' when finished.")
        
        while True:
            variant_name = input("\nVariant name (or 'done'): ")
            if variant_name.lower() == 'done':
                break
            
            price = float(input("Price: "))
            stock = int(input("Stock quantity: "))
            
            variant = ProductVariant.create(session, product.id, variant_name, price, stock)
            print(f"✅ Variant '{variant_name}' added (ID: {variant.id})")
        
        return product.id


def add_images_to_product():
    """Add images to an existing product
    
    Note: You need to get file_id from Telegram first.
    Steps:
    1. Send the image to your bot in Telegram
    2. Bot will receive the photo and you can get file_id from the update
    3. Use that file_id here
    
    Or you can upload images through the bot by creating an admin command.
    """
    product_id = int(input("\nEnter product ID: "))
    
    print("\n=== Add Product Images ===")
    print("You need Telegram file_id for each image.")
    print("Tip: Send images to your bot and extract file_id from the update.")
    print("Type 'done' when finished.")
    
    position = 0
    with get_db() as session:
        while True:
            file_id = input(f"\nImage {position + 1} file_id (or 'done'): ")
            if file_id.lower() == 'done':
                break
            
            image = ProductImage.create(session, product_id, file_id, position)
            print(f"✅ Image added at position {position} (ID: {image.id})")
            position += 1


def main_menu():
    """Main menu for admin tools"""
    init_db()
    
    while True:
        print("\n" + "="*50)
        print("STORE ADMIN TOOLS")
        print("="*50)
        print("1. Add Category")
        print("2. Add Subcategory")
        print("3. Add Product (with variants)")
        print("4. Add Images to Product")
        print("5. List all categories")
        print("6. Exit")
        
        choice = input("\nSelect option: ")
        
        if choice == "1":
            add_category()
        elif choice == "2":
            add_subcategory()
        elif choice == "3":
            add_product()
        elif choice == "4":
            add_images_to_product()
        elif choice == "5":
            list_categories()
        elif choice == "6":
            print("Goodbye!")
            break
        else:
            print("Invalid option")


# ============================================
# EXAMPLE: How to get file_id from Telegram
# ============================================

"""
To get file_id for images, you can add this handler to your bot temporarily:

from aiogram import Router, F
from aiogram.types import Message

admin_router = Router()

@admin_router.message(F.photo)
async def get_photo_id(message: Message):
    # This will show you the file_id when you send a photo
    file_id = message.photo[-1].file_id  # Get largest photo
    await message.answer(f"File ID: `{file_id}`", parse_mode="Markdown")
    print(f"Photo file_id: {file_id}")

# Then in main.py, add:
# dp.include_router(admin_router)

# After sending photos to the bot, copy the file_id and use it in add_images_to_product()
"""


# ============================================
# QUICK START EXAMPLE
# ============================================

def quick_example():
    """
    Quick example of adding a complete product programmatically
    """
    init_db()
    
    with get_db() as session:
        # Assuming you already have categories and subcategories from sample data
        # Let's add a new product to the Smartphones subcategory (ID: 1)
        
        # Create product
        product = Product.create(
            session,
            subcategory_id=1,  # Smartphones
            name="Google Pixel 8",
            description="Latest Google Pixel with AI features"
        )
        
        # Add variants
        variants_data = [
            ("128GB - Black", 699.99, 15),
            ("256GB - Black", 799.99, 10),
            ("256GB - White", 799.99, 8),
        ]
        
        for variant_name, price, stock in variants_data:
            ProductVariant.create(session, product.id, variant_name, price, stock)
        
        print(f"✅ Product 'Google Pixel 8' created with ID: {product.id}")
        print("✅ 3 variants added")
        print("\nTo add images, send photos to your bot and get their file_ids,")
        print("then use add_images_to_product() or ProductImage.create()")


if __name__ == "__main__":
    # Uncomment to run interactive menu
    main_menu()
    
    # Or uncomment to run quick example
    # quick_example()