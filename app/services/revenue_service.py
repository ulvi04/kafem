from datetime import datetime, timedelta
from sqlalchemy import func, and_
from app.models import Order, Restaurant
from app import db

class RevenueService:
    @staticmethod
    def get_revenue_stats(restaurant_id=None, period='daily'):
        base_query = db.session.query(
            func.date(Order.created_at).label('date'),
            func.sum(Order.total_amount).label('revenue'),
            func.count(Order.id).label('order_count')
        ).filter(Order.status == 'completed')
        
        if restaurant_id:
            base_query = base_query.filter(Order.restaurant_id == restaurant_id)
        
        # Define date ranges
        today = datetime.now().date()
        if period == 'daily':
            start_date = today - timedelta(days=30)
        elif period == 'weekly':
            start_date = today - timedelta(weeks=12)
        else:  # monthly
            start_date = today - timedelta(days=365)
        
        base_query = base_query.filter(
            func.date(Order.created_at) >= start_date
        )
        
        results = base_query.group_by(
            func.date(Order.created_at)
        ).order_by(func.date(Order.created_at).desc()).all()
        
        return results
    
    @staticmethod
    def get_total_revenue(restaurant_id=None):
        query = db.session.query(
            func.sum(Order.total_amount).label('total_revenue'),
            func.count(Order.id).label('total_orders')
        ).filter(Order.status == 'completed')
        
        if restaurant_id:
            query = query.filter(Order.restaurant_id == restaurant_id)
        
        result = query.first()
        return {
            'total_revenue': result.total_revenue or 0,
            'total_orders': result.total_orders or 0
        }
    
    @staticmethod
    def get_restaurant_revenue_summary():
        """Get revenue summary for all restaurants (admin view)"""
        results = db.session.query(
            Restaurant.name,
            func.sum(Order.total_amount).label('revenue'),
            func.count(Order.id).label('order_count')
        ).join(Order).filter(
            Order.status == 'completed'
        ).group_by(Restaurant.id).all()
        
        return results