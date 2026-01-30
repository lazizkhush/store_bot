from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, InputMediaPhoto
from aiogram.fsm.context import FSMContext

from database import get_session, CategoryRepository, ProductRepository, VariantRepository, CartRepository
from utils import (
    get_categories_keyboard,
    get_products_keyboard,
    get_variants_keyboard,
    format_variant_caption
)
from config import Messages

router = Router()


@router.message(F.text == "🛍 Browse Categories")
async def show_categories(message: Message):
    """Show all available categories"""
    session = get_session()
    try:
        categories = CategoryRepository.get_all_active(session)
        
        if not categories:
            await message.answer(Messages.NO_CATEGORIES)
            return
        
        await message.answer(
            Messages.SELECT_CATEGORY,
            reply_markup=get_categories_keyboard(categories)
        )
    finally:
        session.close()


@router.callback_query(F.data.startswith("cat_"))
async def show_category_products(callback: CallbackQuery):
    """Show products in selected category"""
    category_id = int(callback.data.split("_")[1])
    
    session = get_session()
    try:
        category = CategoryRepository.get_by_id(session, category_id)
        products = ProductRepository.get_by_category(session, category_id)
        
        if not products:
            await callback.answer(Messages.NO_PRODUCTS, show_alert=True)
            return
        
        await callback.message.edit_text(
            f"📦 <b>{category.name}</b>\n\n{Messages.SELECT_PRODUCT}",
            reply_markup=get_products_keyboard(products, category_id),
            parse_mode="HTML"
        )
        await callback.answer()
    finally:
        session.close()


@router.callback_query(F.data.startswith("prod_"))
async def show_product_variants(callback: CallbackQuery):
    """Show product variants with images"""
    product_id = int(callback.data.split("_")[1])
    
    session = get_session()
    try:
        product = ProductRepository.get_by_id(session, product_id)
        variants = VariantRepository.get_by_product(session, product_id)
        
        if not variants:
            await callback.answer(Messages.NO_VARIANTS, show_alert=True)
            return
        
        # Delete previous message
        await callback.message.delete()
        
        # Prepare media group with variant images
        media_group = []
        for idx, variant in enumerate(variants, 1):
            caption = format_variant_caption(variant, idx) if idx == 1 else None
            
            if variant.image_file_id:
                media_group.append(
                    InputMediaPhoto(
                        media=variant.image_file_id,
                        caption=caption,
                        parse_mode="HTML"
                    )
                )
        
        # Send media group if images exist
        if media_group:
            await callback.message.answer_media_group(media_group)
        else:
            # No images, just send text
            text = f"<b>{product.name}</b>\n\n"
            for idx, variant in enumerate(variants, 1):
                text += format_variant_caption(variant, idx) + "\n\n"
            await callback.message.answer(text, parse_mode="HTML")
        
        # Send variants keyboard
        await callback.message.answer(
            "Choose a variant to add to cart:",
            reply_markup=get_variants_keyboard(variants, product_id)
        )
        
        await callback.answer()
    finally:
        session.close()


@router.callback_query(F.data.startswith("addvar_"))
async def add_variant_to_cart(callback: CallbackQuery):
    """Add variant to cart"""
    variant_id = int(callback.data.split("_")[1])
    user_id = callback.from_user.id
    
    session = get_session()
    try:
        from database import UserRepository
        
        # Check if user exists
        user = UserRepository.get_by_telegram_id(session, user_id)
        if not user:
            await callback.answer("❌ Please register first by using /start", show_alert=True)
            return
        
        # Add to cart
        CartRepository.add_item(session, user.id, variant_id)
        
        await callback.answer(Messages.ITEM_ADDED, show_alert=False)
        
    except Exception as e:
        await callback.answer(f"❌ Error: {str(e)}", show_alert=True)
    finally:
        session.close()


@router.callback_query(F.data.startswith("backprod_"))
async def back_to_products(callback: CallbackQuery):
    """Go back to products list"""
    product_id = int(callback.data.split("_")[1])
    
    session = get_session()
    try:
        product = ProductRepository.get_by_id(session, product_id)
        if product:
            products = ProductRepository.get_by_category(session, product.category_id)
            category = product.category
            
            await callback.message.edit_text(
                f"📦 <b>{category.name}</b>\n\n{Messages.SELECT_PRODUCT}",
                reply_markup=get_products_keyboard(products, product.category_id),
                parse_mode="HTML"
            )
        await callback.answer()
    finally:
        session.close()


@router.callback_query(F.data == "back_categories")
async def back_to_categories(callback: CallbackQuery):
    """Go back to categories list"""
    session = get_session()
    try:
        categories = CategoryRepository.get_all_active(session)
        
        await callback.message.edit_text(
            Messages.SELECT_CATEGORY,
            reply_markup=get_categories_keyboard(categories)
        )
        await callback.answer()
    finally:
        session.close()