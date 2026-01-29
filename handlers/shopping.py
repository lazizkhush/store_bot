"""
Product browsing and shopping handlers
File: handlers/shopping.py
"""

from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery, InputMediaPhoto
from aiogram.fsm.context import FSMContext

from database.models.category import Category
from database.models.product import Product
from database.models.product_image import ProductImage
from database.models.product_variant import ProductVariant
from database.models.user import User
from database.models.cart import Cart
from database.init_db import get_db
from keyboards import (get_categories_keyboard,
                       get_products_keyboard, get_product_variants_keyboard,
                       get_variant_confirmation_keyboard)
from keyboards import (
    get_categories_keyboard,
    get_products_keyboard,
    get_product_variants_keyboard,
    get_variant_confirmation_keyboard
)
from states import OrderStates

router = Router()


@router.message(Command("order"))
async def cmd_order(message: Message, state: FSMContext):
    """Handle /order command - show categories"""
    with get_db() as session:
        user = User.get_by_telegram_id(session, message.from_user.id)
        
        if not user or not user.phone_number:
            await message.answer("Please use /start first to register!")
            return
        
        categories = Category.get_all(session)
        
        if not categories:
            await message.answer("Sorry, no categories available at the moment.")
            return
        
        keyboard = get_categories_keyboard(categories)
        await message.answer("🛍️ Choose a category:", reply_markup=keyboard)
        await state.set_state(OrderStates.browsing_categories)


@router.callback_query(F.data.startswith("category_"))
async def process_category_selection(callback: CallbackQuery, state: FSMContext):
    """Handle category selection - show products in category"""
    category_id = int(callback.data.split("_")[1])
    with get_db() as session:
        products = Product.get_by_category(session, category_id)
        if not products:
            await callback.answer("No products in this category", show_alert=True)
            return
        category = Category.get_by_id(session, category_id)
        keyboard = get_products_keyboard(products, category_id)
        await callback.message.edit_text(
            f"📦 Products in {category.name}:",
            reply_markup=keyboard
        )
        await state.update_data(current_category=category_id)
        await state.set_state(OrderStates.browsing_products)
    await callback.answer()





@router.callback_query(F.data.startswith("product_"))
async def process_product_selection(callback: CallbackQuery, state: FSMContext):
    """Handle product selection - show images and variants"""
    product_id = int(callback.data.split("_")[1])
    
    with get_db() as session:
        product = Product.get_by_id(session, product_id)
        
        if not product:
            await callback.answer("Product not found", show_alert=True)
            return
        
        # Get product images
        images = ProductImage.get_by_product(session, product_id)
        
        # Get product variants
        variants = ProductVariant.get_by_product(session, product_id)
        
        if not variants:
            await callback.answer("No variants available for this product", show_alert=True)
            return
        
        # Build product info text
        text = (
            f"🛒 {product.name}\n\n"
            f"{product.description}\n\n"
        )
        
        if images:
            text += f"📸 {len(images)} image(s) available\n"
            if len(images) > 1:
                text += "Use numbered buttons to view different images\n\n"
        
        text += "Available variants:"
        
        keyboard = get_product_variants_keyboard(variants, product_id, len(images))
        
        # Send images if available
        if images:
            # Delete previous message
            await callback.message.delete()
            
            # Send first image with product info
            await callback.message.answer_photo(
                photo=images[0].file_id,
                caption=text,
                reply_markup=keyboard
            )
            
            # Store image data in state
            await state.update_data(
                current_product=product_id,
                product_images=[img.file_id for img in images],
                current_image_index=0
            )
        else:
            # No images, just edit text
            await callback.message.edit_text(text, reply_markup=keyboard)
            await state.update_data(current_product=product_id)
        
        await state.set_state(OrderStates.viewing_product)
    
    await callback.answer()


@router.callback_query(F.data.startswith("view_image_"))
async def view_image(callback: CallbackQuery, state: FSMContext):
    """Handle image navigation"""
    parts = callback.data.split("_")
    product_id = int(parts[2])
    image_index = int(parts[3])
    
    # Get state data
    data = await state.get_data()
    images = data.get('product_images', [])
    
    if image_index >= len(images):
        await callback.answer("Image not found", show_alert=True)
        return
    
    with get_db() as session:
        # Get product and variants for keyboard
        product = Product.get_by_id(session, product_id)
        variants = ProductVariant.get_by_product(session, product_id)
        
        text = (
            f"🛒 {product.name}\n\n"
            f"{product.description}\n\n"
            f"📸 Image {image_index + 1} of {len(images)}\n\n"
            "Available variants:"
        )
        
        keyboard = get_product_variants_keyboard(variants, product_id, len(images))
        
        # Update the photo
        try:
            await callback.message.edit_media(
                media=InputMediaPhoto(
                    media=images[image_index],
                    caption=text
                ),
                reply_markup=keyboard
            )
            
            # Update state
            await state.update_data(current_image_index=image_index)
            await callback.answer(f"Image {image_index + 1}")
        except Exception as e:
            await callback.answer("Could not load image", show_alert=True)


@router.callback_query(F.data.startswith("variant_"))
async def process_variant_selection(callback: CallbackQuery, state: FSMContext):
    """Handle variant selection"""
    variant_id = int(callback.data.split("_")[1])
    
    with get_db() as session:
        variant = ProductVariant.get_by_id(session, variant_id)
        
        if not variant:
            await callback.answer("Variant not found", show_alert=True)
            return
        
        if variant.stock < 1:
            await callback.answer("Out of stock!", show_alert=True)
            return
        
        product = Product.get_by_id(session, variant.product_id)
        
        # Get current state data to check if we have images
        data = await state.get_data()
        has_images = 'product_images' in data and data['product_images']
        
        text = (
            f"🛒 {product.name}\n"
            f"✨ Variant: {variant.variant_name}\n\n"
            f"{product.description}\n\n"
            f"💰 Price: ${variant.price:.2f}\n"
            f"📦 In stock: {variant.stock}\n\n"
            "Add this to your cart?"
        )
        
        keyboard = get_variant_confirmation_keyboard(variant_id, product.id)
        
        if has_images:
            # If we're viewing images, edit the caption
            try:
                await callback.message.edit_caption(
                    caption=text,
                    reply_markup=keyboard
                )
            except:
                await callback.message.edit_text(text, reply_markup=keyboard)
        else:
            await callback.message.edit_text(text, reply_markup=keyboard)
        
        await state.set_state(OrderStates.selecting_variant)
    
    await callback.answer()


@router.callback_query(F.data.startswith("add_to_cart_"))
async def process_add_to_cart(callback: CallbackQuery, state: FSMContext):
    """Add variant to cart"""
    variant_id = int(callback.data.split("_")[-1])
    
    with get_db() as session:
        user = User.get_by_telegram_id(session, callback.from_user.id)
        variant = ProductVariant.get_by_id(session, variant_id)
        
        if not variant or variant.stock < 1:
            await callback.answer("Product out of stock!", show_alert=True)
            return
        
        # Add to cart
        cart_item = Cart.get_item(session, user.id, variant_id)
        
        if cart_item:
            if cart_item.quantity < variant.stock:
                cart_item.quantity += 1
            else:
                await callback.answer("Not enough stock!", show_alert=True)
                return
        else:
            Cart.add_item(session, user.id, variant_id, 1)
        
        product = Product.get_by_id(session, variant.product_id)
        await callback.answer(f"✅ {product.name} ({variant.variant_name}) added to cart!")


@router.callback_query(F.data == "back_to_categories")
async def back_to_categories(callback: CallbackQuery, state: FSMContext):
    """Go back to categories"""
    with get_db() as session:
        categories = Category.get_all(session)
        keyboard = get_categories_keyboard(categories)
        
        # Delete message if it has a photo
        try:
            await callback.message.delete()
            await callback.message.answer("🛍️ Choose a category:", reply_markup=keyboard)
        except:
            await callback.message.edit_text("🛍️ Choose a category:", reply_markup=keyboard)
        
        await state.set_state(OrderStates.browsing_categories)
    
    await callback.answer()





@router.callback_query(F.data.startswith("back_to_products_"))
async def back_to_products(callback: CallbackQuery, state: FSMContext):
    """Go back to products list in the current category"""
    product_id = int(callback.data.split("_")[-1])
    with get_db() as session:
        product = Product.get_by_id(session, product_id)
        category_id = product.category_id
        products = Product.get_by_category(session, category_id)
        category = Category.get_by_id(session, category_id)
        keyboard = get_products_keyboard(products, category_id)
        # Delete message if it has a photo
        try:
            await callback.message.delete()
            await callback.message.answer(
                f"📦 Products in {category.name}:",
                reply_markup=keyboard
            )
        except:
            await callback.message.edit_text(
                f"📦 Products in {category.name}:",
                reply_markup=keyboard
            )
        await state.set_state(OrderStates.browsing_products)
    await callback.answer()


@router.callback_query(F.data == "separator")
async def ignore_separator(callback: CallbackQuery):
    """Ignore separator button clicks"""
    await callback.answer()