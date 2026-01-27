"""
Configuration file for Telegram Store Bot
File: config.py
"""
import os
from dotenv import load_dotenv
load_dotenv()

# Database Configuration
DATABASE_FILE = "store.db"

BOT_TOKEN = os.getenv("TOKEN")

# Admin user IDs - replace with actual admin Telegram IDs
ADMIN_IDS = [1056263924, 1777601213]