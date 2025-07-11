from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from app.models import Restaurant, MenuItem, User, Table
from app.services.auth_service import AuthService
from app.services.table_service import TableService
from app.services.revenue_service import RevenueService
from app.utils.decorators import role_required, restaurant_access_required
from app.utils.file_utils import save_image, delete_image
from app import db

restaurant_bp = Blueprint('restaurant', __name__)

@restaurant_bp.route('/dashboard')
@login_required
@role_required('restoran_sahibi')
def dashboard():
    restaurant = Restaurant.query.get(current_user.restaurant_id)
    if not restaurant:
        flash('Restoran tapılmadı', 'error')
        return redirect(url_for('main.index'))
    
    revenue_stats = RevenueService.get_total_revenue(restaurant.id)
    return render_template('restaurant/dashboard.html', 
                         restaurant=restaurant,
                         revenue_stats=revenue_stats)

@restaurant_bp.route('/menu')
@login_required
@role_required('restoran_sahibi')
def menu():
    restaurant = Restaurant.query.get(current_user.restaurant_id)
    menu_items = MenuItem.query.filter_by(restaurant_id=restaurant.id).all()
    return render_template('restaurant/menu.html', 
                         restaurant=restaurant,
                         menu_items=menu_items)

@restaurant_bp.route('/menu/create', methods=['GET', 'POST'])
@login_required
@role_required('restoran_sahibi')
def create_menu_item():
    if request.method == 'POST':
        name = request.form['name']
        description = request.form.get('description', '')
        price = float(request.form['price'])
        category = request.form.get('category', '')
        
        menu_item = MenuItem(
            name=name,
            description=description,
            price=price,
            category=category,
            restaurant_id=current_user.restaurant_id
        )
        
        # Handle image upload
        if 'image' in request.files:
            image_file = request.files['image']
            if image_file.filename:
                image_path = save_image(image_file, 'menu')
                menu_item.image = image_path
        
        db.session.add(menu_item)
        db.session.commit()
        
        flash('Menyu elementi əlavə edildi', 'success')
        return redirect(url_for('restaurant.menu'))
    
    return render_template('restaurant/create_menu_item.html')

@restaurant_bp.route('/menu/<int:item_id>/edit', methods=['GET', 'POST'])
@login_required
@role_required('restoran_sahibi')
def edit_menu_item(item_id):
    menu_item = MenuItem.query.filter_by(
        id=item_id, 
        restaurant_id=current_user.restaurant_id
    ).first_or_404()
    
    if request.method == 'POST':
        menu_item.name = request.form['name']
        menu_item.description = request.form.get('description', '')
        menu_item.price = float(request.form['price'])
        menu_item.category = request.form.get('category', '')
        menu_item.is_available = 'is_available' in request.form
        
        # Handle image upload
        if 'image' in request.files:
            image_file = request.files['image']
            if image_file.filename:
                # Delete old image
                if menu_item.image:
                    delete_image(menu_item.image)
                
                image_path = save_image(image_file, 'menu')
                menu_item.image = image_path
        
        db.session.commit()
        flash('Menyu elementi yeniləndi', 'success')
        return redirect(url_for('restaurant.menu'))
    
    return render_template('restaurant/edit_menu_item.html', menu_item=menu_item)

@restaurant_bp.route('/menu/<int:item_id>/delete', methods=['POST'])
@login_required
@role_required('restoran_sahibi')
def delete_menu_item(item_id):
    menu_item = MenuItem.query.filter_by(
        id=item_id, 
        restaurant_id=current_user.restaurant_id
    ).first_or_404()
    
    # Delete image
    if menu_item.image:
        delete_image(menu_item.image)
    
    db.session.delete(menu_item)
    db.session.commit()
    
    flash('Menyu elementi silindi', 'success')
    return redirect(url_for('restaurant.menu'))

@restaurant_bp.route('/tables')
@login_required
@role_required('restoran_sahibi')
def tables():
    restaurant = Restaurant.query.get(current_user.restaurant_id)
    tables = Table.query.filter_by(restaurant_id=restaurant.id).all()
    return render_template('restaurant/tables.html', 
                         restaurant=restaurant,
                         tables=tables)

@restaurant_bp.route('/settings', methods=['GET', 'POST'])
@login_required
@role_required('restoran_sahibi')
def settings():
    restaurant = Restaurant.query.get(current_user.restaurant_id)
    
    if request.method == 'POST':
        restaurant.name = request.form['name']
        restaurant.address = request.form.get('address', '')
        restaurant.phone = request.form.get('phone', '')
        
        new_table_count = int(request.form.get('table_count', 10))
        if new_table_count != restaurant.table_count:
            restaurant.table_count = new_table_count
            TableService.create_tables_for_restaurant(restaurant.id, new_table_count)
        
        # Handle logo upload
        if 'logo' in request.files:
            logo_file = request.files['logo']
            if logo_file.filename:
                # Delete old logo
                if restaurant.logo:
                    delete_image(restaurant.logo)
                
                logo_path = save_image(logo_file, 'logos')
                restaurant.logo = logo_path
        
        db.session.commit()
        flash('Restoran parametrləri yeniləndi', 'success')
        return redirect(url_for('restaurant.settings'))
    
    return render_template('restaurant/settings.html', restaurant=restaurant)

@restaurant_bp.route('/staff')
@login_required
@role_required('restoran_sahibi')
def staff():
    staff_members = User.query.filter_by(
        restaurant_id=current_user.restaurant_id,
        role='ofisiant'
    ).all()
    return render_template('restaurant/staff.html', staff_members=staff_members)

@restaurant_bp.route('/staff/create', methods=['POST'])
@login_required
@role_required('restoran_sahibi')
def create_staff():
    username = request.form['username']
    email = request.form['email']
    password = request.form['password']
    
    user, error = AuthService.create_user(
        username, email, password, 'ofisiant', current_user.restaurant_id
    )
    
    if user:
        flash('Ofisiant uğurla əlavə edildi', 'success')
    else:
        flash(error, 'error')
    
    return redirect(url_for('restaurant.staff'))

@restaurant_bp.route('/revenue')
@login_required
@role_required('restoran_sahibi')
def revenue():
    period = request.args.get('period', 'daily')
    revenue_stats = RevenueService.get_revenue_stats(
        restaurant_id=current_user.restaurant_id, 
        period=period
    )
    total_stats = RevenueService.get_total_revenue(current_user.restaurant_id)
    
    return render_template('restaurant/revenue.html', 
                         revenue_stats=revenue_stats,
                         total_stats=total_stats,
                         period=period)