from flask import request
from app.models import User, SecurityLog
from app import db

class AuthService:
    @staticmethod
    def create_user(username, email, password, role, restaurant_id=None):
        if User.query.filter_by(username=username).first():
            return None, "İstifadəçi adı artıq mövcuddur"
        
        if User.query.filter_by(email=email).first():
            return None, "E-poçt ünvanı artıq mövcuddur"
        
        user = User(
            username=username,
            email=email,
            role=role,
            restaurant_id=restaurant_id
        )
        user.set_password(password)
        
        db.session.add(user)
        db.session.commit()
        
        return user, None
    
    @staticmethod
    def authenticate_user(username, password):
        user = User.query.filter_by(username=username, is_active=True).first()
        
        if user and user.check_password(password):
            AuthService.log_security_event(None, 'login_success', True)
            return user
        
        AuthService.log_security_event(None, 'login_failed', False)
        return None
    
    @staticmethod
    def log_security_event(table_id, action, success):
        log = SecurityLog(
            table_id=table_id,
            ip_address=request.remote_addr,
            user_agent=request.headers.get('User-Agent'),
            action=action,
            success=success
        )
        db.session.add(log)
        db.session.commit()