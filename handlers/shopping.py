"""
Product browsing and shopping handlers
File: handlers/shopping.py
"""

from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext

from database import User, Category, Product, Cart
from keyboards import get_categories_keyboard, get_products_keyboard, get_product_keyboard
from states import OrderStates

router = Router()


@router.message(Command("order"))
async def cmd_order(message: Message, state: FSMContext):
    """Handle /order command - show categories"""
    user = User.get_by_telegram_id(message.from_user.id)
    
    if not user or not user.get('phone_number'):
        await message.answer("Please use /start first to register!")
        return
    
    categories = Category.get_all()
    
    if not categories:
        await message.answer("Sorry, no categories available at the moment.")
        return
    
    keyboard = get_categories_keyboard(categories)
    await message.answer("🛍️ Choose a category:", reply_markup=keyboard)
    await state.set_state(OrderStates.browsing_categories)


@router.callback_query(F.data.startswith("category_"))
async def process_category_selection(callback: CallbackQuery, state: FSMContext):
    """Handle category selection"""
    category_id = int(callback.data.split("_")[1])
    
    products = Product.get_by_category(category_id)
    
    if not products:
        await callback.answer("No products in this category", show_alert=True)
        return
    
    category = Category.get_by_id(category_id)
    keyboard = get_products_keyboard(products, category_id)
    
    await callback.message.edit_text(
        f"📦 Products in {category['name']}:",
        reply_markup=keyboard
    )
    await state.update_data(current_category=category_id)
    await state.set_state(OrderStates.browsing_products)
    
    await callback.answer()


@router.callback_query(F.data.startswith("product_"))
async def process_product_selection(callback: CallbackQuery, state: FSMContext):
    """Handle product selection - show product details"""
    product_id = int(callback.data.split("_")[1])
    
    product = Product.get_by_id(product_id)
    
    if not product:
        await callback.answer("Product not found", show_alert=True)
        return
    
    keyboard = get_product_keyboard(product_id)
    
    text = (
        f"🛒 {product['name']}\n\n"
        f"{product['description']}\n\n"
        f"💰 Price: ${product['price']:.2f}\n"
        f"📦 In stock: {product['stock']}"
    )
    
    await callback.message.edit_text(text, reply_markup=keyboard)
    await state.set_state(OrderStates.viewing_product)
    
    await callback.answer()


@router.callback_query(F.data.startswith("add_to_cart_"))
async def process_add_to_cart(callback: CallbackQuery, state: FSMContext):
    """Add product to cart"""
    product_id = int(callback.data.split("_")[-1])
    
    user = User.get_by_telegram_id(callback.from_user.id)
    product = Product.get_by_id(product_id)
    
    if not product or product['stock'] < 1:
        await callback.answer("Product out of stock!", show_alert=True)
        return
    
    # Add to cart
    cart_item = Cart.get_item(user['id'], product_id)
    
    if cart_item:
        if cart_item['quantity'] < product['stock']:
            Cart.update_quantity(user['id'], product_id, cart_item['quantity'] + 1)
            await callback.answer(f"Added another {product['name']} to cart!")
        else:
            await callback.answer("Not enough stock!", show_alert=True)
            return
    else:
        Cart.add_item(user['id'], product_id, 1)
    
    # Update the message with updated keyboard
    keyboard = get_product_keyboard(product_id)
    await callback.message.edit_reply_markup(reply_markup=keyboard)
    
    await callback.answer("✅ Added to cart!")


@router.callback_query(F.data == "back_to_categories")
async def back_to_categories(callback: CallbackQuery, state: FSMContext):
    """Go back to categories"""
    categories = Category.get_all()
    keyboard = get_categories_keyboard(categories)
    
    await callback.message.edit_text("🛍️ Choose a category:", reply_markup=keyboard)
    await state.set_state(OrderStates.browsing_categories)
    
    await callback.answer()


@router.callback_query(F.data.startswith("back_to_products_"))
async def back_to_products(callback: CallbackQuery, state: FSMContext):
    """Go back to products list"""
    category_id = int(callback.data.split("_")[-1])
    
    products = Product.get_by_category(category_id)
    category = Category.get_by_id(category_id)
    keyboard = get_products_keyboard(products, category_id)
    
    await callback.message.edit_text(
        f"📦 Products in {category['name']}:",
        reply_markup=keyboard
    )
    await state.set_state(OrderStates.browsing_products)
    
    await callback.answer()


