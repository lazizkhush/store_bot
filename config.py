"""
Configuration file for Telegram Store Bot
File: config.py
"""
import os
from dotenv import load_dotenv

load_dotenv()

# Bot Configuration
BOT_TOKEN = os.getenv('TOKEN')

# Admin Configuration
ADMIN_IDS = [int(id.strip()) for id in os.getenv('ADMIN_IDS', '').split(',') if id.strip()]

# Channel Configuration (for forwarding confirmed orders)
CHANNEL_ID = os.getenv('CHANNEL_ID', '')  # e.g., '@yourchannel' or '-1001234567890'

# Database Configuration
DATABASE_URL = os.getenv('DATABASE_URL', 'sqlite:///store_bot.db')

# States for FSM (Finite State Machine)
class States:
    """User states for conversation flow"""
    WAITING_PHONE = "waiting_phone"
    BROWSING = "browsing"
    WAITING_NOTE = "waiting_note"
    WAITING_LOCATION = "waiting_location"


# Messages
class Messages:
    """Bot messages"""
    
    WELCOME = """
👋 Welcome to our store!

To get started, please share your phone number by typing it manually.

Example: +1234567890
"""
    
    PHONE_REGISTERED = """
✅ Thank you! Your phone number has been registered.

You can now browse our products!
"""
    
    INVALID_PHONE = """
❌ Invalid phone number format.

Please send a valid phone number (e.g., +1234567890)
"""
    
    SELECT_CATEGORY = """
🛍 Please select a category:
"""
    
    SELECT_PRODUCT = """
📦 Please select a product:
"""
    
    CART_EMPTY = """
🛒 Your cart is empty.

Start shopping to add items!
"""
    
    ASK_NOTE = """
📝 Would you like to add a note or comment for this order?
"""
    
    ENTER_NOTE = """
✍️ Please type your note or comment:
"""
    
    ASK_LOCATION = """
📍 Please share the delivery location.

Tap the button below to share your location.
"""
    
    ORDER_SENT_TO_ADMIN = """
✅ Your order has been sent to the administrator!

We'll notify you once it's confirmed.

Order ID: #{order_id}
"""
    
    ORDER_CONFIRMED = """
🎉 Your order has been confirmed!

Order ID: #{order_id}

We'll deliver it to the provided location soon.
"""
    
    ORDER_REJECTED = """
❌ Sorry, your order has been rejected.

Order ID: #{order_id}

Please contact support for more information.
"""
    
    NO_CATEGORIES = """
❌ No categories available at the moment.

Please try again later.
"""
    
    NO_PRODUCTS = """
❌ No products available in this category.

Please select another category.
"""
    
    NO_VARIANTS = """
❌ No variants available for this product.
"""
    
    ITEM_ADDED = """
✅ Item added to cart!
"""

# import os
# from dotenv import load_dotenv
# load_dotenv()

# # Database Configuration
# DATABASE_FILE = "store.db"

# BOT_TOKEN = os.getenv("TOKEN")

# # Admin user IDs - replace with actual admin Telegram IDs
# ADMIN_IDS = [1056263924, 1777601213]