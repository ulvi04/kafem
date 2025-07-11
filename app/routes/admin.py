from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_required, current_user
from app.models import Restaurant, User, Table
from app.services.auth_service import AuthService
from app.services.table_service import TableService
from app.services.revenue_service import RevenueService
from app.utils.decorators import role_required
from app.utils.file_utils import save_image
from app import db

admin_bp = Blueprint('admin', __name__)

@admin_bp.route('/dashboard')
@login_required
@role_required('admin')
def dashboard():
    restaurants = Restaurant.query.filter_by(is_active=True).all()
    revenue_summary = RevenueService.get_restaurant_revenue_summary()
    total_stats = RevenueService.get_total_revenue()
    
    return render_template('admin/dashboard.html', 
                         restaurants=restaurants,
                         revenue_summary=revenue_summary,
                         total_stats=total_stats)

@admin_bp.route('/restaurants')
@login_required
@role_required('admin')
def restaurants():
    restaurants = Restaurant.query.all()
    return render_template('admin/restaurants.html', restaurants=restaurants)

@admin_bp.route('/restaurants/create', methods=['GET', 'POST'])
@login_required
@role_required('admin')
def create_restaurant():
    if request.method == 'POST':
        name = request.form['name']
        address = request.form.get('address', '')
        phone = request.form.get('phone', '')
        table_count = int(request.form.get('table_count', 10))
        
        restaurant = Restaurant(
            name=name,
            address=address,
            phone=phone,
            table_count=table_count
        )
        
        # Handle logo upload
        if 'logo' in request.files:
            logo_file = request.files['logo']
            if logo_file.filename:
                logo_path = save_image(logo_file, 'logos')
                restaurant.logo = logo_path
        
        db.session.add(restaurant)
        db.session.commit()
        
        # Create tables
        TableService.create_tables_for_restaurant(restaurant.id, table_count)
        
        flash('Restoran uğurla yaradıldı', 'success')
        return redirect(url_for('admin.restaurants'))
    
    return render_template('admin/create_restaurant.html')

@admin_bp.route('/restaurants/<int:restaurant_id>/edit', methods=['GET', 'POST'])
@login_required
@role_required('admin')
def edit_restaurant(restaurant_id):
    restaurant = Restaurant.query.get_or_404(restaurant_id)
    
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
                logo_path = save_image(logo_file, 'logos')
                restaurant.logo = logo_path
        
        db.session.commit()
        flash('Restoran məlumatları yeniləndi', 'success')
        return redirect(url_for('admin.restaurants'))
    
    return render_template('admin/edit_restaurant.html', restaurant=restaurant)

@admin_bp.route('/restaurants/<int:restaurant_id>/delete', methods=['POST'])
@login_required
@role_required('admin')
def delete_restaurant(restaurant_id):
    restaurant = Restaurant.query.get_or_404(restaurant_id)
    
    try:
        # First delete all tables associated with the restaurant
        Table.query.filter_by(restaurant_id=restaurant_id).delete()
        
        # Then delete the restaurant itself
        db.session.delete(restaurant)
        db.session.commit()
        
        flash('Restoran və ona aid bütün masalar uğurla silindi', 'success')
    except Exception as e:
        db.session.rollback()
        flash('Restoran silinərkən xəta baş verdi: ' + str(e), 'error')
    
    return redirect(url_for('admin.restaurants'))

@admin_bp.route('/users')
@login_required
@role_required('admin')
def users():
    users = User.query.all()
    restaurants = Restaurant.query.filter_by(is_active=True).all()
    return render_template('admin/users.html', users=users, restaurants=restaurants)

@admin_bp.route('/users/create', methods=['POST'])
@login_required
@role_required('admin')
def create_user():
    username = request.form['username']
    email = request.form['email']
    password = request.form['password']
    role = request.form['role']
    restaurant_id = request.form.get('restaurant_id') or None
    
    user, error = AuthService.create_user(username, email, password, role, restaurant_id)
    
    if user:
        flash('İstifadəçi uğurla yaradıldı', 'success')
    else:
        flash(error, 'error')
    
    return redirect(url_for('admin.users'))

@admin_bp.route('/users/<int:user_id>/delete', methods=['POST'])
@login_required
@role_required('admin')
def delete_user(user_id):
    # Prevent admin from deleting themselves
    if current_user.id == user_id:
        flash('Öz hesabınızı silə bilməzsiniz', 'error')
        return redirect(url_for('admin.users'))
    
    user = User.query.get_or_404(user_id)
    
    try:
        db.session.delete(user)
        db.session.commit()
        flash('İstifadəçi uğurla silindi', 'success')
    except Exception as e:
        db.session.rollback()
        flash('İstifadəçi silinərkən xəta baş verdi', 'error')
    
    return redirect(url_for('admin.users'))

@admin_bp.route('/tables/<int:restaurant_id>')
@login_required
@role_required('admin')
def tables(restaurant_id):
    restaurant = Restaurant.query.get_or_404(restaurant_id)
    tables = Table.query.filter_by(restaurant_id=restaurant_id).all()
    return render_template('admin/tables.html', restaurant=restaurant, tables=tables)

@admin_bp.route('/tables/<int:table_id>/regenerate-token', methods=['POST'])
@login_required
@role_required('admin')
def regenerate_table_token(table_id):
    table = Table.query.get_or_404(table_id)
    table.generate_token()
    TableService.generate_qr_code(table)
    db.session.commit()
    
    flash('Masa tokeni yeniləndi', 'success')
    return redirect(url_for('admin.tables', restaurant_id=table.restaurant_id))

@admin_bp.route('/revenue')
@login_required
@role_required('admin')
def revenue():
    period = request.args.get('period', 'daily')
    revenue_stats = RevenueService.get_revenue_stats(period=period)
    total_stats = RevenueService.get_total_revenue()
    
    return render_template('admin/revenue.html', 
                         revenue_stats=revenue_stats,
                         total_stats=total_stats,
                         period=period)