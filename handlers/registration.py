from aiogram import Router, F
from aiogram.types import Message
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

from database import get_session, UserRepository
from utils import validate_phone_number, get_main_menu_keyboard
from config import Messages

router = Router()


class RegistrationStates(StatesGroup):
    """States for registration flow"""
    waiting_phone = State()


@router.message(CommandStart())
async def cmd_start(message: Message, state: FSMContext):
    """Handle /start command"""
    session = get_session()
    try:
        # Check if user already exists
        user = UserRepository.get_by_telegram_id(session, message.from_user.id)
        
        if user:
            # User already registered
            await message.answer(
                f"Welcome back, {message.from_user.first_name}! 👋",
                reply_markup=get_main_menu_keyboard()
            )
        else:
            # New user - request phone number
            await message.answer(Messages.WELCOME)
            await state.set_state(RegistrationStates.waiting_phone)
    finally:
        session.close()


@router.message(RegistrationStates.waiting_phone)
async def process_phone_number(message: Message, state: FSMContext):
    """Process phone number sent by user"""
    
    # Validate phone number
    phone = validate_phone_number(message.text)
    
    if not phone:
        await message.answer(Messages.INVALID_PHONE)
        return
    
    # Save user to database
    session = get_session()
    try:
        user = UserRepository.create(
            session=session,
            telegram_id=message.from_user.id,
            phone_number=phone,
            username=message.from_user.username,
            first_name=message.from_user.first_name,
            last_name=message.from_user.last_name
        )
        
        await message.answer(
            Messages.PHONE_REGISTERED,
            reply_markup=get_main_menu_keyboard()
        )
        
        # Clear state
        await state.clear()
        
    except Exception as e:
        await message.answer(f"❌ Error registering user: {str(e)}")
    finally:
        session.close()