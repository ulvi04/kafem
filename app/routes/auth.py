from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_user, logout_user, login_required, current_user
from app.services.auth_service import AuthService
from app import limiter

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/login', methods=['GET', 'POST'])
@limiter.limit("5 per minute")
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        user = AuthService.authenticate_user(username, password)
        if user:
            login_user(user, remember=True)
            
            # Redirect based on role
            if user.role == 'admin':
                return redirect(url_for('admin.dashboard'))
            elif user.role == 'restoran_sahibi':
                return redirect(url_for('restaurant.dashboard'))
            else:  # ofisiant
                return redirect(url_for('waiter.dashboard'))
        else:
            flash('Yanlış istifadəçi adı və ya parol', 'error')
    
    return render_template('auth/login.html')

@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Uğurla çıxış etdiniz', 'success')
    return redirect(url_for('main.index'))