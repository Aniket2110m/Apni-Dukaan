from flask import Flask, render_template, request, redirect, session, url_for, flash
import json
import os

app = Flask(__name__)
app.secret_key = 'your_secret_key'

USER_FILE = 'users.json'
ORDERS_FILE = 'orders.json'

def load_users():
    if not os.path.exists(USER_FILE):
        return []
    with open(USER_FILE, 'r') as f:
        return json.load(f)

def save_users(users):
    with open(USER_FILE, 'w') as f:
        json.dump(users, f)

def load_orders():
    if not os.path.exists(ORDERS_FILE):
        return []
    with open(ORDERS_FILE, 'r') as f:
        return json.load(f)

def save_orders(orders):
    with open(ORDERS_FILE, 'w') as f:
        json.dump(orders, f, indent=2)

products = [
    {
        'id': 1, 'name': 'Apple Iphone', 'price': 60000, 'image': 'iphone16.jpg',
        'description': 'The phone includes a 48MP main camera for stunning photos and videos.It is powered by the fast and efficient A16 Bionic chip.', 'rating': 4.5
    },
    {
        'id': 2, 'name': 'Apple MacBook', 'price': 90000, 'image': 'mac.jpg',
        'description': 'The MacBook with M-series chip delivers powerful performance and energy efficiency, thanks to Apple’s custom silicon..', 'rating': 4.2
    },
    {
        'id': 3, 'name': 'Apple Watch', 'price': 35000, 'image': 'watch.jpg',
        'description': 'The Apple Watch combines fitness tracking, health monitoring, and smart features in a sleek wearable. It offers heart rate tracking and workout detection.', 'rating': 4.7
    },
    {
        'id': 4, 'name': 'Apple Mac Desktop', 'price': 55000, 'image': 'mac.png',
        'description': 'Apple Mac is a line of personal computers designed and developed by Apple Inc., known for its sleek design and intuitive macOS operating system.', 'rating': 4.1
    },
     {
        'id': 5, 'name': 'Apple iPad', 'price': 37000, 'image': 'ipad.jpg',
        'description': 'Apple iPad is a tablet computer created by Apple Inc., combining portability with powerful performance and a touch-based interface. It runs on iPadOS', 'rating': 4.5
    },
     {
        'id': 6, 'name': 'Apple iPod', 'price': 47000, 'image': 'ipod.jpg',
        'description': 'Apple iPod is a portable media player developed by Apple Inc., originally designed for storing and playing music on the go. It became iconic for its sleek design.', 'rating': 4.2
    },
]

@app.route('/')
def home():
    return render_template('home.html', products=products, user=session.get('user'))

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')

        if not all([username, email, password, confirm_password]):
            flash('Please fill in all fields.', 'error')
            return redirect(url_for('signup'))

        if password != confirm_password:
            flash('Passwords do not match.', 'error')
            return redirect(url_for('signup'))

        users = load_users()

        if any(u['email'] == email for u in users):
            flash('Email already exists. Please login.', 'error')
            return redirect(url_for('signup'))

        users.append({'name': username, 'email': email, 'password': password})
        save_users(users)

        session['user'] = username
        flash('Signup successful!', 'success')
        return redirect(url_for('home'))

    return render_template('signup.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')

        users = load_users()
        user = next((u for u in users if u['email'] == email and u['password'] == password), None)

        if user:
            session['user'] = user['name']
            flash('Login successful!', 'success')
            return redirect(url_for('home'))
        else:
            flash('Invalid email or password.', 'error')
            return redirect(url_for('login'))

    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    flash('Logged out successfully.', 'success')
    return redirect(url_for('home'))

@app.route('/add/<int:product_id>')
def add_to_cart(product_id):
    if 'user' not in session:
        return redirect(url_for('login'))

    cart = session.get('cart', [])
    cart.append(product_id)
    session['cart'] = cart
    return redirect(url_for('home'))

@app.route('/remove/<int:product_id>')
def remove_from_cart(product_id):
    cart = session.get('cart', [])
    if product_id in cart:
        cart.remove(product_id)
    session['cart'] = cart
    return redirect(url_for('cart'))

@app.route('/cart')
def cart():
    if 'user' not in session:
        return redirect(url_for('login'))

    cart = session.get('cart', [])
    items = [p for p in products if p['id'] in cart]
    total = sum(p['price'] for p in items)
    return render_template('cart.html', items=items, total=total)

@app.route('/checkout', methods=['GET', 'POST'])
def checkout():
    if 'user' not in session:
        return redirect(url_for('login'))

    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        address = request.form.get('address')

        cart = session.get('cart', [])
        items = [p for p in products if p['id'] in cart]
        total = sum(p['price'] for p in items)

        orders = load_orders()
        orders.append({
            'name': name,
            'email': email,
            'address': address,
            'items': items,
            'total': total
        })
        save_orders(orders)

        session['cart'] = []
        return render_template('thankyou.html', name=name)
    return render_template('checkout.html')

@app.route('/admin/orders')
def view_orders():
    orders = load_orders()
    return render_template('orders.html', orders=orders)

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(debug=True, host='0.0.0.0', port=port)
