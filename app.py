#!/usr/bin/env python3

from app import create_app, db
from app.models import User, Restaurant, Table, MenuItem, Order, OrderItem, SecurityLog

# Create Flask application
app = create_app()

# Make shell context
@app.shell_context_processor
def make_shell_context():
    return {
        'db': db,
        'User': User,
        'Restaurant': Restaurant,
        'Table': Table,
        'MenuItem': MenuItem,
        'Order': Order,
        'OrderItem': OrderItem,
        'SecurityLog': SecurityLog
    }

if __name__ == '__main__':
    with app.app_context():
        # Create all database tables
        db.create_all()
        
        # Create admin user if not exists
        admin = User.query.filter_by(username='admin').first()
        if not admin:
            admin = User(
                username='admin',
                email='admin@Kafem.az',
                role='admin'
            )
            admin.set_password('admin123')
            db.session.add(admin)
            print("Created admin user: admin/admin123")
        
        # Create sample restaurant if not exists
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
            
            # Create restaurant owner
            owner = User(
                username='restoran1',
                email='restoran1@Kafem.az',
                role='restoran_sahibi',
                restaurant_id=restaurant.id
            )
            owner.set_password('restoran123')
            db.session.add(owner)
            
            # Create waiter
            waiter = User(
                username='ofisiant1',
                email='ofisiant1@Kafem.az',
                role='ofisiant',
                restaurant_id=restaurant.id
            )
            waiter.set_password('ofisiant123')
            db.session.add(waiter)
            
            print("Created sample restaurant and users")
            print("Restaurant owner: restoran1/restoran123")
            print("Waiter: ofisiant1/ofisiant123")
        
        db.session.commit()
        
        # Create tables if not exist
        from app.services.table_service import TableService
        if restaurant:
            existing_tables = Table.query.filter_by(restaurant_id=restaurant.id).count()
            if existing_tables == 0:
                try:
                    TableService.create_tables_for_restaurant(restaurant.id, restaurant.table_count)
                    print(f"Created {restaurant.table_count} tables with QR codes")
                except Exception as e:
                    print(f"Error creating tables: {e}")
        
        # Create sample menu items
        if restaurant:
            existing_items = MenuItem.query.filter_by(restaurant_id=restaurant.id).count()
            if existing_items == 0:
                menu_items = [
                    {
                        'name': 'Plov',
                        'description': 'Ənənəvi Azərbaycan plov',
                        'price': 8.50,
                        'category': 'Əsas yeməklər'
                    },
                    {
                        'name': 'Dolma',
                        'description': 'Üzüm yarpağında dolma',
                        'price': 6.00,
                        'category': 'Əsas yeməklər'
                    },
                    {
                        'name': 'Çay',
                        'description': 'İsti qara çay',
                        'price': 1.50,
                        'category': 'İçkilər'
                    },
                    {
                        'name': 'Baklava',  
                        'description': 'Şirin baklava',
                        'price': 4.00,
                        'category': 'Şirniyyat'
                    }
                ]
                
                for item_data in menu_items:
                    item = MenuItem(
                        restaurant_id=restaurant.id,
                        **item_data
                    )
                    db.session.add(item)
                
                db.session.commit()
                print("Created sample menu items")
        
        print("\n" + "="*50)
        print("Kafem Application Started Successfully!")
        print("="*50)
        print("Login credentials:")
        print("Admin: admin/admin123")
        print("Restaurant Owner: restoran1/restoran123") 
        print("Waiter: ofisiant1/ofisiant123")
        print("="*50)
    
    # Run the application
    app.run(debug=True, host='0.0.0.0', port=5000)