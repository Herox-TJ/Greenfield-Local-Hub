from flask import Flask, render_template, request, redirect, url_for, session, flash
from model import db, User, Producer, Product, CartItem, Order, OrderItem
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
    if 'user_id' in session:
        user = get_current_user()
        if user:
            return redirect(url_for(f'dashboard_{user.role}'))
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
                sid = session.pop('guest_sid', None)
                if sid:
                    for item in CartItem.query.filter_by(session_id=sid).all():
                        existing = CartItem.query.filter_by(
                            user_id=user.id, product_id=item.product_id).first()
                        if existing:
                            existing.quantity += item.quantity
                            db.session.delete(item)
                        else:
                            item.user_id = user.id
                            item.session_id = None
                    db.session.commit()
                flash(f'Welcome back, {user.first_name}!', 'success')
                return redirect(url_for(f'dashboard_{user.role}'))
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
        sec_q      = request.form.get('security_question', '').strip()
        sec_a      = request.form.get('security_answer', '').strip().lower()

        if not all([first_name, last_name, email, password, confirm]):
            flash('All fields are required.', 'error')
            return render_template('register.html')
        if len(first_name) < 2 or len(first_name) > 20:
            flash('First name must be between 2 and 20 characters.', 'error')
            return render_template('register.html')
        if len(last_name) < 2 or len(last_name) > 20:
            flash('Last name must be between 2 and 20 characters.', 'error')
            return render_template('register.html')
        if '@' not in email or '.' not in email.split('@')[-1]:
            flash('Please enter a valid email address.', 'error')
            return render_template('register.html')
        if password != confirm:
            flash('Passwords do not match.', 'error')
            return render_template('register.html')
        if len(password) < 8 or len(password) > 16:
            flash('Password must be between 8 and 16 characters.', 'error')
            return render_template('register.html')
        if not any(c.isupper() for c in password):
            flash('Password must contain at least one uppercase letter.', 'error')
            return render_template('register.html')
        if not any(c.islower() for c in password):
            flash('Password must contain at least one lowercase letter.', 'error')
            return render_template('register.html')
        if not any(c.isdigit() for c in password):
            flash('Password must contain at least one number.', 'error')
            return render_template('register.html')
        if not any(c in '!@#$%^&*()_+-=[]{}|;:,.<>?' for c in password):
            flash('Password must contain at least one special character.', 'error')
            return render_template('register.html')
        if User.query.filter_by(email=email).first():
            flash('An account with this email already exists.', 'error')
            return render_template('register.html')

        user = User(first_name=first_name, last_name=last_name, email=email,
                    role=role, security_question=sec_q, security_answer=sec_a)
        user.set_password(password)
        db.session.add(user)
        db.session.flush()

        if role == 'producer':
            p = Producer(user_id=user.id,
                         name=f"{first_name} {last_name}'s Farm",
                         slug=f"producer-{uuid.uuid4().hex[:8]}",
                         description='', location='')
            db.session.add(p)

        db.session.commit()
        session['user_id'] = user.id
        flash('Account created! Welcome to Greenfield Local Hub.', 'success')
        return redirect(url_for(f'dashboard_{role}'))

    return render_template('register.html')


@app.route('/logout')
def logout():
    session.pop('user_id', None)
    flash('You have been logged out.', 'success')
    return redirect(url_for('index'))


#password reset
@app.route('/forgot-password', methods=['GET', 'POST'])
def forgot_password():
    if request.method == 'POST':
        email = request.form.get('email', '').strip().lower()
        user  = User.query.filter_by(email=email).first()
        if user and user.security_question:
            session['reset_email'] = email
            return redirect(url_for('reset_security'))
        flash('No account found with that email address.', 'error')
    return render_template('forgot_password.html')


@app.route('/reset-password/security', methods=['GET', 'POST'])
def reset_security():
    email = session.get('reset_email')
    if not email:
        return redirect(url_for('forgot_password'))
    user = User.query.filter_by(email=email).first()
    if not user:
        return redirect(url_for('forgot_password'))
    if request.method == 'POST':
        answer = request.form.get('answer', '').strip().lower()
        if answer == user.security_answer:
            session['reset_verified'] = True
            return redirect(url_for('reset_new_password'))
        flash('Incorrect answer. Please try again.', 'error')
    return render_template('reset_security.html', question=user.security_question)


@app.route('/reset-password/new', methods=['GET', 'POST'])
def reset_new_password():
    if not session.get('reset_verified') or not session.get('reset_email'):
        return redirect(url_for('forgot_password'))
    if request.method == 'POST':
        password = request.form.get('password', '')
        confirm  = request.form.get('confirm_password', '')
        if len(password) < 8 or len(password) > 16:
            flash('Password must be between 8 and 16 characters.', 'error')
            return render_template('reset_new_password.html')
        if password != confirm:
            flash('Passwords do not match.', 'error')
            return render_template('reset_new_password.html')
        user = User.query.filter_by(email=session['reset_email']).first()
        user.set_password(password)
        db.session.commit()
        session.pop('reset_email', None)
        session.pop('reset_verified', None)
        flash('Password reset successfully! Please log in.', 'success')
        return redirect(url_for('login'))
    return render_template('reset_new_password.html')


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


#dashboards
@app.route('/dashboard/customer')
@login_required
def dashboard_customer():
    user   = get_current_user()
    if user.role != 'customer':
        return redirect(url_for(f'dashboard_{user.role}'))
    orders = Order.query.filter_by(user_id=user.id).order_by(Order.created_at.desc()).all()
    return render_template('dashboard/customer.html', user=user, orders=orders)


@app.route('/dashboard/producer')
@login_required
def dashboard_producer():
    user     = get_current_user()
    if user.role != 'producer':
        return redirect(url_for(f'dashboard_{user.role}'))
    producer = Producer.query.filter_by(user_id=user.id).first()
    prods    = Product.query.filter_by(producer_id=producer.id).all() if producer else []
    total_stock = sum(p.stock for p in prods)
    prod_ids    = [p.id for p in prods]
    order_items = OrderItem.query.filter(OrderItem.product_id.in_(prod_ids)).all() if prod_ids else []
    order_ids   = list({oi.order_id for oi in order_items})
    orders      = Order.query.filter(Order.id.in_(order_ids)).order_by(Order.created_at.desc()).limit(5).all() if order_ids else []
    total_revenue = sum(oi.price * oi.quantity for oi in order_items)
    return render_template('dashboard/producer.html', user=user, producer=producer,
                           products=prods, total_stock=total_stock,
                           total_revenue=total_revenue, orders=orders)


@app.route('/dashboard/admin')
@login_required
def dashboard_admin():
    user     = get_current_user()
    if user.role != 'admin':
        return redirect(url_for(f'dashboard_{user.role}'))
    all_users    = User.query.all()
    all_products = Product.query.all()
    all_producers = Producer.query.all()
    all_orders   = Order.query.order_by(Order.created_at.desc()).all()
    total_revenue = sum(o.total for o in Order.query.all())
    categories   = {}
    for p in all_products:
        cat = p.category or 'Other'
        categories[cat] = categories.get(cat, 0) + 1
    max_category_count = max(categories.values()) if categories else 1
    return render_template('dashboard/admin.html', user=user,
                           users=all_users, products=all_products,
                           producers=all_producers, orders=all_orders,
                           total_revenue=total_revenue, categories=categories,
                           max_category_count=max_category_count)


#init
with app.app_context():
    db.create_all()

if __name__ == '__main__':
    app.run(debug=True) 