"""
Admin order management handlers
File: handlers/admin.py
"""

import logging
from aiogram import Router, F, Bot
from aiogram.types import CallbackQuery

from config import ADMIN_IDS, BOT_TOKEN
from database.models.order import Order
from database.models.order_item import OrderItem
from database.models.product import Product


router = Router()
bot = Bot(token=BOT_TOKEN)


@router.callback_query(F.data.startswith("confirm_order_"))
async def confirm_order(callback: CallbackQuery):
    """Admin confirms order"""
    if callback.from_user.id not in ADMIN_IDS:
        await callback.answer("Unauthorized", show_alert=True)
        return
    
    order_id = int(callback.data.split("_")[-1])
    
    order = Order.get_by_id(order_id)
    
    if not order:
        await callback.answer("Order not found", show_alert=True)
        return
    
    Order.update_status(order_id, "confirmed")
    
    # Notify customer
    try:
        await bot.send_message(
            order['telegram_id'],
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
    
    order = Order.get_by_id(order_id)
    
    if not order:
        await callback.answer("Order not found", show_alert=True)
        return
    
    Order.update_status(order_id, "cancelled")
    
    # Restore stock
    order_items = OrderItem.get_by_order(order_id)
    for item in order_items:
        Product.update_stock(item['product_id'], item['quantity'])
    
    # Notify customer
    try:
        await bot.send_message(
            order['telegram_id'],
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


    