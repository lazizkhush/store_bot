from aiogram import Router, F
from aiogram.types import Message

from database import get_session, UserRepository, OrderRepository
from utils import format_order_message, get_main_menu_keyboard

router = Router()


@router.message(F.text == "📦 My Orders")
async def show_my_orders(message: Message):
    """Show user's order history"""
    session = get_session()
    try:
        user = UserRepository.get_by_telegram_id(session, message.from_user.id)
        
        if not user:
            await message.answer("❌ Please register first by using /start")
            return
        
        orders = OrderRepository.get_user_orders(session, user.id)
        
        if not orders:
            await message.answer(
                "📦 You haven't placed any orders yet.",
                reply_markup=get_main_menu_keyboard()
            )
            return
        
        await message.answer(
            f"📦 <b>Your Orders ({len(orders)})</b>\n\n"
            "Here's your order history:",
            parse_mode="HTML"
        )
        
        for order in orders[:10]:  # Show last 10 orders
            status_emoji = {
                'pending': '⏳',
                'confirmed': '✅',
                'cancelled': '❌',
                'delivered': '📦'
            }
            
            emoji = status_emoji.get(order.status, '❓')
            
            order_msg = f"{emoji} {format_order_message(order)}"
            await message.answer(order_msg, parse_mode="HTML")
        
        if len(orders) > 10:
            await message.answer(f"... and {len(orders) - 10} more orders")
        
    finally:
        session.close()