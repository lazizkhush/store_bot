"""
User registration handlers
File: handlers/registration.py
"""

from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message
from aiogram.fsm.context import FSMContext
from database import User, get_db
from states import OrderStates

router = Router()

@router.message(Command("start"))
async def cmd_start(message: Message, state: FSMContext):
    await state.clear()
    with get_db() as session:
        user = User.get_by_telegram_id(session, message.from_user.id)
        if user:
            await message.answer("Welcome back! You are already registered.\nSend /order to start shopping.")
            return
    await message.answer(
        "Welcome to the E-Commerce Store Bot!\nPlease enter your phone number (e.g. +1234567890):"
    )
    await state.set_state(OrderStates.waiting_for_phone)


@router.message(OrderStates.waiting_for_phone)
async def process_phone(message: Message, state: FSMContext):
    phone = message.text.strip()
    # Basic validation: starts with + and is digits
    if not (phone.startswith("+") and phone[1:].isdigit() and 8 <= len(phone) <= 20):
        await message.answer("Invalid phone number. Please enter in format +1234567890:")
        return
    with get_db() as session:
        user = User.get_by_telegram_id(session, message.from_user.id)
        if not user:
            user = User.create(
                session,
                telegram_id=message.from_user.id,
                phone_number=phone,
                first_name=message.from_user.first_name or "",
                last_name=message.from_user.last_name or "",
                username=message.from_user.username or ""
            )
        else:
            user.phone_number = phone
        session.commit()
    await message.answer("✅ Registration complete!\nSend /order to start shopping.")
    await state.clear()


@router.message(Command("help"))
async def cmd_help(message: Message, state: FSMContext):
    await message.answer(
        "This is a demo e-commerce bot.\n"
        "Commands:\n"
        "/start - Register or login\n"
        "/order - Start shopping\n"
        "/cart - View your cart\n"
        "/help - Show this help message"
    )