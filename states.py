"""
Finite State Machine states for bot workflows
File: states.py
"""

from aiogram.fsm.state import State, StatesGroup


class OrderStates(StatesGroup):
    """States for the ordering process"""
    waiting_for_phone = State()
    browsing_categories = State()
    browsing_products = State()
    viewing_product = State()
    in_cart = State()
    waiting_for_location = State()