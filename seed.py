"""Run once to populate the database with sample data.
   Usage: python seed.py
   Credentials:
     Admin:    admin@greenfield.com  / Admin123!
     Customer: customer@greenfield.com / Customer1!
"""

from app import app, db
from model import User, Producer, Product


def seed():
    with app.app_context():
        Product.query.delete()
        Producer.query.delete()
        User.query.delete()
        db.session.commit()

        # users 
        admin = User(first_name='Gabby', last_name='Admin',
                     email='admin@greenfield.com', role='admin')
        admin.set_password('Admin123!')

        customer = User(first_name='TJ', last_name='Swami',
                        email='customer@greenfield.com', role='customer')
        customer.set_password('Customer1!')

        db.session.add_all([admin, customer])
        db.session.commit()

        print('Seed data created successfully.')
        print('  admin@greenfield.com    / Admin123!')
        print('  customer@greenfield.com / Customer1!')


if __name__ == '__main__':
    seed() 