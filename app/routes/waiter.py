from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify, abort
from flask_login import login_required, current_user
from app.models import Order, OrderItem, Restaurant
from app.services.order_service import OrderService
from app.utils.decorators import role_required
from app import db

waiter_bp = Blueprint('waiter', __name__)

@waiter_bp.route('/dashboard')
@login_required
@role_required('ofisiant')
def dashboard():
    restaurant = Restaurant.query.get(current_user.restaurant_id)
    
    # Get pending and preparing orders
    pending_orders = Order.query.filter_by(
        restaurant_id=current_user.restaurant_id,
        status='pending'
    ).order_by(Order.created_at.asc()).all()
    
    preparing_orders = Order.query.filter_by(
        restaurant_id=current_user.restaurant_id,
        status='preparing'
    ).order_by(Order.created_at.asc()).all()
    
    return render_template('waiter/dashboard.html', 
                         restaurant=restaurant,
                         pending_orders=pending_orders,
                         preparing_orders=preparing_orders)

@waiter_bp.route('/orders')
@login_required
@role_required('ofisiant')
def orders():
    status = request.args.get('status', 'all')
    
    query = Order.query.filter_by(restaurant_id=current_user.restaurant_id)
    if status != 'all':
        query = query.filter_by(status=status)
    
    orders = query.order_by(Order.created_at.desc()).all()
    
    return render_template('waiter/orders.html', orders=orders, current_status=status)

@waiter_bp.route('/orders/<int:order_id>')
@login_required
@role_required('ofisiant')
def order_detail(order_id):
    order = Order.query.filter_by(
        id=order_id,
        restaurant_id=current_user.restaurant_id
    ).first_or_404()
    
    return render_template('waiter/order_detail.html', order=order)

@waiter_bp.route('/orders/<int:order_id>/update-status', methods=['POST'])
@login_required
@role_required('ofisiant')
def update_order_status(order_id):
    order = Order.query.filter_by(
        id=order_id,
        restaurant_id=current_user.restaurant_id
    ).first_or_404()
    
    new_status = request.form.get('status')
    valid_statuses = ['pending', 'preparing', 'ready', 'completed']
    
    if new_status in valid_statuses:
        success = OrderService.update_order_status(order_id, new_status)
        if success:
            flash(f'Sifariş statusu {new_status} olaraq yeniləndi', 'success')
        else:
            flash('Xəta baş verdi', 'error')
    else:
        flash('Yanlış status', 'error')
    
    return redirect(url_for('waiter.order_detail', order_id=order_id))

@waiter_bp.route('/api/orders/status', methods=['GET'])
@login_required
@role_required('ofisiant')
def api_orders_status():
    """API endpoint for real-time order updates"""
    pending_count = Order.query.filter_by(
        restaurant_id=current_user.restaurant_id,
        status='pending'
    ).count()
    
    preparing_count = Order.query.filter_by(
        restaurant_id=current_user.restaurant_id,
        status='preparing'
    ).count()
    
    return jsonify({
        'pending': pending_count,
        'preparing': preparing_count
    })

# Block access to revenue-related endpoints for waiters
@waiter_bp.route('/revenue')
@waiter_bp.route('/revenue/<path:path>')
def block_revenue_access(path=None):
    """Block all revenue access for waiters"""
    abort(403)