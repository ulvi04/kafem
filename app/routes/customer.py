from flask import Blueprint, render_template, request, redirect, url_for, flash, session, jsonify
from app.models import Restaurant, MenuItem, Order
from app.services.table_service import TableService
from app.services.order_service import OrderService
from app.utils.decorators import table_token_required
from app import limiter

customer_bp = Blueprint('customer', __name__)

@customer_bp.route('/masa/<int:table_id>')
@limiter.limit("20 per minute")
@table_token_required
def menu(table_id, table):
    """Customer menu page - token protected"""
    restaurant = table.restaurant
    menu_items = MenuItem.query.filter_by(
        restaurant_id=restaurant.id,
        is_available=True
    ).order_by(MenuItem.category, MenuItem.name).all()
    
    # Group items by category
    categories = {}
    for item in menu_items:
        cat = item.category or 'Digər'
        if cat not in categories:
            categories[cat] = []
        categories[cat].append(item)
    
    return render_template('customer/menu.html', 
                         table=table,
                         restaurant=restaurant,
                         categories=categories)

@customer_bp.route('/masa/<int:table_id>/cart')
@limiter.limit("10 per minute")
@table_token_required
def cart(table_id, table):
    """Shopping cart page"""
    cart_items = session.get('cart', {})
    
    # Get menu items for cart
    cart_details = []
    total = 0
    
    for item_id, quantity in cart_items.items():
        menu_item = MenuItem.query.get(int(item_id))
        if menu_item and menu_item.is_available:
            subtotal = menu_item.price * quantity
            cart_details.append({
                'item': menu_item,
                'quantity': quantity,
                'subtotal': subtotal
            })
            total += subtotal
    
    return render_template('customer/cart.html',
                         table=table,
                         restaurant=table.restaurant,
                         cart_details=cart_details,
                         total=total)

@customer_bp.route('/masa/<int:table_id>/add-to-cart', methods=['POST'])
@limiter.limit("30 per minute")
@table_token_required
def add_to_cart(table_id, table):
    """Add item to cart via AJAX"""
    item_id = request.json.get('item_id')
    quantity = int(request.json.get('quantity', 1))
    
    if not item_id or quantity <= 0:
        return jsonify({'success': False, 'message': 'Yanlış məlumat'})
    
    # Verify item belongs to restaurant
    menu_item = MenuItem.query.filter_by(
        id=item_id,
        restaurant_id=table.restaurant_id,
        is_available=True
    ).first()
    
    if not menu_item:
        return jsonify({'success': False, 'message': 'Məhsul tapılmadı'})
    
    # Update cart in session
    cart = session.get('cart', {})
    cart[str(item_id)] = cart.get(str(item_id), 0) + quantity
    session['cart'] = cart
    session.permanent = True
    
    cart_count = sum(cart.values())
    
    return jsonify({
        'success': True,
        'message': 'Səbətə əlavə edildi',
        'cart_count': cart_count
    })

@customer_bp.route('/masa/<int:table_id>/update-cart', methods=['POST'])
@limiter.limit("20 per minute")
@table_token_required
def update_cart(table_id, table):
    """Update cart quantities"""
    cart_updates = request.json
    
    cart = session.get('cart', {})
    for item_id, quantity in cart_updates.items():
        if quantity <= 0:
            cart.pop(item_id, None)
        else:
            cart[item_id] = quantity
    
    session['cart'] = cart
    session.permanent = True
    
    return jsonify({'success': True})

@customer_bp.route('/masa/<int:table_id>/checkout', methods=['POST'])
@limiter.limit("5 per minute")
@table_token_required
def checkout(table_id, table):
    """Process order"""
    cart_items = session.get('cart', {})
    
    if not cart_items:
        flash('Səbət boşdur', 'error')
        return redirect(url_for('customer.cart', table_id=table_id))
    
    # Create order
    order, error = OrderService.create_order(
        table=table,
        cart_items=cart_items,
        customer_ip=request.remote_addr,
        user_agent=request.headers.get('User-Agent')
    )
    
    if error:
        flash(error, 'error')
        return redirect(url_for('customer.cart', table_id=table_id))
    
    # Clear cart
    session.pop('cart', None)
    
    flash('Sifarişiniz qəbul edildi', 'success')
    return redirect(url_for('customer.receipt', table_id=table_id, order_id=order.id))

@customer_bp.route('/masa/<int:table_id>/receipt/<int:order_id>')
@limiter.limit("10 per minute")
@table_token_required
def receipt(table_id, order_id, table):
    """Order receipt page"""
    order = Order.query.filter_by(
        id=order_id,
        table_id=table_id
    ).first_or_404()
    
    return render_template('customer/receipt.html',
                         table=table,
                         restaurant=table.restaurant,
                         order=order)

@customer_bp.route('/masa/<int:table_id>/orders')
@limiter.limit("10 per minute")
@table_token_required
def orders(table_id, table):
    """Customer's orders history"""
    orders = Order.query.filter_by(table_id=table_id).order_by(
        Order.created_at.desc()
    ).limit(10).all()
    
    return render_template('customer/orders.html',
                         table=table,
                         restaurant=table.restaurant,
                         orders=orders)