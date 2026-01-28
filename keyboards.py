"""
Inline keyboard layouts for the Telegram bot
File: keyboards.py
"""

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


def get_subcategories_keyboard(subcategories, category_id: int) -> InlineKeyboardMarkup:
    """Create inline keyboard with subcategories"""
    buttons = []
    
    for subcat in subcategories:
        buttons.append([
            InlineKeyboardButton(
                text=f"📂 {subcat.name}",
                callback_data=f"subcategory_{subcat.id}"
            )
        ])
    
    # Add back button
    buttons.append([
        InlineKeyboardButton(
            text="⬅️ Back to Categories",
            callback_data="back_to_categories"
        )
    ])
    
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def get_products_keyboard(products, subcategory_id: int) -> InlineKeyboardMarkup:
    """Create inline keyboard with products"""
    buttons = []
    
    for product in products:
        buttons.append([
            InlineKeyboardButton(
                text=f"🛍️ {product.name}",
                callback_data=f"product_{product.id}"
            )
        ])
    
    # Add back button
    buttons.append([
        InlineKeyboardButton(
            text="⬅️ Back to Subcategories",
            callback_data=f"back_to_subcategories_{subcategory_id}"
        )
    ])
    
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def get_product_variants_keyboard(variants, product_id: int, num_images: int) -> InlineKeyboardMarkup:
    """Create inline keyboard with numbered image buttons and variant selection"""
    buttons = []
    
    # Add numbered buttons for images (if there are multiple images)
    if num_images > 1:
        image_buttons = []
        for i in range(num_images):
            image_buttons.append(
                InlineKeyboardButton(
                    text=f"{i + 1}",
                    callback_data=f"view_image_{product_id}_{i}"
                )
            )
        
        # Split into rows of 5 buttons each
        for i in range(0, len(image_buttons), 5):
            buttons.append(image_buttons[i:i+5])
    
    # Add separator
    if num_images > 1:
        buttons.append([
            InlineKeyboardButton(
                text="━━━━━ Select Variant ━━━━━",
                callback_data="separator"
            )
        ])
    
    # Add variant buttons
    for variant in variants:
        stock_text = f" ({variant.stock} left)" if variant.stock < 10 else ""
        buttons.append([
            InlineKeyboardButton(
                text=f"✨ {variant.variant_name} - ${variant.price:.2f}{stock_text}",
                callback_data=f"variant_{variant.id}"
            )
        ])
    
    # Add cart and back buttons
    buttons.append([
        InlineKeyboardButton(
            text="🛒 View Cart",
            callback_data="view_cart"
        )
    ])
    
    buttons.append([
        InlineKeyboardButton(
            text="⬅️ Back to Products",
            callback_data=f"back_to_products_{product_id}"
        )
    ])
    
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def get_variant_confirmation_keyboard(variant_id: int, product_id: int) -> InlineKeyboardMarkup:
    """Create keyboard for variant confirmation"""
    buttons = [
        [
            InlineKeyboardButton(
                text="➕ Add to Cart",
                callback_data=f"add_to_cart_{variant_id}"
            )
        ],
        [
            InlineKeyboardButton(
                text="🛒 View Cart",
                callback_data="view_cart"
            )
        ],
        [
            InlineKeyboardButton(
                text="⬅️ Back to Product",
                callback_data=f"product_{product_id}"
            )
        ]
    ]
    
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def get_cart_keyboard() -> InlineKeyboardMarkup:
    """Create inline keyboard for cart view"""
    buttons = [
        [
            InlineKeyboardButton(
                text="✅ Checkout",
                callback_data="checkout"
            )
        ],
        [
            InlineKeyboardButton(
                text="🛍️ Continue Shopping",
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
                text="✅ Confirm Order",
                callback_data=f"confirm_order_{order_id}"
            )
        ],
        [
            InlineKeyboardButton(
                text="❌ Cancel Order",
                callback_data=f"cancel_order_{order_id}"
            )
        ]
    ]
    
    return InlineKeyboardMarkup(inline_keyboard=buttons)