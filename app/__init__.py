from flask import Flask, render_template
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
    
    # Error handlers
    @app.errorhandler(400)
    def bad_request(error):
        return render_template('error/400.html'), 400
    
    @app.errorhandler(401)
    def bad_request(error):
        return render_template('error/401.html'), 401
    
    @app.errorhandler(403)
    def forbidden(error):
        return render_template('error/403.html'), 403
    
    @app.errorhandler(404)
    def page_not_found(error):
        return render_template('error/404.html'), 404
    
    @app.errorhandler(429)
    def page_not_found(error):
        return render_template('error/429.html'), 429
    
    @app.errorhandler(500)
    def internal_server_error(error):
        return render_template('error/500.html'), 500
    
    @app.errorhandler(503)
    def service_unavailable(error):
        return render_template('error/503.html'), 503
    
    return app