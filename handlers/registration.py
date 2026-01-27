"""
User registration and onboarding handlers
File: handlers/registration.py
"""

from aiogram import Router, F
from aiogram.filters import CommandStart, Command
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove
from aiogram.fsm.context import FSMContext

from database import User
from states import OrderStates

router = Router()


@router.message(CommandStart())
async def cmd_start(message: Message, state: FSMContext):
    """Handle /start command"""
    user = User.get_by_telegram_id(message.from_user.id)
    
    if user and user.get('phone_number'):
        await message.answer(
            f"Welcome back, {user['first_name']}! 👋\n\n"
            "Use /order to start shopping\n"
            "Use /cart to view your cart\n"
            "Use /help for more commands"
        )
    else:
        # Request phone number
        keyboard = ReplyKeyboardMarkup(
            keyboard=[[KeyboardButton(text="📱 Share Phone Number", request_contact=True)]],
            resize_keyboard=True,
            one_time_keyboard=True
        )
        await message.answer(
            "Welcome to our store! 🛍️\n\n"
            "To get started, please share your phone number:",
            reply_markup=keyboard
        )
        await state.set_state(OrderStates.waiting_for_phone)


@router.message(OrderStates.waiting_for_phone, F.contact)
async def process_phone_number(message: Message, state: FSMContext):
    """Process shared phone number"""
    contact = message.contact
    
    user = User.get_by_telegram_id(message.from_user.id)
    
    if user:
        User.update_phone(
            message.from_user.id,
            contact.phone_number,
            message.from_user.first_name or "",
            message.from_user.last_name or "",
            message.from_user.username or ""
        )
    else:
        User.create(
            message.from_user.id,
            contact.phone_number,
            message.from_user.first_name or "",
            message.from_user.last_name or "",
            message.from_user.username or ""
        )
    
    await message.answer(
        "Great! Your phone number has been saved. ✅\n\n"
        "Use /order to start shopping!",
        reply_markup=ReplyKeyboardRemove()
    )
    await state.clear()


@router.message(Command("help"))
async def cmd_help(message: Message):
    """Show help message"""
    help_text = (
        "🤖 Bot Commands:\n\n"
        "/start - Register or restart\n"
        "/order - Browse products\n"
        "/cart - View your cart\n"
        "/help - Show this message"
    )
    await message.answer(help_text)