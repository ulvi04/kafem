from functools import wraps
from flask import abort, session, request
from flask_login import current_user
from app.services.table_service import TableService

def role_required(role):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not current_user.is_authenticated or current_user.role != role:
                abort(403)
            return f(*args, **kwargs)
        return decorated_function
    return decorator

def restaurant_access_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        restaurant_id = kwargs.get('restaurant_id')
        if not restaurant_id:
            abort(400)
        
        if not current_user.can_access_restaurant(restaurant_id):
            abort(403)
        
        return f(*args, **kwargs)
    return decorated_function

def table_token_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        table_id = kwargs.get('table_id')
        token = session.get(f'table_{table_id}_token')
        
        if not token:
            abort(403)
        
        table = TableService.validate_table_token(table_id, token)
        if not table:
            abort(403)
        
        kwargs['table'] = table
        return f(*args, **kwargs)
    return decorated_function