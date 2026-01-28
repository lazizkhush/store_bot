"""
Shopping cart management handlers
File: handlers/cart.py
"""

from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext

from database import User, Cart, get_db
from keyboards import get_cart_keyboard

router = Router()


@router.message(Command("cart"))
@router.callback_query(F.data == "view_cart")
async def view_cart(message_or_callback, state: FSMContext):
    """View cart contents"""
    if isinstance(message_or_callback, CallbackQuery):
        callback = message_or_callback
        user_id = callback.from_user.id
        is_callback = True
    else:
        message = message_or_callback
        user_id = message.from_user.id
        is_callback = False
    
    with get_db() as session:
        user = User.get_by_telegram_id(session, user_id)
        cart_items = Cart.get_user_cart(session, user.id)
        
        if not cart_items:
            text = "🛒 Your cart is empty!"
            keyboard = None
        else:
            total = sum(item.variant.price * item.quantity for item in cart_items)
            
            text = "🛒 Your Cart:\n\n"
            for item in cart_items:
                product_name = item.variant.product.name
                variant_name = item.variant.variant_name
                price = item.variant.price
                quantity = item.quantity
                
                text += f"• {product_name} ({variant_name})\n"
                text += f"  ${price:.2f} x {quantity} = ${price * quantity:.2f}\n\n"
            
            text += f"💰 Total: ${total:.2f}"
            keyboard = get_cart_keyboard()
        
        if is_callback:
            # Delete if it's a photo message
            try:
                await callback.message.delete()
                await callback.message.answer(text, reply_markup=keyboard)
            except:
                await callback.message.edit_text(text, reply_markup=keyboard)
            await callback.answer()
        else:
            await message.answer(text, reply_markup=keyboard)