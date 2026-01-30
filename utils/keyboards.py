from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder


def get_main_menu_keyboard():
    """Main menu keyboard"""
    keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="🛍 Browse Categories")],
            [KeyboardButton(text="🛒 View Cart"), KeyboardButton(text="📦 My Orders")]
        ],
        resize_keyboard=True
    )
    return keyboard


def get_categories_keyboard(categories):
    """Inline keyboard with categories"""
    builder = InlineKeyboardBuilder()
    
    for category in categories:
        builder.button(
            text=f"📁 {category.name}",
            callback_data=f"cat_{category.id}"
        )
    
    builder.adjust(2)  # 2 buttons per row
    return builder.as_markup()


def get_products_keyboard(products, category_id):
    """Inline keyboard with products"""
    builder = InlineKeyboardBuilder()
    
    for product in products:
        builder.button(
            text=f"📦 {product.name}",
            callback_data=f"prod_{product.id}"
        )
    
    builder.button(
        text="⬅️ Back to Categories",
        callback_data="back_categories"
    )
    
    builder.adjust(1)  # 1 button per row
    return builder.as_markup()


def get_variants_keyboard(variants, product_id):
    """Inline keyboard with variant buttons"""
    builder = InlineKeyboardBuilder()
    
    # Add variant buttons
    for idx, variant in enumerate(variants, 1):
        builder.button(
            text=f"➕ Add Variant {idx}",
            callback_data=f"addvar_{variant.id}"
        )
    
    # Back button
    builder.button(
        text="⬅️ Back to Products",
        callback_data=f"backprod_{product_id}"
    )
    
    # Adjust layout: all variant buttons in one row if <= 4, otherwise wrap
    if len(variants) <= 4:
        builder.adjust(len(variants), 1)
    else:
        builder.adjust(2, 1)
    
    return builder.as_markup()


def get_cart_keyboard(has_items=False):
    """Inline keyboard for cart actions"""
    builder = InlineKeyboardBuilder()
    
    if has_items:
        builder.button(
            text="✅ Confirm Order",
            callback_data="checkout_confirm"
        )
        builder.button(
            text="🗑 Clear Cart",
            callback_data="cart_clear"
        )
        builder.adjust(1)
    
    builder.button(
        text="⬅️ Continue Shopping",
        callback_data="back_categories"
    )
    
    builder.adjust(1)
    return builder.as_markup()


def get_note_keyboard():
    """Keyboard for adding note"""
    builder = InlineKeyboardBuilder()
    
    builder.button(
        text="✍️ Yes, add note",
        callback_data="note_yes"
    )
    builder.button(
        text="⏭ No, skip",
        callback_data="note_no"
    )
    
    builder.adjust(2)
    return builder.as_markup()


def get_location_keyboard():
    """Keyboard to request location"""
    keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="📍 Share Location", request_location=True)]
        ],
        resize_keyboard=True,
        one_time_keyboard=True
    )
    return keyboard


def get_admin_keyboard(order_id):
    """Admin keyboard for order confirmation"""
    builder = InlineKeyboardBuilder()
    
    builder.button(
        text="✅ Confirm Order",
        callback_data=f"admin_confirm_{order_id}"
    )
    builder.button(
        text="❌ Reject Order",
        callback_data=f"admin_reject_{order_id}"
    )
    
    builder.adjust(2)
    return builder.as_markup()