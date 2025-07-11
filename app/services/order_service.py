from datetime import datetime
from decimal import Decimal
from app.models import Order, OrderItem, MenuItem
from app import db

class OrderService:
    @staticmethod
    def create_order(table, cart_items, customer_ip, user_agent):
        total_amount = Decimal('0.00')
        order_items = []
        
        # Validate and calculate total
        for item_id, quantity in cart_items.items():
            menu_item = MenuItem.query.get(int(item_id))
            if not menu_item or not menu_item.is_available:
                continue
            
            subtotal = menu_item.price * quantity
            total_amount += subtotal
            
            order_item = OrderItem(
                menu_item_id=menu_item.id,
                quantity=quantity,
                price=menu_item.price,
                subtotal=subtotal
            )
            order_items.append(order_item)
        
        if not order_items:
            return None, "Səbət boşdur"
        
        # Create order
        order = Order(
            table_id=table.id,
            restaurant_id=table.restaurant_id,
            total_amount=total_amount,
            customer_ip=customer_ip,
            user_agent=user_agent
        )
        
        db.session.add(order)
        db.session.flush()  # Get order ID
        
        # Add order items
        for item in order_items:
            item.order_id = order.id
            db.session.add(item)
        
        db.session.commit()
        return order, None
    
    @staticmethod
    def update_order_status(order_id, status):
        order = Order.query.get(order_id)
        if not order:
            return False
        
        order.status = status
        if status == 'completed':
            order.completed_at = datetime.utcnow()
        
        db.session.commit()
        return True
    
    @staticmethod
    def get_restaurant_orders(restaurant_id, status=None):
        query = Order.query.filter_by(restaurant_id=restaurant_id)
        if status:
            query = query.filter_by(status=status)
        return query.order_by(Order.created_at.desc()).all()