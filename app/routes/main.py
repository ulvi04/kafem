from flask import Blueprint, render_template, redirect, url_for, session, request, abort
from app.services.table_service import TableService
from app import limiter

main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def index():
    return render_template('index.html')

@main_bp.route('/giris/masa-<int:table_id>')
@limiter.limit("10 per minute")
def table_entry(table_id):
    """QR code entry point - validates table and sets token in session"""
    table = TableService.validate_table_token(table_id, request.args.get('token', ''))
    
    if not table:
        # For QR codes, we need to get the token from the table
        from app.models import Table
        table = Table.query.filter_by(id=table_id, is_active=True).first()
        if not table:
            abort(404)
        
        # Store token in session for secure access
        session[f'table_{table_id}_token'] = table.token
        session.permanent = True
        
        return redirect(url_for('customer.menu', table_id=table_id))
    
    abort(403)