from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import relationship
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime

db = SQLAlchemy()


class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(100), nullable=False)
    last_name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(200), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    role = db.Column(db.String(20), default='customer')  # customer, producer, admin
    phone_number = db.Column(db.String(30))
    address = db.Column(db.Text)
    accessibility_preferences = db.Column(db.Text)
    is_active = db.Column(db.Boolean, default=True)
    security_question = db.Column(db.String(300))
    security_answer = db.Column(db.String(200))
    loyalty_points = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    cart_items = db.relationship('CartItem', backref='user', lazy=True,
                                 foreign_keys='CartItem.user_id')
    orders = db.relationship('Order', backref='user', lazy=True)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"

    @property
    def initials(self):
        return f"{self.first_name[0]}{self.last_name[0]}".upper()

    @property
    def member_since_year(self):
        return self.created_at.year


class Producer(db.Model):
    __tablename__ = 'producers'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    name = db.Column(db.String(200), nullable=False)
    slug = db.Column(db.String(200), unique=True, nullable=False)
    description = db.Column(db.Text)
    location = db.Column(db.String(300))
    image = db.Column(db.String(400))
    farming_methods = db.Column(db.String(500))   # comma-separated
    certifications = db.Column(db.String(500))    # comma-separated

    products = db.relationship('Product', backref='producer', lazy=True)

    @property
    def farming_methods_list(self):
        if self.farming_methods:
            return [m.strip() for m in self.farming_methods.split(',') if m.strip()]
        return []

    @property
    def certifications_list(self):
        if self.certifications:
            return [c.strip() for c in self.certifications.split(',') if c.strip()]
        return []

    @property
    def product_count(self):
        return len(self.products)


class Product(db.Model):
    __tablename__ = 'products'
    id = db.Column(db.Integer, primary_key=True)
    producer_id = db.Column(db.Integer, db.ForeignKey('producers.id'), nullable=False)
    name = db.Column(db.String(200), nullable=False)
    slug = db.Column(db.String(200), unique=True, nullable=False, index=True)
    description = db.Column(db.Text)
    price = db.Column(db.Float, nullable=False)
    unit = db.Column(db.String(50))   # e.g. '1kg', '250g', 'each'
    stock = db.Column(db.Integer, default=0)
    category = db.Column(db.String(100), index=True)  # Vegetables, Fruits, Dairy, Bakery, Meat

    image = db.Column(db.String(400))
    is_available = db.Column(db.Boolean, default=True)
    origin_location = db.Column(db.String(300))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    cart_items = db.relationship('CartItem', backref='product', lazy=True)
    order_items = db.relationship('OrderItem', backref='product', lazy=True)

    @property
    def in_stock(self):
        return self.stock > 0

    @property
    def formatted_price(self):
        return f"£{self.price:.2f}"


class CartItem(db.Model):
    __tablename__ = 'cart_items'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    session_id = db.Column(db.String(200), nullable=True)   # for guest users
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'), nullable=False)
    quantity = db.Column(db.Integer, default=1)

    @property
    def subtotal(self):
        return self.product.price * self.quantity


class Order(db.Model):
    __tablename__ = 'orders'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    total = db.Column(db.Float, default=0.0)
    status = db.Column(db.String(50), default='pending')
    fulfillment_method = db.Column(db.String(20), default='delivery')  # delivery, collection
    delivery_address = db.Column(db.Text)
    delivery_date = db.Column(db.Date)
    delivery_slot = db.Column(db.String(50))
    is_cart = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    items = db.relationship('OrderItem', backref='order', lazy=True)


class OrderItem(db.Model):
    __tablename__ = 'order_items'
    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey('orders.id'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'), nullable=False)
    quantity = db.Column(db.Integer, default=1)
    price = db.Column(db.Float, nullable=False)


class Payment(db.Model):
    __tablename__ = 'payments'
    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey('orders.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    method = db.Column(db.String(50))  # card, etc.
    status = db.Column(db.String(50), default='pending')  # pending, completed, refunded
    transaction_ref = db.Column(db.String(200))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    order = db.relationship('Order', backref='payments', lazy=True)


class LoyaltyScheme(db.Model):
    __tablename__ = 'loyalty_scheme'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    order_id = db.Column(db.Integer, db.ForeignKey('orders.id'), nullable=True)
    points_earned = db.Column(db.Integer, default=0)
    points_redeemed = db.Column(db.Integer, default=0)
    description = db.Column(db.String(300))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    user = db.relationship('User', backref='loyalty_history', lazy=True)


class AuditLog(db.Model):
    __tablename__ = 'audit_logs'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    action = db.Column(db.String(200), nullable=False)
    target_type = db.Column(db.String(100))  # e.g. 'User', 'Product', 'Order'
    target_id = db.Column(db.Integer)
    detail = db.Column(db.Text)
    ip_address = db.Column(db.String(50))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    user = db.relationship('User', backref='audit_logs', lazy=True) 