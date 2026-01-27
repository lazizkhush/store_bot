"""
Inline keyboard layouts for the Telegram bot
File: keyboards.py
"""
from database import Product, get_session

from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from typing import List


def get_categories_keyboard(categories) -> InlineKeyboardMarkup:
    """Create inline keyboard with categories"""
    buttons = []
    
    for category in categories:
        buttons.append([
            InlineKeyboardButton(
                text=f"📁 {category.name}",
                callback_data=f"category_{category.id}"
            )
        ])
    
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def get_products_keyboard(products, category_id: int) -> InlineKeyboardMarkup:
    """Create inline keyboard with products"""
    buttons = []
    
    for product in products:
        stock_text = f" ({product.stock} ta qoldi)" if product.stock < 10 else ""
        buttons.append([
            InlineKeyboardButton(
                text=f"🛍️ {product.name} - ${product.price:.2f}{stock_text}",
                callback_data=f"product_{product.id}"
            )
        ])
    
    # Add back button
    buttons.append([
        InlineKeyboardButton(
            text="⬅️ Bo'limlarga qaytish",
            callback_data="back_to_categories"
        )
    ])
    
    return InlineKeyboardMarkup(inline_keyboard=buttons)


async def get_product_keyboard(product_id: int) -> InlineKeyboardMarkup:
    """Create inline keyboard for a single product"""
    # Get category_id from the product (you might need to pass this)
    async with get_session() as session:
        product = await Product.get_by_id(session, product_id)
    buttons = [
        [
            InlineKeyboardButton(
                text="➕ Savatga qo'shish",
                callback_data=f"add_to_cart_{product_id}"
            )
        ],
        [
            InlineKeyboardButton(
                text="🛒 Savatni ko'rish",
                callback_data="view_cart"
            )
        ],
        [
            InlineKeyboardButton(
                text="⬅️ Mahsulotlarga qaytish",
                callback_data=f"back_to_products_{product.category_id}"  # Will be updated dynamically
            )
        ]
    ]
    
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def get_cart_keyboard() -> InlineKeyboardMarkup:
    """Create inline keyboard for cart view"""
    buttons = [
        [
            InlineKeyboardButton(
                text="✅ Tekshirish",
                callback_data="checkout"
            )
        ],
        [
            InlineKeyboardButton(
                text="🛍️ Sotib olishni davom ettirish",
                callback_data="back_to_categories"
            )
        ]
    ]
    
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def get_admin_order_keyboard(order_id: int) -> InlineKeyboardMarkup:
    """Create inline keyboard for admin order actions"""
    buttons = [
        [
            InlineKeyboardButton(
                text="✅ Tasdiqlash",
                callback_data=f"confirm_order_{order_id}"
            )
        ],
        [
            InlineKeyboardButton(
                text="❌ Bekor qilish",
                callback_data=f"cancel_order_{order_id}"
            )
        ]
    ]
    
    return InlineKeyboardMarkup(inline_keyboard=buttons)



# from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
# from db.session import Session
# from db.models import Category, Product


# def categories_keyboard():
#     session = Session()
#     categories = session.query(Category).all()
#     session.close()

#     kb = []
#     for category in categories:
#         kb.append([InlineKeyboardButton(text=f"{category.name}", callback_data=f"cat_{category.id}")])

#     kb.append([InlineKeyboardButton(text="Savatni ko'rish", callback_data="see_cart")])
#     return InlineKeyboardMarkup(inline_keyboard=kb)

# def products_keyboard(category_id):
#     session = Session()
#     products = session.query(Product).filter(Product.category_id == category_id).all()
#     session.close()

#     kb = []
#     for item in products:
#         kb.append([InlineKeyboardButton(text=f"{item.name}", callback_data=f"prod_{item.id}")])
        
#     kb.append([InlineKeyboardButton(text="🔙 Back", callback_data="back_to_categories")])
#     return InlineKeyboardMarkup(inline_keyboard=kb)


# def order_confirmation_kb():
#     return InlineKeyboardMarkup(
#             inline_keyboard=[
#                 [
#                     InlineKeyboardButton(text="Tasdiqlash ✅", callback_data=f"send_order")
#                 ],
#                 [
#                     InlineKeyboardButton(text="Bekor qilish ❌", callback_data="cancel"),
#                     InlineKeyboardButton(text="🔙 Back", callback_data="back_to_categories")
#                 ]
#             ]
#         )

# def add_to_cart_kb():
#     return InlineKeyboardMarkup(
#         inline_keyboard=[
#             [
#                 InlineKeyboardButton(text="➕", callback_data=f"addtocart_{category}_{product_id}")
#             ],
#             [
#                 InlineKeyboardButton(text="🔙 Back", callback_data=f"back_to_products_{category}")
#             ]
#         ]
#     )