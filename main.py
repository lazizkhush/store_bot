"""
Main entry point for Telegram Store Bot
File: main.py
"""

import asyncio
import logging
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import BotCommand

from config import BOT_TOKEN
from database import init_db
from handlers import registration, shopping, cart, checkout, admin

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

# Initialize bot and dispatcher
bot = Bot(token=BOT_TOKEN)
storage = MemoryStorage()
dp = Dispatcher(storage=storage)

async def set_commands(bot: Bot):
    commands = [
        BotCommand(command="start", description="Botni ishga tushurish"),
        BotCommand(command="order", description="Buyurtma qilish"),
        BotCommand(command="cart", description="Savatni Ko'rish"),
        BotCommand(command="help", description="Yordam")
    ]
    await bot.set_my_commands(commands)


async def main():
    """Start the bot"""
    # Initialize database
    init_db()
    logging.info("Database initialized")
    
    await set_commands(bot)
    # Register all handlers
    dp.include_router(registration.router)
    dp.include_router(shopping.router)
    dp.include_router(cart.router)
    dp.include_router(checkout.router)
    dp.include_router(admin.router)
    
    logging.info("Starting bot...")
    
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