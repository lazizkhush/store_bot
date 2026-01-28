"""
Admin order management handlers
File: handlers/admin.py
"""

import logging
from aiogram import Router, F, Bot
from aiogram.types import CallbackQuery

from config import ADMIN_IDS, BOT_TOKEN
from database import Order, OrderItem, get_db

router = Router()
bot = Bot(token=BOT_TOKEN)


@router.callback_query(F.data.startswith("confirm_order_"))
async def confirm_order(callback: CallbackQuery):
    """Admin confirms order"""
    if callback.from_user.id not in ADMIN_IDS:
        await callback.answer("Unauthorized", show_alert=True)
        return
    
    order_id = int(callback.data.split("_")[-1])
    
    with get_db() as session:
        order = Order.get_by_id(session, order_id)
        
        if not order:
            await callback.answer("Order not found", show_alert=True)
            return
        
        order.status = "confirmed"
        
        # Notify customer
        try:
            await bot.send_message(
                order.user.telegram_id,
                f"✅ Your order #{order_id} has been confirmed!\n"
                "We're preparing your delivery."
            )
        except Exception as e:
            logging.error(f"Failed to notify customer: {e}")
    
    await callback.message.edit_text(
        callback.message.text + "\n\n✅ CONFIRMED",
        reply_markup=None
    )
    
    await callback.answer("Order confirmed!")


@router.callback_query(F.data.startswith("cancel_order_"))
async def cancel_order(callback: CallbackQuery):
    """Admin cancels order"""
    if callback.from_user.id not in ADMIN_IDS:
        await callback.answer("Unauthorized", show_alert=True)
        return
    
    order_id = int(callback.data.split("_")[-1])
    
    with get_db() as session:
        order = Order.get_by_id(session, order_id)
        
        if not order:
            await callback.answer("Order not found", show_alert=True)
            return
        
        order.status = "cancelled"
        
        # Restore stock
        order_items = OrderItem.get_by_order(session, order_id)
        for item in order_items:
            item.variant.stock += item.quantity
        
        # Notify customer
        try:
            await bot.send_message(
                order.user.telegram_id,
                f"❌ Your order #{order_id} has been cancelled.\n"
                "Please contact support if you have questions."
            )
        except Exception as e:
            logging.error(f"Failed to notify customer: {e}")
    
    await callback.message.edit_text(
        callback.message.text + "\n\n❌ CANCELLED",
        reply_markup=None
    )
    
    await callback.answer("Order cancelled!")