import os
import uuid
from PIL import Image
from flask import current_app
from werkzeug.utils import secure_filename

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def save_image(file, folder='menu'):
    if not file or not allowed_file(file.filename):
        return None
    
    # Generate unique filename
    filename = str(uuid.uuid4()) + '.' + file.filename.rsplit('.', 1)[1].lower()
    
    # Create folder if not exists
    upload_path = os.path.join(current_app.static_folder, 'images', 'uploads', folder)
    os.makedirs(upload_path, exist_ok=True)
    
    filepath = os.path.join(upload_path, filename)
    
    # Resize and save image
    try:
        image = Image.open(file)
        image.thumbnail((800, 600), Image.Resampling.LANCZOS)
        image.save(filepath, optimize=True, quality=85)
        
        return f"images/uploads/{folder}/{filename}"
    except Exception as e:
        return None

def delete_image(image_path):
    if image_path:
        full_path = os.path.join(current_app.static_folder, image_path)
        if os.path.exists(full_path):
            os.remove(full_path)