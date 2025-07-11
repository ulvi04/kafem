import qrcode
import os
from PIL import Image
from flask import current_app, url_for
from app.models import Table, SecurityLog
from app import db
from app.services.auth_service import AuthService

class TableService:
    @staticmethod
    def validate_table_token(table_id, token):
        table = Table.query.filter_by(id=table_id, is_active=True).first()
        
        if not table or table.token != token:
            AuthService.log_security_event(table_id, 'invalid_token_access', False)
            return None
        
        AuthService.log_security_event(table_id, 'valid_token_access', True)
        return table
    
    @staticmethod
    def generate_qr_code(table):
        qr_url = f"{current_app.config['QR_CODE_BASE_URL']}/giris/masa-{table.id}"
        
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4,
        )
        qr.add_data(qr_url)
        qr.make(fit=True)
        
        img = qr.make_image(fill_color="black", back_color="white")
        
        # Create QR code directory if it doesn't exist
        qr_dir = os.path.join(current_app.static_folder, 'images', 'qr_codes')
        os.makedirs(qr_dir, exist_ok=True)
        
        filename = f"table_{table.id}_qr.png"
        filepath = os.path.join(qr_dir, filename)
        img.save(filepath)
        
        table.qr_code_path = f"images/qr_codes/{filename}"
        db.session.commit()
        
        return filepath
    
    @staticmethod
    def create_tables_for_restaurant(restaurant_id, table_count):
        # Delete existing tables
        Table.query.filter_by(restaurant_id=restaurant_id).delete()
        
        tables = []
        for i in range(1, table_count + 1):
            table = Table(number=i, restaurant_id=restaurant_id)
            db.session.add(table)
            tables.append(table)
        
        db.session.commit()
        
        # Generate QR codes for all tables
        for table in tables:
            TableService.generate_qr_code(table)
        
        return tables