from aiogram import Router, F
from aiogram.types import Message, CallbackQuery

from database import get_session, UserRepository, CartRepository
from utils import format_cart_message, get_cart_keyboard
from config import Messages

router = Router()


@router.message(F.text == "🛒 View Cart")
async def view_cart(message: Message):
    """Display user's shopping cart"""
    session = get_session()
    try:
        user = UserRepository.get_by_telegram_id(session, message.from_user.id)
        
        if not user:
            await message.answer("❌ Please register first by using /start")
            return
        
        cart_items = CartRepository.get_user_cart(session, user.id)
        
        if not cart_items:
            await message.answer(
                Messages.CART_EMPTY,
                reply_markup=get_cart_keyboard(has_items=False)
            )
            return
        
        cart_message = format_cart_message(cart_items)
        
        await message.answer(
            cart_message,
            reply_markup=get_cart_keyboard(has_items=True),
            parse_mode="HTML"
        )
        
    finally:
        session.close()


@router.callback_query(F.data == "cart_clear")
async def clear_cart(callback: CallbackQuery):
    """Clear all items from cart"""
    session = get_session()
    try:
        user = UserRepository.get_by_telegram_id(session, callback.from_user.id)
        
        if user:
            CartRepository.clear_cart(session, user.id)
            await callback.message.edit_text(
                "🗑 Cart cleared!",
                reply_markup=get_cart_keyboard(has_items=False)
            )
        
        await callback.answer("Cart cleared!", show_alert=False)
        
    finally:
        session.close()