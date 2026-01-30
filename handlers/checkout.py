from aiogram import Router, F, Bot
from aiogram.types import Message, CallbackQuery, Location
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

from database import get_session, UserRepository, CartRepository, OrderRepository
from utils import (
    get_note_keyboard,
    get_location_keyboard,
    get_main_menu_keyboard,
    format_order_message,
    get_admin_keyboard
)
from config import Messages, ADMIN_IDS

router = Router()


class CheckoutStates(StatesGroup):
    """States for checkout flow"""
    waiting_note = State()
    waiting_location = State()


@router.callback_query(F.data == "checkout_confirm")
async def start_checkout(callback: CallbackQuery, state: FSMContext):
    """Start checkout process"""
    session = get_session()
    try:
        user = UserRepository.get_by_telegram_id(session, callback.from_user.id)
        cart_items = CartRepository.get_user_cart(session, user.id)
        
        if not cart_items:
            await callback.answer("Your cart is empty!", show_alert=True)
            return
        
        # Ask if user wants to add a note
        await callback.message.edit_text(
            Messages.ASK_NOTE,
            reply_markup=get_note_keyboard()
        )
        
        await callback.answer()
        
    finally:
        session.close()


@router.callback_query(F.data == "note_yes")
async def ask_for_note(callback: CallbackQuery, state: FSMContext):
    """Ask user to enter note"""
    await callback.message.edit_text(Messages.ENTER_NOTE)
    await state.set_state(CheckoutStates.waiting_note)
    await callback.answer()


@router.callback_query(F.data == "note_no")
async def skip_note(callback: CallbackQuery, state: FSMContext):
    """Skip note and ask for location"""
    await state.update_data(note=None)
    await callback.message.edit_text(Messages.ASK_LOCATION)
    await callback.message.answer(
        "👇 Tap the button below:",
        reply_markup=get_location_keyboard()
    )
    await state.set_state(CheckoutStates.waiting_location)
    await callback.answer()


@router.message(CheckoutStates.waiting_note)
async def process_note(message: Message, state: FSMContext):
    """Process note from user"""
    note = message.text
    await state.update_data(note=note)
    
    await message.answer(Messages.ASK_LOCATION)
    await message.answer(
        "👇 Tap the button below:",
        reply_markup=get_location_keyboard()
    )
    await state.set_state(CheckoutStates.waiting_location)


@router.message(CheckoutStates.waiting_location, F.location)
async def process_location(message: Message, state: FSMContext, bot: Bot):
    """Process location and create order"""
    location: Location = message.location
    
    # Get note from state
    data = await state.get_data()
    note = data.get('note')
    
    session = get_session()
    try:
        user = UserRepository.get_by_telegram_id(session, message.from_user.id)
        cart_items = CartRepository.get_user_cart(session, user.id)
        
        if not cart_items:
            await message.answer("Your cart is empty!", reply_markup=get_main_menu_keyboard())
            await state.clear()
            return
        
        # Create order
        order = OrderRepository.create_order(
            session=session,
            user_id=user.id,
            cart_items=cart_items,
            note=note,
            location_lat=location.latitude,
            location_lon=location.longitude
        )
        
        # Clear cart
        CartRepository.clear_cart(session, user.id)
        
        # Send confirmation to user
        await message.answer(
            Messages.ORDER_SENT_TO_ADMIN.format(order_id=order.id),
            reply_markup=get_main_menu_keyboard()
        )
        
        # Send order to admin(s)
        order_message = format_order_message(order)
        
        for admin_id in ADMIN_IDS:
            try:
                # Send order details
                admin_msg = await bot.send_message(
                    admin_id,
                    order_message,
                    reply_markup=get_admin_keyboard(order.id),
                    parse_mode="HTML"
                )
                
                # Send location
                await bot.send_location(
                    admin_id,
                    latitude=location.latitude,
                    longitude=location.longitude
                )
                
                # Update order with admin message ID
                OrderRepository.update_message_ids(session, order.id, admin_msg_id=admin_msg.message_id)
                
            except Exception as e:
                print(f"Error sending to admin {admin_id}: {e}")
        
        # Clear state
        await state.clear()
        
    except Exception as e:
        await message.answer(f"❌ Error creating order: {str(e)}", reply_markup=get_main_menu_keyboard())
        await state.clear()
    finally:
        session.close()


@router.message(CheckoutStates.waiting_location)
async def invalid_location(message: Message):
    """Handle invalid location input"""
    await message.answer(
        "❌ Please share your location using the button below.",
        reply_markup=get_location_keyboard()
    )