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

