import re
from typing import Optional
from database import get_session, UserRepository


def validate_phone_number(phone: str) -> Optional[str]:
    """
    Validate and clean phone number
    Returns cleaned phone number or None if invalid
    """
    # Remove spaces, dashes, parentheses
    cleaned = re.sub(r'[\s\-\(\)]', '', phone)
    
    # Check if it matches a valid phone pattern
    # Accepts formats like: +1234567890, 1234567890, etc.
    pattern = r'^\+?[1-9]\d{7,14}$'
    
    if re.match(pattern, cleaned):
        # Ensure it starts with +
        if not cleaned.startswith('+'):
            cleaned = '+' + cleaned
        return cleaned
    
    return None


def format_price(price: float) -> str:
    """Format price with currency symbol"""
    return f"${price:,.2f}"


def format_cart_message(cart_items) -> str:
    """Format cart items into a readable message"""
    if not cart_items:
        return "🛒 Your cart is empty."
    
    message = "🛒 <b>Your Cart:</b>\n\n"
    
    total = 0
    for item in cart_items:
        variant = item.variant
        product = variant.product
        item_total = variant.price * item.quantity
        total += item_total
        
        message += f"<b>{product.name}</b>\n"
        message += f"  Variant: {variant.name}\n"
        message += f"  Price: {format_price(variant.price)} x {item.quantity}\n"
        message += f"  Subtotal: {format_price(item_total)}\n\n"
    
    message += f"━━━━━━━━━━━━━━━━━━\n"
    message += f"<b>Total: {format_price(total)}</b>"
    
    return message


def format_order_message(order) -> str:
    """Format order details for admin and customer"""
    message = f"📦 <b>Order #{order.id}</b>\n\n"
    
    # Customer info
    user = order.user
    message += f"👤 <b>Customer:</b>\n"
    if user.first_name or user.last_name:
        message += f"  Name: {user.first_name or ''} {user.last_name or ''}".strip() + "\n"
    message += f"  Phone: {user.phone_number}\n"
    if user.username:
        message += f"  Username: @{user.username}\n"
    message += "\n"
    
    # Order items
    message += f"🛍 <b>Items:</b>\n"
    for item in order.items:
        message += f"  • {item.product_name} - {item.variant_name}\n"
        message += f"    {format_price(item.price_at_purchase)} x {item.quantity} = {format_price(item.price_at_purchase * item.quantity)}\n"
    
    message += f"\n💰 <b>Total: {format_price(order.total_amount)}</b>\n\n"
    
    # Note
    if order.note:
        message += f"📝 <b>Note:</b> {order.note}\n\n"
    
    # Location
    if order.location_latitude and order.location_longitude:
        message += f"📍 <b>Delivery Location:</b>\n"
        if order.location_address:
            message += f"  {order.location_address}\n"
        message += f"  Coordinates: {order.location_latitude}, {order.location_longitude}\n"
    
    message += f"\n🕐 <b>Order Time:</b> {order.created_at.strftime('%Y-%m-%d %H:%M:%S')}\n"
    message += f"📊 <b>Status:</b> {order.status.upper()}"
    
    return message


def format_variant_caption(variant, index: int) -> str:
    """Format caption for variant image"""
    caption = f"<b>Variant {index}</b>\n\n"
    caption += f"<b>{variant.name}</b>\n"
    if variant.description:
        caption += f"{variant.description}\n\n"
    caption += f"💰 <b>Price:</b> {format_price(variant.price)}"
    return caption


def is_admin(user_id: int) -> bool:
    """Check if user is admin"""
    from config import ADMIN_IDS
    return user_id in ADMIN_IDS


def get_or_create_user(telegram_id: int, phone_number: str, username=None, first_name=None, last_name=None):
    """Get existing user or create new one"""
    session = get_session()
    try:
        user = UserRepository.get_by_telegram_id(session, telegram_id)
        if not user:
            user = UserRepository.create(
                session=session,
                telegram_id=telegram_id,
                phone_number=phone_number,
                username=username,
                first_name=first_name,
                last_name=last_name
            )
        return user
    finally:
        session.close()