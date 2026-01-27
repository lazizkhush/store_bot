"""
Checkout and order placement handlers
File: handlers/checkout.py
"""

import logging
from aiogram import Router, F, Bot
from aiogram.types import CallbackQuery, Message, ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove
from aiogram.fsm.context import FSMContext

from config import ADMIN_IDS, BOT_TOKEN
from database import User, Cart, Order, OrderItem, Product
from keyboards import get_admin_order_keyboard
from states import OrderStates

router = Router()
bot = Bot(token=BOT_TOKEN)


@router.callback_query(F.data == "checkout")
async def process_checkout(callback: CallbackQuery, state: FSMContext):
    """Start checkout process"""
    user = User.get_by_telegram_id(callback.from_user.id)
    cart_items = Cart.get_user_cart(user['id'])
    
    if not cart_items:
        await callback.answer("Your cart is empty!", show_alert=True)
        return
    
    await callback.message.edit_text(
        "📍 Please share your delivery location:",
        reply_markup=None
    )
    
    keyboard = ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text="📍 Share Location", request_location=True)]],
        resize_keyboard=True,
        one_time_keyboard=True
    )
    
    await callback.message.answer(
        "Click the button below to share your location:",
        reply_markup=keyboard
    )
    
    await state.set_state(OrderStates.waiting_for_location)
    await callback.answer()


@router.message(OrderStates.waiting_for_location, F.location)
async def process_location(message: Message, state: FSMContext):
    """Process location and create order"""
    location = message.location
    
    user = User.get_by_telegram_id(message.from_user.id)
    cart_items = Cart.get_user_cart(user['id'])
    
    if not cart_items:
        await message.answer("Your cart is empty!", reply_markup=ReplyKeyboardRemove())
        await state.clear()
        return
    
    # Calculate total
    total = sum(item['price'] * item['quantity'] for item in cart_items)
    
    # Create order
    order_id = Order.create(user['id'], total, location.latitude, location.longitude)
    
    # Create order items and update stock
    for cart_item in cart_items:
        OrderItem.create(
            order_id,
            cart_item['product_id'],
            cart_item['quantity'],
            cart_item['price']
        )
        Product.update_stock(cart_item['product_id'], -cart_item['quantity'])
    
    # Clear cart
    Cart.clear_cart(user['id'])
    
    # Notify user
    await message.answer(
        f"✅ Order #{order_id} created successfully!\n\n"
        f"Total: ${total:.2f}\n"
        f"Status: Pending confirmation\n\n"
        "Our team will contact you shortly!",
        reply_markup=ReplyKeyboardRemove()
    )
    
    # Notify admins
    order_text = (
        f"🆕 NEW ORDER #{order_id}\n\n"
        f"👤 Customer: {user['first_name']} {user.get('last_name', '')}\n"
        f"📱 Phone: {user['phone_number']}\n"
        f"💰 Total: ${total:.2f}\n\n"
        f"📦 Items:\n"
    )
    
    order_items = OrderItem.get_by_order(order_id)
    for item in order_items:
        order_text += f"• {item['name']} x{item['quantity']} - ${item['price'] * item['quantity']:.2f}\n"
    
    keyboard = get_admin_order_keyboard(order_id)
    
    for admin_id in ADMIN_IDS:
        try:
            await bot.send_message(admin_id, order_text, reply_markup=keyboard)
            await bot.send_location(admin_id, location.latitude, location.longitude)
        except Exception as e:
            logging.error(f"Failed to notify admin {admin_id}: {e}")
    
    await state.clear()