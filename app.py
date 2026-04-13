from flask import Flask, render_template, request, redirect, url_for, session, flash
from model import db, User, Producer, Product, CartItem
from functools import wraps
import uuid

app = Flask(__name__)
app.config['SECRET_KEY'] = 'greenfield-local-hub-2026'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///greenfield.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)


#helpers 
def get_current_user():
    if 'user_id' in session:
        return db.session.get(User, session['user_id'])
    return None


def get_cart_count():
    user = get_current_user()
    if user:
        return CartItem.query.filter_by(user_id=user.id).count()
    sid = session.get('guest_sid')
    if sid:
        return CartItem.query.filter_by(session_id=sid).count()
    return 0


def login_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if 'user_id' not in session:
            flash('Please log in to access this page.', 'error')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated


@app.context_processor
def inject_globals():
    return {'current_user': get_current_user(), 'cart_count': get_cart_count()}


#public pages
@app.route('/')
def index():

    featured = Product.query.limit(6).all()
    return render_template('index.html', featured=featured)


@app.route('/products')
def products():
    category     = request.args.get('category', 'all')
    search       = request.args.get('search', '').strip()
    q            = Product.query
    if category and category != 'all':
        q = q.filter_by(category=category)
    if search:
        q = q.filter(Product.name.ilike(f'%{search}%'))
    all_products = q.all()
    categories   = ['All', 'Vegetables', 'Fruits', 'Dairy', 'Bakery', 'Meat']
    return render_template('products.html', products=all_products,
                           categories=categories, selected=category, search=search)


@app.route('/products/<slug>')
def product_detail(slug):
    product = Product.query.filter_by(slug=slug).first_or_404()
    return render_template('product_detail.html', product=product)


@app.route('/producers')
def producers():
    all_producers = Producer.query.all()
    return render_template('producers.html', producers=all_producers)


@app.route('/producers/<slug>')
def producer_detail(slug):
    producer = Producer.query.filter_by(slug=slug).first_or_404()
    prods    = Product.query.filter_by(producer_id=producer.id).all()
    return render_template('producer_detail.html', producer=producer, products=prods)


@app.route('/about')
def about():
    return render_template('about.html')


@app.route('/contact', methods=['GET', 'POST'])
def contact():
    if request.method == 'POST':
        flash('Thank you for your message! We will get back to you soon.', 'success')
        return redirect(url_for('contact'))
    return render_template('contact.html')


@app.route('/privacy')
def privacy():
    return render_template('privacy.html')


@app.route('/terms')
def terms():
    return render_template('terms.html')


#auth

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email    = request.form.get('email', '').strip().lower()
        password = request.form.get('password', '')
        user     = User.query.filter_by(email=email).first()
        selected_role = request.form.get('role', 'customer')
        if user and user.check_password(password):
            if user.role != selected_role:
                flash(f'This account is not registered as a {selected_role}.', 'error')
            else:
                session['user_id'] = user.id
                # merge guest cart
                sid = session.pop('guest_sid', None)
                if sid:
                    for item in CartItem.query.filter_by(session_id=sid).all():
                        existing = CartItem.query.filter_by(
                            user_id=user.id, product_id=item.product_id).first()
                        if existing:
                            existing.quantity += item.quantity
                            db.session.delete(item)
                        else:
                            item.user_id    = user.id
                            item.session_id = None
                    db.session.commit()
                flash(f'Welcome back, {user.first_name}!', 'success')
                return redirect(url_for('index'))
        else:
            flash('Invalid email or password.', 'error')
    return render_template('login.html')


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        first_name = request.form.get('first_name', '').strip()
        last_name  = request.form.get('last_name', '').strip()
        email      = request.form.get('email', '').strip().lower()
        password   = request.form.get('password', '')
        confirm    = request.form.get('confirm_password', '')
        role       = request.form.get('role', 'customer')

        if not all([first_name, last_name, email, password, confirm]):
            flash('All fields are required.', 'error')
            return render_template('register.html')
        if password != confirm:
            flash('Passwords do not match.', 'error')
            return render_template('register.html')
        if len(password) < 8:
            flash('Password must be at least 8 characters.', 'error')
            return render_template('register.html')
        if User.query.filter_by(email=email).first():
            flash('An account with this email already exists.', 'error')
            return render_template('register.html')

        user = User(first_name=first_name, last_name=last_name,
                    email=email, role=role)
        user.set_password(password)
        db.session.add(user)
        db.session.commit()
        session['user_id'] = user.id
        flash('Account created! Welcome to Greenfield Local Hub.', 'success')
        return redirect(url_for('index'))

    return render_template('register.html')


@app.route('/logout')
def logout():
    session.pop('user_id', None)
    flash('You have been logged out.', 'success')
    return redirect(url_for('index'))


#cart
@app.route('/cart')
def cart():
    user  = get_current_user()
    if user:
        items = CartItem.query.filter_by(user_id=user.id).all()
    else:
        sid   = session.get('guest_sid')
        items = CartItem.query.filter_by(session_id=sid).all() if sid else []
    total = sum(i.subtotal for i in items)
    return render_template('cart.html', cart_items=items, total=total)


@app.route('/cart/add', methods=['POST'])
def cart_add():
    product_id = request.form.get('product_id', type=int)
    quantity   = request.form.get('quantity', 1, type=int)
    product    = db.session.get(Product, product_id)
    if not product:
        flash('Product not found.', 'error')
        return redirect(url_for('products'))
    user = get_current_user()
    if user:
        existing = CartItem.query.filter_by(user_id=user.id, product_id=product_id).first()
        if existing:
            existing.quantity += quantity
        else:
            db.session.add(CartItem(user_id=user.id, product_id=product_id, quantity=quantity))
    else:
        sid = session.get('guest_sid')
        if not sid:
            sid = str(uuid.uuid4())
            session['guest_sid'] = sid
        existing = CartItem.query.filter_by(session_id=sid, product_id=product_id).first()
        if existing:
            existing.quantity += quantity
        else:
            db.session.add(CartItem(session_id=sid, product_id=product_id, quantity=quantity))
    db.session.commit()
    flash(f'{product.name} added to cart!', 'success')
    return redirect(request.referrer or url_for('products'))


@app.route('/cart/remove/<int:item_id>', methods=['POST'])
def cart_remove(item_id):
    item = db.session.get(CartItem, item_id)
    if not item:
        return redirect(url_for('cart'))
    user = get_current_user()
    if (user and item.user_id == user.id) or \
       (not user and item.session_id == session.get('guest_sid')):
        db.session.delete(item)
        db.session.commit()
    return redirect(url_for('cart'))


@app.route('/cart/update', methods=['POST'])
def cart_update():
    item_id  = request.form.get('item_id', type=int)
    quantity = request.form.get('quantity', type=int)
    item     = db.session.get(CartItem, item_id)
    if not item:
        return redirect(url_for('cart'))
    user       = get_current_user()
    authorized = (user and item.user_id == user.id) or \
                 (not user and item.session_id == session.get('guest_sid'))
    if authorized:
        if quantity and quantity > 0:
            item.quantity = quantity
            db.session.commit()
        elif quantity == 0:
            db.session.delete(item)
            db.session.commit()
    return redirect(url_for('cart'))


#init
with app.app_context():
    db.create_all()

if __name__ == '__main__':
    app.run(debug=True) 