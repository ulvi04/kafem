from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_migrate import Migrate
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from config.config import Config

db = SQLAlchemy()
login_manager = LoginManager()
migrate = Migrate()
limiter = Limiter(
    key_func=get_remote_address,
    default_limits=["1000 per hour"]
)

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    
    # Initialize extensions
    db.init_app(app)
    login_manager.init_app(app)
    migrate.init_app(app, db)
    limiter.init_app(app)
    
    login_manager.login_view = 'auth.login'
    login_manager.login_message = 'Zəhmət olmasa giriş edin.'
    login_manager.login_message_category = 'info'
    
    # Import models
    from app.models import User, Restaurant, Table, MenuItem, Order, OrderItem
    
    # Register blueprints
    from app.routes.auth import auth_bp
    from app.routes.admin import admin_bp
    from app.routes.restaurant import restaurant_bp
    from app.routes.waiter import waiter_bp
    from app.routes.customer import customer_bp
    from app.routes.main import main_bp
    
    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(admin_bp, url_prefix='/admin')
    app.register_blueprint(restaurant_bp, url_prefix='/restaurant')
    app.register_blueprint(waiter_bp, url_prefix='/waiter')
    app.register_blueprint(customer_bp, url_prefix='/customer')
    app.register_blueprint(main_bp)
    
    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))
    
    return app