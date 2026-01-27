"""
Telegram Store Bot using aiogram 3.x and SQLAlchemy
Main bot file - bot.py
"""
from dotenv import load_dotenv
import os
import asyncio
import logging
from aiogram import Bot, Dispatcher, F, Router
from aiogram.filters import CommandStart, Command
from aiogram.types import Message, CallbackQuery, ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove, BotCommand
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.storage.memory import MemoryStorage

from database import init_db, User, Category, Product, Order, OrderItem, Cart, get_session
from keyboards import get_categories_keyboard, get_products_keyboard, get_product_keyboard, get_cart_keyboard, get_admin_order_keyboard

load_dotenv()
# Configure logging
logging.basicConfig(level=logging.INFO)

# Bot token - replace with your actual token
BOT_TOKEN = os.getenv("TOKEN")

# Admin user IDs - replace with actual admin Telegram IDs
ADMIN_IDS = [1056263924, 1777601213]  # Add admin user IDs here

bot = Bot(token=BOT_TOKEN)
storage = MemoryStorage()
dp = Dispatcher(storage=storage)
router = Router()


# States for order flow
class OrderStates(StatesGroup):
    waiting_for_phone = State()
    browsing_categories = State()
    browsing_products = State()
    viewing_product = State()
    in_cart = State()
    waiting_for_location = State()


@router.message(CommandStart())
async def cmd_start(message: Message, state: FSMContext):
    """Handle /start command"""
    async with get_session() as session:
        user = await User.get_by_telegram_id(session, message.from_user.id)
        
        if user and user.phone_number:
            await message.answer(
                f"Welcome back, {user.first_name}!\n\n"
                "Use /order to start shopping\n"
                "Use /cart to view your cart\n"
                "Use /help for more commands"
            )
        else:
            # Request phone number
            keyboard = ReplyKeyboardMarkup(
                keyboard=[[KeyboardButton(text="📱 Telefon raqamni ulashish", request_contact=True)]],
                resize_keyboard=True,
                one_time_keyboard=True
            )
            await message.answer(
                "Do'konimizga xush kelibsiz! 🛍️\n\n"
                "Botdan foydalanish uchun telefon raqamingizni yuboring:",
                reply_markup=keyboard
            )
            await state.set_state(OrderStates.waiting_for_phone)


@router.message(OrderStates.waiting_for_phone, F.contact)
async def process_phone_number(message: Message, state: FSMContext):
    """Process shared phone number"""
    contact = message.contact
    
    async with get_session() as session:
        user = await User.get_by_telegram_id(session, message.from_user.id)
        
        if user:
            user.phone_number = contact.phone_number
            user.first_name = message.from_user.first_name or ""
            user.last_name = message.from_user.last_name or ""
            user.username = message.from_user.username or ""
        else:
            user = User(
                telegram_id=message.from_user.id,
                phone_number=contact.phone_number,
                first_name=message.from_user.first_name or "",
                last_name=message.from_user.last_name or "",
                username=message.from_user.username or ""
            )
            session.add(user)
        
        await session.commit()
    
    await message.answer(
        "Botdan foydalanishingiz mumkin ✅\n\n"
        "/order komandasi orqali buyurtma berishingiz mumkin!",
        reply_markup=ReplyKeyboardRemove()
    )
    await state.clear()


@router.message(Command("order"))
async def cmd_order(message: Message, state: FSMContext):
    """Handle /order command - show categories"""
    async with get_session() as session:
        user = await User.get_by_telegram_id(session, message.from_user.id)
        
        if not user or not user.phone_number:
            await message.answer("Avaal /start komandasi orqali ro'yxatdan o'ting")
            return
        
        categories = await Category.get_all(session)
        
        if not categories:
            await message.answer("Sorry, no categories available at the moment.")
            return
        
        keyboard = get_categories_keyboard(categories)
        await message.answer("🛍️ Kerakli bo'limni tanlang:", reply_markup=keyboard)
        await state.set_state(OrderStates.browsing_categories)


@router.callback_query(F.data.startswith("category_"))
async def process_category_selection(callback: CallbackQuery, state: FSMContext):
    """Handle category selection"""
    category_id = int(callback.data.split("_")[1])
    
    async with get_session() as session:
        products = await Product.get_by_category(session, category_id)
        
        if not products:
            await callback.answer("No products in this category", show_alert=True)
            return
        
        category = await Category.get_by_id(session, category_id)
        keyboard = get_products_keyboard(products, category_id)
        
        await callback.message.edit_text(
            f"📦 {category.name} Bo'limidagi mahsulotlar:",
            reply_markup=keyboard
        )
        await state.update_data(current_category=category_id)
        await state.set_state(OrderStates.browsing_products)
    
    await callback.answer()


@router.callback_query(F.data.startswith("product_"))
async def process_product_selection(callback: CallbackQuery, state: FSMContext):
    """Handle product selection - show product details"""
    product_id = int(callback.data.split("_")[1])
    
    async with get_session() as session:
        product = await Product.get_by_id(session, product_id)
        
        if not product:
            await callback.answer("Product not found", show_alert=True)
            return
        
        keyboard = await get_product_keyboard(product_id)
        
        text = (
            f"🛒 {product.name}\n\n"
            f"{product.description}\n\n"
            f"💰 Narxi: ${product.price:.2f}\n"
            f"📦 Mavjud: {product.stock} ta"
        )
        
        await callback.message.edit_text(text, reply_markup=keyboard)
        await state.set_state(OrderStates.viewing_product)
    
    await callback.answer()


@router.callback_query(F.data.startswith("add_to_cart_"))
async def process_add_to_cart(callback: CallbackQuery, state: FSMContext):
    """Add product to cart"""
    product_id = int(callback.data.split("_")[-1])
    
    async with get_session() as session:
        user = await User.get_by_telegram_id(session, callback.from_user.id)
        product = await Product.get_by_id(session, product_id)
        
        if not product or product.stock < 1:
            await callback.answer("Product out of stock!", show_alert=True)
            return
        
        # Add to cart
        cart_item = await Cart.get_item(session, user.id, product_id)
        
        if cart_item:
            if cart_item.quantity < product.stock:
                cart_item.quantity += 1
                await callback.answer(f"Yana 1ta {product.name} savatga qo'shildi!")
            else:
                await callback.answer("Not enough stock!", show_alert=True)
                return
        else:
            cart_item = Cart(user_id=user.id, product_id=product_id, quantity=1)
            session.add(cart_item)
        
        await session.commit()
    
    await callback.answer("✅ Savatga qo'shildi")


@router.callback_query(F.data == "back_to_categories")
async def back_to_categories(callback: CallbackQuery, state: FSMContext):
    """Go back to categories"""
    async with get_session() as session:
        categories = await Category.get_all(session)
        keyboard = get_categories_keyboard(categories)
        
        await callback.message.edit_text("🛍️ Bo'lim tanlang:", reply_markup=keyboard)
        await state.set_state(OrderStates.browsing_categories)
    
    await callback.answer()


@router.callback_query(F.data.startswith("back_to_products_"))
async def back_to_products(callback: CallbackQuery, state: FSMContext):
    """Go back to products list"""
    category_id = int(callback.data.split("_")[-1])
    
    async with get_session() as session:
        products = await Product.get_by_category(session, category_id)
        category = await Category.get_by_id(session, category_id)
        keyboard = get_products_keyboard(products, category_id)
        
        await callback.message.edit_text(
            f"📦 Products in {category.name}:",
            reply_markup=keyboard
        )
        await state.set_state(OrderStates.browsing_products)
    
    await callback.answer()


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
    
    async with get_session() as session:
        user = await User.get_by_telegram_id(session, user_id)
        cart_items = await Cart.get_user_cart(session, user.id)
        
        if not cart_items:
            text = "🛒 Your cart is empty!"
            keyboard = None
        else:
            total = sum(item.product.price * item.quantity for item in cart_items)
            
            text = "🛒 Your Cart:\n\n"
            for item in cart_items:
                text += f"• {item.product.name}\n"
                text += f"  ${item.product.price:.2f} x {item.quantity} = ${item.product.price * item.quantity:.2f}\n\n"
            
            text += f"💰 Jami: ${total:.2f}"
            keyboard = get_cart_keyboard()
        
        if is_callback:
            await callback.message.edit_text(text, reply_markup=keyboard)
            await callback.answer()
        else:
            await message.answer(text, reply_markup=keyboard)


@router.callback_query(F.data == "checkout")
async def process_checkout(callback: CallbackQuery, state: FSMContext):
    """Start checkout process"""
    async with get_session() as session:
        user = await User.get_by_telegram_id(session, callback.from_user.id)
        cart_items = await Cart.get_user_cart(session, user.id)
        
        if not cart_items:
            await callback.answer("Your cart is empty!", show_alert=True)
            return
    
    await callback.message.edit_text(
        "📍 Manzilingizni yuboring",
        reply_markup=None
    )
    
    keyboard = ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text="📍 Manzilni yuborish", request_location=True)]],
        resize_keyboard=True,
        one_time_keyboard=True
    )
    
    await callback.message.answer(
        "Click the button below to share your location:",
        reply_markup=keyboard
    )
    
    await state.set_state(OrderStates.waiting_for_location)
    await callback.answer()


@router.message(OrderStates.waiting_for_location, F.location)
async def process_location(message: Message, state: FSMContext):
    """Process location and create order"""
    location = message.location
    
    async with get_session() as session:
        user = await User.get_by_telegram_id(session, message.from_user.id)
        cart_items = await Cart.get_user_cart(session, user.id)
        
        if not cart_items:
            await message.answer("Your cart is empty!", reply_markup=ReplyKeyboardRemove())
            await state.clear()
            return
        
        # Calculate total
        total = sum(item.product.price * item.quantity for item in cart_items)
        
        # Create order
        order = Order(
            user_id=user.id,
            total_price=total,
            delivery_latitude=location.latitude,
            delivery_longitude=location.longitude,
            status="pending"
        )
        session.add(order)
        await session.flush()
        
        # Create order items
        for cart_item in cart_items:
            order_item = OrderItem(
                order_id=order.id,
                product_id=cart_item.product_id,
                quantity=cart_item.quantity,
                price=cart_item.product.price
            )
            session.add(order_item)
            
            # Update product stock
            cart_item.product.stock -= cart_item.quantity
        
        # Clear cart
        await Cart.clear_cart(session, user.id)
        
        await session.commit()
        
        # Notify user
        await message.answer(
            f"✅ Buyurtma #{order.id} muvafaqqiyatli yaratildi\n\n"
            f"Jami: ${total:.2f}\n"
            f"Status: Ko'rib chiqilmoqda\n\n"
            "Sizga tez orada bog'lanamiz",
            reply_markup=ReplyKeyboardRemove()
        )
        
        # Notify admins
        order_text = (
            f"🆕 Yangi buyurtma #{order.id}\n\n"
            f"👤 Mijoz: {user.first_name} {user.last_name}\n"
            f"📱 Telefon: {user.phone_number}\n"
            f"💰 Jami: ${total:.2f}\n\n"
            f"📦 Mahsulotlar:\n"
        )
        
        for item in await OrderItem.get_by_order(session, order.id):
            order_text += f"• {item.product.name} x{item.quantity} - ${item.price * item.quantity:.2f}\n"
        
        keyboard = get_admin_order_keyboard(order.id)
        
        for admin_id in ADMIN_IDS:
            try:
                await bot.send_message(admin_id, order_text, reply_markup=keyboard)
                await bot.send_location(admin_id, location.latitude, location.longitude)
            except Exception as e:
                logging.error(f"Failed to notify admin {admin_id}: {e}")
    
    await state.clear()


@router.callback_query(F.data.startswith("confirm_order_"))
async def confirm_order(callback: CallbackQuery):
    """Admin confirms order"""
    if callback.from_user.id not in ADMIN_IDS:
        await callback.answer("Unauthorized", show_alert=True)
        return
    
    order_id = int(callback.data.split("_")[-1])
    
    async with get_session() as session:
        order = await Order.get_by_id(session, order_id)
        
        if not order:
            await callback.answer("Order not found", show_alert=True)
            return
        
        order.status = "confirmed"
        await session.commit()
        
        # Notify customer
        try:
            await bot.send_message(
                order.user.telegram_id,
                f"✅ Buyurtma #{order_id} tasdiqlandi!\n"
                "Buyurtmangiz tayyorlanmoqda"
            )
        except Exception as e:
            logging.error(f"Failed to notify customer: {e}")
        
        await callback.message.edit_text(
            callback.message.text + "\n\n✅ Tasdiqlandi",
            reply_markup=None
        )
    
    await callback.answer("Buyurtma tasdiqlandi!")


@router.callback_query(F.data.startswith("cancel_order_"))
async def cancel_order(callback: CallbackQuery):
    """Admin cancels order"""
    if callback.from_user.id not in ADMIN_IDS:
        await callback.answer("Unauthorized", show_alert=True)
        return
    
    order_id = int(callback.data.split("_")[-1])
    
    async with get_session() as session:
        order = await Order.get_by_id(session, order_id)
        
        if not order:
            await callback.answer("Order not found", show_alert=True)
            return
        
        order.status = "cancelled"
        
        # Restore stock
        order_items = await OrderItem.get_by_order(session, order_id)
        for item in order_items:
            item.product.stock += item.quantity
        
        await session.commit()
        
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

async def set_commands(bot: Bot):
    commands = [
        BotCommand(command="start", description="Botni ishga tushurish"),
        BotCommand(command="order", description="Buyurtma qilish"),
        BotCommand(command="cart", description="Savatni Ko'rish"),
        BotCommand(command="help", description="Yordam")
    ]
    await bot.set_my_commands(commands)

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


async def main():
    """Start the bot"""
    # Initialize database
    await init_db()
    
    # Register router
    dp.include_router(router)
    await set_commands(bot)
    
    # Start polling
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())






# from aiogram import Bot, Dispatcher, Router
# from aiogram.filters import Command
# from dotenv import load_dotenv
# import os 
# import asyncio
# from aiogram.types import (
#     Message, BotCommand, 
#     CallbackQuery)
# from callback_utils import *
# from keyboards import categories_keyboard, products_keyboard, order_confirmation_kb
# load_dotenv()
# token = os.getenv("TOKEN")

# dp = Dispatcher()
# router = Router()
# bot = Bot(token)
# ADMIN_ID = 1056263924

# async def set_commands(bot: Bot):
#     commands = [
#         BotCommand(command="start", description="Botni ishga tushurish"),
#         BotCommand(command="order", description="Buyurtma qilish")
#     ]
#     await bot.set_my_commands(commands)
# products = []
# cart = []

# @router.message(Command('order'))
# async def order(message: Message):
#     await message.answer(
#         "Buyurtma berish uchun mahsulot bo'limini tanlang:", 
#         reply_markup=categories_keyboard())
    
# @router.callback_query()
# async def handle_category(callback: CallbackQuery):
#     data = callback.data

#     if data.startswith('cat_'):
#         parts = data.split("_")
#         await callback.message.edit_text(
#             text="Mahsulotni tanlang: ",
#             reply_markup=products_keyboard(int(parts[1]))
#         )

#     elif data.startswith("prod_"):
#         await select_product(data, callback)

#     elif data == "back_to_categories":
#         await callback.message.edit_text(
#             text="Buyurtma berish uchun mahsulot bo'limini tanlang:", 
#             reply_markup=categories_keyboard()
#         )
#     elif data.startswith("back_to_products"):
#         parts = data.split("_", 3)
#         category = parts[-1]
#         await callback.message.edit_text(
#             text="Mahsulotni tanlang: ",
#             reply_markup=products_keyboard(category)
#         )

#     elif data.startswith("addtocart_"):
#         # addtocart_cat_drink_4
#         parts = data.split("_")
#         category = f"cat_{parts[2]}"
#         product_id = int(parts[3])
        
#         for cart_item in cart:
#             if cart_item["id"] == product_id:
#                 cart_item["quantity"] += 1
#                 break
#         else:
#             cart.append({"id":product_id, "category" : category, "quantity":1})

#         await callback.answer("Added to cart ✅")
#     elif data == "see_cart":

#         message = "Savatdagi mahsulotlar:\n"
#         message += see_cart(cart, products)
    
#         await callback.message.edit_text(text=message, reply_markup=order_confirmation_kb())

#     elif data.startswith("send_order"):

#         message = "Yangi buyurtma!!\n"
#         message += see_cart(cart, products)
        
#         await bot.send_message(ADMIN_ID, message)
#         await callback.answer()

#     else:
#         await callback.answer()



# dp.include_router(router)
# async def  main():

#     await set_commands(bot)
#     await dp.start_polling(bot)


# asyncio.run(main())