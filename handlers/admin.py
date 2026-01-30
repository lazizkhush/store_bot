from aiogram import Router, F, Bot
from aiogram.types import CallbackQuery, Message
from aiogram.filters import Command
from sqlalchemy import func

from database import get_session, OrderRepository
from utils import is_admin, format_order_message, get_admin_keyboard
from config import Messages, CHANNEL_ID

router = Router()


@router.callback_query(F.data.startswith("admin_confirm_"))
async def confirm_order(callback: CallbackQuery, bot: Bot):
    """Admin confirms order"""
    if not is_admin(callback.from_user.id):
        await callback.answer("❌ You are not authorized!", show_alert=True)
        return
    
    order_id = int(callback.data.split("_")[2])
    
    session = get_session()
    try:
        order = OrderRepository.get_by_id(session, order_id)
        
        if not order:
            await callback.answer("❌ Order not found!", show_alert=True)
            return
        
        if order.status != 'pending':
            await callback.answer(f"Order is already {order.status}!", show_alert=True)
            return
        
        # Update order status
        OrderRepository.update_status(session, order_id, 'confirmed')
        
        # Notify customer
        try:
            await bot.send_message(
                order.user.telegram_id,
                Messages.ORDER_CONFIRMED.format(order_id=order.id)
            )
        except Exception as e:
            print(f"Error notifying customer: {e}")
        
        # Forward to channel if configured
        if CHANNEL_ID:
            try:
                order_message = format_order_message(order)
                channel_msg = await bot.send_message(
                    CHANNEL_ID,
                    f"✅ <b>CONFIRMED ORDER</b>\n\n{order_message}",
                    parse_mode="HTML"
                )
                
                # Send location to channel
                if order.location_latitude and order.location_longitude:
                    await bot.send_location(
                        CHANNEL_ID,
                        latitude=order.location_latitude,
                        longitude=order.location_longitude
                    )
                
                # Update order with channel message ID
                OrderRepository.update_message_ids(session, order_id, channel_msg_id=channel_msg.message_id)
                
            except Exception as e:
                print(f"Error forwarding to channel: {e}")
        
        # Update admin message
        await callback.message.edit_text(
            f"✅ <b>ORDER CONFIRMED</b>\n\n{format_order_message(order)}",
            parse_mode="HTML"
        )
        
        await callback.answer("✅ Order confirmed and sent to channel!", show_alert=True)
        
    except Exception as e:
        await callback.answer(f"❌ Error: {str(e)}", show_alert=True)
    finally:
        session.close()


@router.callback_query(F.data.startswith("admin_reject_"))
async def reject_order(callback: CallbackQuery, bot: Bot):
    """Admin rejects order"""
    if not is_admin(callback.from_user.id):
        await callback.answer("❌ You are not authorized!", show_alert=True)
        return
    
    order_id = int(callback.data.split("_")[2])
    
    session = get_session()
    try:
        order = OrderRepository.get_by_id(session, order_id)
        
        if not order:
            await callback.answer("❌ Order not found!", show_alert=True)
            return
        
        if order.status != 'pending':
            await callback.answer(f"Order is already {order.status}!", show_alert=True)
            return
        
        # Update order status
        OrderRepository.update_status(session, order_id, 'cancelled')
        
        # Notify customer
        try:
            await bot.send_message(
                order.user.telegram_id,
                Messages.ORDER_REJECTED.format(order_id=order.id)
            )
        except Exception as e:
            print(f"Error notifying customer: {e}")
        
        # Update admin message
        await callback.message.edit_text(
            f"❌ <b>ORDER REJECTED</b>\n\n{format_order_message(order)}",
            parse_mode="HTML"
        )
        
        await callback.answer("❌ Order rejected!", show_alert=True)
        
    except Exception as e:
        await callback.answer(f"❌ Error: {str(e)}", show_alert=True)
    finally:
        session.close()


@router.message(Command("admin"))
async def admin_panel(message: Message):
    """Show admin panel"""
    if not is_admin(message.from_user.id):
        await message.answer("❌ You are not authorized!")
        return
    
    await message.answer(
        "👤 <b>Admin Panel</b>\n\n"
        "You can manage orders by responding to order notifications.\n\n"
        "Available commands:\n"
        "/stats - View statistics\n"
        "/pending - View pending orders",
        parse_mode="HTML"
    )


@router.message(Command("stats"))
async def show_stats(message: Message):
    """Show order statistics"""
    if not is_admin(message.from_user.id):
        await message.answer("❌ You are not authorized!")
        return
    
    session = get_session()
    try:
        from database.models import Order, User
        
        total_orders = session.query(Order).count()
        pending_orders = session.query(Order).filter(Order.status == 'pending').count()
        confirmed_orders = session.query(Order).filter(Order.status == 'confirmed').count()
        cancelled_orders = session.query(Order).filter(Order.status == 'cancelled').count()
        total_users = session.query(User).count()
        
        total_revenue = session.query(func.sum(Order.total_amount)).filter(
            Order.status == 'confirmed'
        ).scalar() or 0
        
        stats_message = f"""
📊 <b>Store Statistics</b>

👥 Total Users: {total_users}
📦 Total Orders: {total_orders}

📋 Order Status:
  • Pending: {pending_orders}
  • Confirmed: {confirmed_orders}
  • Cancelled: {cancelled_orders}

💰 Total Revenue: ${total_revenue:,.2f}
"""
        
        await message.answer(stats_message, parse_mode="HTML")
        
    finally:
        session.close()


@router.message(Command("pending"))
async def show_pending_orders(message: Message):
    """Show all pending orders"""
    if not is_admin(message.from_user.id):
        await message.answer("❌ You are not authorized!")
        return
    
    session = get_session()
    try:
        from database.models import Order
        
        pending_orders = session.query(Order).filter(Order.status == 'pending').order_by(Order.created_at.desc()).all()
        
        if not pending_orders:
            await message.answer("✅ No pending orders!")
            return
        
        await message.answer(f"📋 <b>Pending Orders ({len(pending_orders)})</b>", parse_mode="HTML")
        
        for order in pending_orders:
            order_msg = format_order_message(order)
            await message.answer(
                order_msg,
                reply_markup=get_admin_keyboard(order.id),
                parse_mode="HTML"
            )
            
            if order.location_latitude and order.location_longitude:
                await message.answer_location(
                    latitude=order.location_latitude,
                    longitude=order.location_longitude
                )
        
    finally:
        session.close()