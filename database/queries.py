from sqlalchemy.orm import Session
from database.models import User, Category, Product, ProductVariant, CartItem, Order, OrderItem
from datetime import datetime


class UserRepository:
    """User database operations"""
    
    @staticmethod
    def get_by_telegram_id(session: Session, telegram_id: int):
        return session.query(User).filter(User.telegram_id == telegram_id).first()
    
    @staticmethod
    def create(session: Session, telegram_id: int, phone_number: str, username=None, first_name=None, last_name=None):
        user = User(
            telegram_id=telegram_id,
            phone_number=phone_number,
            username=username,
            first_name=first_name,
            last_name=last_name
        )
        session.add(user)
        session.commit()
        return user


class CategoryRepository:
    """Category database operations"""
    
    @staticmethod
    def get_all_active(session: Session):
        return session.query(Category).filter(Category.is_active == True).order_by(Category.order, Category.name).all()
    
    @staticmethod
    def get_by_id(session: Session, category_id: int):
        return session.query(Category).filter(Category.id == category_id).first()


class ProductRepository:
    """Product database operations"""
    
    @staticmethod
    def get_by_category(session: Session, category_id: int):
        return session.query(Product).filter(
            Product.category_id == category_id,
            Product.is_active == True
        ).order_by(Product.order, Product.name).all()
    
    @staticmethod
    def get_by_id(session: Session, product_id: int):
        return session.query(Product).filter(Product.id == product_id).first()


class VariantRepository:
    """Product variant database operations"""
    
    @staticmethod
    def get_by_product(session: Session, product_id: int):
        return session.query(ProductVariant).filter(
            ProductVariant.product_id == product_id,
            ProductVariant.is_active == True
        ).order_by(ProductVariant.order, ProductVariant.name).all()
    
    @staticmethod
    def get_by_id(session: Session, variant_id: int):
        return session.query(ProductVariant).filter(ProductVariant.id == variant_id).first()


class CartRepository:
    """Shopping cart database operations"""
    
    @staticmethod
    def get_user_cart(session: Session, user_id: int):
        return session.query(CartItem).filter(CartItem.user_id == user_id).all()
    
    @staticmethod
    def add_item(session: Session, user_id: int, variant_id: int):
        """Add item to cart or increase quantity if already exists"""
        cart_item = session.query(CartItem).filter(
            CartItem.user_id == user_id,
            CartItem.variant_id == variant_id
        ).first()
        
        if cart_item:
            cart_item.quantity += 1
        else:
            cart_item = CartItem(user_id=user_id, variant_id=variant_id, quantity=1)
            session.add(cart_item)
        
        session.commit()
        return cart_item
    
    @staticmethod
    def clear_cart(session: Session, user_id: int):
        session.query(CartItem).filter(CartItem.user_id == user_id).delete()
        session.commit()
    
    @staticmethod
    def get_cart_total(session: Session, user_id: int):
        cart_items = CartRepository.get_user_cart(session, user_id)
        total = sum(item.quantity * item.variant.price for item in cart_items)
        return total


class OrderRepository:
    """Order database operations"""
    
    @staticmethod
    def create_order(session: Session, user_id: int, cart_items, note=None, 
                    location_lat=None, location_lon=None, location_address=None):
        """Create order from cart items"""
        total = sum(item.quantity * item.variant.price for item in cart_items)
        
        order = Order(
            user_id=user_id,
            total_amount=total,
            note=note,
            location_latitude=location_lat,
            location_longitude=location_lon,
            location_address=location_address,
            status='pending'
        )
        session.add(order)
        session.flush()  # Get order ID
        
        # Create order items
        for cart_item in cart_items:
            order_item = OrderItem(
                order_id=order.id,
                variant_id=cart_item.variant_id,
                quantity=cart_item.quantity,
                price_at_purchase=cart_item.variant.price,
                variant_name=cart_item.variant.name,
                product_name=cart_item.variant.product.name
            )
            session.add(order_item)
        
        session.commit()
        return order
    
    @staticmethod
    def get_by_id(session: Session, order_id: int):
        return session.query(Order).filter(Order.id == order_id).first()
    
    @staticmethod
    def update_status(session: Session, order_id: int, status: str):
        order = OrderRepository.get_by_id(session, order_id)
        if order:
            order.status = status
            if status == 'confirmed':
                order.confirmed_at = datetime.utcnow()
            session.commit()
        return order
    
    @staticmethod
    def update_message_ids(session: Session, order_id: int, admin_msg_id=None, channel_msg_id=None):
        order = OrderRepository.get_by_id(session, order_id)
        if order:
            if admin_msg_id:
                order.admin_message_id = admin_msg_id
            if channel_msg_id:
                order.channel_message_id = channel_msg_id
            session.commit()
        return order
    
    @staticmethod
    def get_user_orders(session: Session, user_id: int):
        return session.query(Order).filter(Order.user_id == user_id).order_by(Order.created_at.desc()).all()