# wsgi.py

from app import create_app, db
from app.models import User, Restaurant, Table, MenuItem, Order, OrderItem, SecurityLog
from app.services.table_service import TableService
import os

app = create_app()

def initialize_data():
    with app.app_context():
        db.create_all()

        admin = User.query.filter_by(username='admin').first()
        if not admin:
            admin = User(
                username='admin',
                email='admin@Kafem.az',
                role='admin'
            )
            admin.set_password('admin123')
            db.session.add(admin)
            print("✅ Admin user created: admin/admin123")

        restaurant = Restaurant.query.filter_by(name='Nəmunə Restoran').first()
        if not restaurant:
            restaurant = Restaurant(
                name='Nəmunə Restoran',
                address='Bakı şəhəri, Nizami küçəsi 1',
                phone='+994-12-555-0000',
                table_count=5
            )
            db.session.add(restaurant)
            db.session.flush()

            owner = User(
                username='restoran1',
                email='restoran1@Kafem.az',
                role='restoran_sahibi',
                restaurant_id=restaurant.id
            )
            owner.set_password('restoran123')
            db.session.add(owner)

            waiter = User(
                username='ofisiant1',
                email='ofisiant1@Kafem.az',
                role='ofisiant',
                restaurant_id=restaurant.id
            )
            waiter.set_password('ofisiant123')
            db.session.add(waiter)

            print("✅ Restoran sahibi və ofisiant yaradıldı.")

            existing_tables = Table.query.filter_by(restaurant_id=restaurant.id).count()
            if existing_tables == 0:
                TableService.create_tables_for_restaurant(restaurant.id, restaurant.table_count)
                print(f"✅ {restaurant.table_count} masa yaradıldı.")

            existing_items = MenuItem.query.filter_by(restaurant_id=restaurant.id).count()
            if existing_items == 0:
                menu_items = [
                    {'name': 'Plov', 'description': 'Ənənəvi Azərbaycan plov', 'price': 8.5, 'category': 'Əsas yeməklər'},
                    {'name': 'Dolma', 'description': 'Üzüm yarpağında dolma', 'price': 6.0, 'category': 'Əsas yeməklər'},
                    {'name': 'Çay', 'description': 'İsti qara çay', 'price': 1.5, 'category': 'İçkilər'},
                    {'name': 'Baklava', 'description': 'Şirin baklava', 'price': 4.0, 'category': 'Şirniyyat'},
                ]
                for item in menu_items:
                    db.session.add(MenuItem(restaurant_id=restaurant.id, **item))
                print("✅ Menyu əlavə edildi.")

        db.session.commit()
        print("🎉 Məlumat bazası ilkin olaraq hazırlandı.")

# Sadəcə ilk dəfə üçün işə salırıq
if not os.path.exists("init_done.txt"):
    initialize_data()
    with open("init_done.txt", "w") as f:
        f.write("done")

# Gunicorn üçün lazım olan app obyekti
# Bundan sonra gunicorn wsgi:app işləyəcək
