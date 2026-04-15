from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime

db = SQLAlchemy()


class User(db.Model):
    __tablename__ = 'users'
    id            = db.Column(db.Integer, primary_key=True)
    first_name    = db.Column(db.String(100), nullable=False)
    last_name     = db.Column(db.String(100), nullable=False)
    email         = db.Column(db.String(200), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    role          = db.Column(db.String(20), default='customer')
    created_at    = db.Column(db.DateTime, default=datetime.utcnow)

    cart_items = db.relationship('CartItem', backref='user', lazy=True,
                                 foreign_keys='CartItem.user_id')

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


class Producer(db.Model):
    __tablename__ = 'producers'
    id              = db.Column(db.Integer, primary_key=True)
    user_id         = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    name            = db.Column(db.String(200), nullable=False)
    slug            = db.Column(db.String(200), unique=True, nullable=False)
    description     = db.Column(db.Text)
    location        = db.Column(db.String(300))
    image           = db.Column(db.String(400))
    farming_methods = db.Column(db.String(500))   # comma-separated
    certifications  = db.Column(db.String(500))   # comma-separated

    products = db.relationship('Product', backref='producer', lazy=True)

    @property
    def farming_methods_list(self):
        if self.farming_methods:
            return [m.strip() for m in self.farming_methods.split(',') if m.strip()]
        return []
    
    @property
    def certifications_list(self):
        if self.certificatons:
            return [c.strip() for c in self.certifications.split(',') if c.strip()]
        return []

    @property
    def product_count(self):
        return len(self.products)


class Product(db.Model):
    __tablename__ = 'products'
    id          = db.Column(db.Integer, primary_key=True)
    producer_id = db.Column(db.Integer, db.ForeignKey('producers.id'), nullable=False)
    name        = db.Column(db.String(200), nullable=False)
    slug        = db.Column(db.String(200), unique=True, nullable=False)
    description = db.Column(db.Text)
    price       = db.Column(db.Float, nullable=False)
    unit        = db.Column(db.String(50))
    stock       = db.Column(db.Integer, default=0)
    category    = db.Column(db.String(100))
    image       = db.Column(db.String(400), nullable=False)

    cart_items = db.relationship('CartItem', backref='product', lazy=True)

    @property
    def in_stock(self):
        return self.stock > 0

    @property
    def formatted_price(self):
        return f"£{self.price:.2f}"


class CartItem(db.Model):
    __tablename__ = 'cart_items'
    id         = db.Column(db.Integer, primary_key=True)
    user_id    = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    session_id = db.Column(db.String(200), nullable=True)   # for guests
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'), nullable=False)
    quantity   = db.Column(db.Integer, default=1)

    @property
    def subtotal(self):
        return self.product.price * self.quantity