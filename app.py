from flask import Flask, render_template, request, redirect, url_for, flash, jsonify, session
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, timedelta
import os
from functools import wraps

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key-here-change-in-production'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///rental_app.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(days=7)  # Session lasts 7 days

db = SQLAlchemy(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# Database Models
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    phone = db.Column(db.String(20), nullable=False)
    password_hash = db.Column(db.String(120), nullable=False)
    is_admin = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

class Vehicle(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    model = db.Column(db.String(100), nullable=False)
    vehicle_type = db.Column(db.String(20), nullable=False)  # 'car' or 'bike'
    mileage = db.Column(db.String(50), nullable=False)
    price_per_day = db.Column(db.Float, nullable=False)
    image_url = db.Column(db.String(200), nullable=False)
    is_available = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Rental(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    vehicle_id = db.Column(db.Integer, db.ForeignKey('vehicle.id'), nullable=False)
    start_date = db.Column(db.Date, nullable=False)
    end_date = db.Column(db.Date, nullable=False)
    total_price = db.Column(db.Float, nullable=False)
    is_returned = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    user = db.relationship('User', backref='rentals')
    vehicle = db.relationship('Vehicle', backref='rentals')

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.is_admin:
            flash('Admin access required', 'error')
            return redirect(url_for('index'))
        return f(*args, **kwargs)
    return decorated_function

# Routes
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        
        if user and user.check_password(password):
            login_user(user, remember=True)
            session.permanent = True
            return redirect(url_for('vehicle_selection'))
        else:
            flash('Invalid username or password', 'error')
    
    return render_template('login.html')

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        phone = request.form['phone']
        password = request.form['password']
        
        if User.query.filter_by(username=username).first():
            flash('Username already exists', 'error')
            return render_template('signup.html')
        
        if User.query.filter_by(email=email).first():
            flash('Email already exists', 'error')
            return render_template('signup.html')
        
        user = User(username=username, email=email, phone=phone)
        user.set_password(password)
        db.session.add(user)
        db.session.commit()
        
        # Automatically log in the user after signup
        login_user(user, remember=True)
        flash('Account created successfully! You are now logged in.', 'success')
        return redirect(url_for('vehicle_selection'))
    
    return render_template('signup.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))

@app.route('/vehicle-selection')
@login_required
def vehicle_selection():
    cars = Vehicle.query.filter_by(vehicle_type='car', is_available=True).all()
    bikes = Vehicle.query.filter_by(vehicle_type='bike', is_available=True).all()
    return render_template('vehicle_selection.html', cars=cars, bikes=bikes)

@app.route('/rental-details', methods=['GET', 'POST'])
@login_required
def rental_details():
    if request.method == 'POST':
        selected_vehicles = request.form.getlist('selected_vehicles')
        if not selected_vehicles:
            flash('Please select at least one vehicle', 'error')
            return redirect(url_for('vehicle_selection'))
        
        vehicles = Vehicle.query.filter(Vehicle.id.in_(selected_vehicles)).all()
        return render_template('rental_details.html', vehicles=vehicles)
    
    return redirect(url_for('vehicle_selection'))

@app.route('/confirm-rental', methods=['POST'])
@login_required
def confirm_rental():
    vehicle_ids = request.form.getlist('vehicle_ids')
    start_date = datetime.strptime(request.form['start_date'], '%Y-%m-%d').date()
    end_date = datetime.strptime(request.form['end_date'], '%Y-%m-%d').date()
    
    if start_date >= end_date:
        flash('End date must be after start date', 'error')
        return redirect(url_for('rental_details'))
    
    vehicles = Vehicle.query.filter(Vehicle.id.in_(vehicle_ids)).all()
    total_price = 0
    rental_days = (end_date - start_date).days
    
    for vehicle in vehicles:
        if not vehicle.is_available:
            flash(f'{vehicle.name} is no longer available', 'error')
            return redirect(url_for('vehicle_selection'))
        
        total_price += vehicle.price_per_day * rental_days
        
        # Create rental record
        rental = Rental(
            user_id=current_user.id,
            vehicle_id=vehicle.id,
            start_date=start_date,
            end_date=end_date,
            total_price=vehicle.price_per_day * rental_days
        )
        db.session.add(rental)
        
        # Mark vehicle as unavailable
        vehicle.is_available = False
    
    db.session.commit()
    flash(f'Rental confirmed! Total price: ${total_price:.2f}', 'success')
    return redirect(url_for('my_rentals'))

@app.route('/my-rentals')
@login_required
def my_rentals():
    rentals = Rental.query.filter_by(user_id=current_user.id, is_returned=False).all()
    return render_template('my_rentals.html', rentals=rentals)

@app.route('/return-vehicle/<int:rental_id>')
@login_required
def return_vehicle(rental_id):
    rental = Rental.query.get_or_404(rental_id)
    if rental.user_id != current_user.id:
        flash('Unauthorized access', 'error')
        return redirect(url_for('my_rentals'))
    
    rental.is_returned = True
    rental.vehicle.is_available = True
    db.session.commit()
    
    flash('Vehicle returned successfully!', 'success')
    return redirect(url_for('my_rentals'))

@app.route('/admin')
@admin_required
def admin_dashboard():
    today = datetime.now().date()
    active_rentals = Rental.query.filter_by(is_returned=False).all()
    today_rentals = Rental.query.filter(
        Rental.start_date <= today,
        Rental.end_date >= today,
        Rental.is_returned == False
    ).all()
    
    # Debug: Print rental details to console
    print(f"Admin Dashboard - Active Rentals: {len(active_rentals)}")
    for rental in active_rentals:
        print(f"Rental ID: {rental.id}, User: {rental.user.username}, Vehicle: {rental.vehicle.name}")
    
    return render_template('admin_dashboard.html', 
                         active_rentals=active_rentals, 
                         today_rentals=today_rentals)

@app.route('/forgot-password', methods=['GET', 'POST'])
def forgot_password():
    if request.method == 'POST':
        email = request.form['email']
        user = User.query.filter_by(email=email).first()
        
        if user:
            # In a real application, you would send an email with reset link
            flash('Password reset instructions have been sent to your email.', 'success')
        else:
            flash('Email not found in our system.', 'error')
        
        return redirect(url_for('login'))
    
    return render_template('forgot_password.html')

@app.route('/api/vehicles')
def api_vehicles():
    vehicle_type = request.args.get('type')
    search = request.args.get('search', '')
    
    query = Vehicle.query.filter_by(is_available=True)
    if vehicle_type:
        query = query.filter_by(vehicle_type=vehicle_type)
    if search:
        query = query.filter(Vehicle.name.contains(search) | Vehicle.model.contains(search))
    
    vehicles = query.all()
    return jsonify([{
        'id': v.id,
        'name': v.name,
        'model': v.model,
        'vehicle_type': v.vehicle_type,
        'mileage': v.mileage,
        'price_per_day': v.price_per_day,
        'image_url': v.image_url,
        'is_available': v.is_available
    } for v in vehicles])

@app.route('/api/vehicle/<int:vehicle_id>')
def api_vehicle_details(vehicle_id):
    vehicle = Vehicle.query.get_or_404(vehicle_id)
    return jsonify({
        'id': vehicle.id,
        'name': vehicle.name,
        'model': vehicle.model,
        'vehicle_type': vehicle.vehicle_type,
        'mileage': vehicle.mileage,
        'price_per_day': vehicle.price_per_day,
        'image_url': vehicle.image_url,
        'is_available': vehicle.is_available
    })

@app.route('/api/user/rentals')
@login_required
def api_user_rentals():
    rentals = Rental.query.filter_by(user_id=current_user.id, is_returned=False).all()
    return jsonify([{
        'id': r.id,
        'vehicle_name': r.vehicle.name,
        'vehicle_model': r.vehicle.model,
        'vehicle_image': r.vehicle.image_url,
        'start_date': r.start_date.isoformat(),
        'end_date': r.end_date.isoformat(),
        'total_price': r.total_price,
        'is_returned': r.is_returned
    } for r in rentals])

@app.route('/test')
def test_page():
    return render_template('test_page.html')

@app.route('/create-test-user')
def create_test_user():
    # Create a test user for demonstration
    test_user = User.query.filter_by(username='testuser').first()
    if not test_user:
        test_user = User(username='testuser', email='test@example.com', phone='1234567890')
        test_user.set_password('test123')
        db.session.add(test_user)
        db.session.commit()
        return jsonify({'message': 'Test user created successfully! Username: testuser, Password: test123'})
    else:
        return jsonify({'message': 'Test user already exists! Username: testuser, Password: test123'})

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        
        # Create sample data if no vehicles exist
        if Vehicle.query.count() == 0:
            sample_vehicles = [
                # Cars
                Vehicle(name='Toyota Camry', model='2023', vehicle_type='car', mileage='25 MPG', price_per_day=50.0, image_url='https://images.unsplash.com/photo-1621007947382-bb3c3994e3fb?w=400&h=300&fit=crop'),
                Vehicle(name='Honda Civic', model='2023', vehicle_type='car', mileage='32 MPG', price_per_day=45.0, image_url='https://images.unsplash.com/photo-1558618666-fcd25c85cd64?w=400&h=300&fit=crop'),
                Vehicle(name='BMW 3 Series', model='2023', vehicle_type='car', mileage='28 MPG', price_per_day=80.0, image_url='https://images.unsplash.com/photo-1555215695-3004980ad54e?w=400&h=300&fit=crop'),
                Vehicle(name='Mercedes C-Class', model='2023', vehicle_type='car', mileage='26 MPG', price_per_day=85.0, image_url='https://images.unsplash.com/photo-1618843479313-40f8afb4b4d8?w=400&h=300&fit=crop'),
                Vehicle(name='Audi A4', model='2023', vehicle_type='car', mileage='27 MPG', price_per_day=75.0, image_url='https://images.unsplash.com/photo-1606664515524-ed2f786a0bd6?w=400&h=300&fit=crop'),
                Vehicle(name='Tesla Model 3', model='2023', vehicle_type='car', mileage='Electric', price_per_day=90.0, image_url='https://images.unsplash.com/photo-1560958089-b8a1929cea89?w=400&h=300&fit=crop'),
                Vehicle(name='Ford Mustang', model='2023', vehicle_type='car', mileage='22 MPG', price_per_day=70.0, image_url='https://images.unsplash.com/photo-1552519507-da3b142c6e3d?w=400&h=300&fit=crop'),
                Vehicle(name='Chevrolet Corvette', model='2023', vehicle_type='car', mileage='19 MPG', price_per_day=120.0, image_url='https://images.unsplash.com/photo-1544636331-e26879cd4d9b?w=400&h=300&fit=crop'),
                Vehicle(name='Nissan Altima', model='2023', vehicle_type='car', mileage='30 MPG', price_per_day=40.0, image_url='https://images.unsplash.com/photo-1606664515524-ed2f786a0bd6?w=400&h=300&fit=crop'),
                Vehicle(name='Hyundai Sonata', model='2023', vehicle_type='car', mileage='29 MPG', price_per_day=42.0, image_url='https://images.unsplash.com/photo-1555215695-3004980ad54e?w=400&h=300&fit=crop'),
                
                # Bikes
                Vehicle(name='Honda CBR600RR', model='2023', vehicle_type='bike', mileage='40 MPG', price_per_day=35.0, image_url='https://images.unsplash.com/photo-1558618666-fcd25c85cd64?w=400&h=300&fit=crop'),
                Vehicle(name='Yamaha R6', model='2023', vehicle_type='bike', mileage='38 MPG', price_per_day=32.0, image_url='https://images.unsplash.com/photo-1558618666-fcd25c85cd64?w=400&h=300&fit=crop'),
                Vehicle(name='Kawasaki Ninja 650', model='2023', vehicle_type='bike', mileage='45 MPG', price_per_day=28.0, image_url='https://images.unsplash.com/photo-1558618666-fcd25c85cd64?w=400&h=300&fit=crop'),
                Vehicle(name='Suzuki GSX-R750', model='2023', vehicle_type='bike', mileage='35 MPG', price_per_day=40.0, image_url='https://images.unsplash.com/photo-1558618666-fcd25c85cd64?w=400&h=300&fit=crop'),
                Vehicle(name='Ducati Panigale V2', model='2023', vehicle_type='bike', mileage='30 MPG', price_per_day=65.0, image_url='https://images.unsplash.com/photo-1558618666-fcd25c85cd64?w=400&h=300&fit=crop'),
                Vehicle(name='BMW S1000RR', model='2023', vehicle_type='bike', mileage='32 MPG', price_per_day=70.0, image_url='https://images.unsplash.com/photo-1558618666-fcd25c85cd64?w=400&h=300&fit=crop'),
                Vehicle(name='Aprilia RSV4', model='2023', vehicle_type='bike', mileage='28 MPG', price_per_day=75.0, image_url='https://images.unsplash.com/photo-1558618666-fcd25c85cd64?w=400&h=300&fit=crop'),
                Vehicle(name='KTM 1290 Super Duke', model='2023', vehicle_type='bike', mileage='35 MPG', price_per_day=55.0, image_url='https://images.unsplash.com/photo-1558618666-fcd25c85cd64?w=400&h=300&fit=crop'),
                Vehicle(name='Triumph Street Triple', model='2023', vehicle_type='bike', mileage='42 MPG', price_per_day=45.0, image_url='https://images.unsplash.com/photo-1558618666-fcd25c85cd64?w=400&h=300&fit=crop'),
                Vehicle(name='Harley Davidson Sportster', model='2023', vehicle_type='bike', mileage='50 MPG', price_per_day=50.0, image_url='https://images.unsplash.com/photo-1558618666-fcd25c85cd64?w=400&h=300&fit=crop'),
            ]
            
            for vehicle in sample_vehicles:
                db.session.add(vehicle)
            
            # Create admin user
            admin = User(username='admin', email='admin@rental.com', phone='1234567890', is_admin=True)
            admin.set_password('admin123')
            db.session.add(admin)
            
            db.session.commit()
    
    app.run(debug=True)
