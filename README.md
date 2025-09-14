# Car and Bike Rental Web Application

A comprehensive rental management system built with Flask, featuring a beautiful modern UI and full CRUD functionality.

## Features

### 🚗 Vehicle Management
- **Cars & Bikes**: Browse through 10 cars and 10 bikes
- **Dynamic Availability**: Real-time vehicle availability updates
- **Search & Filter**: Find vehicles by name, model, or type
- **Detailed Information**: Photos, specifications, and pricing

### 👤 User Authentication
- **Sign Up**: Create account with username, email, phone, and password
- **Login/Logout**: Secure authentication system
- **User Dashboard**: View personal rental history

### 📅 Rental System
- **Multi-Vehicle Selection**: Rent multiple vehicles at once
- **Date Selection**: Choose start and end dates with validation
- **Price Calculation**: Automatic total price calculation
- **Return System**: Easy vehicle return process

### 🔧 Admin Dashboard
- **Real-time Monitoring**: Track active rentals and today's rentals
- **User Management**: View customer details and rental history
- **Revenue Tracking**: Monitor total revenue and statistics
- **Vehicle Management**: Mark vehicles as returned

### 🎨 Modern UI/UX
- **Responsive Design**: Works on desktop, tablet, and mobile
- **Bootstrap 5**: Modern, clean interface
- **Interactive Elements**: Smooth animations and transitions
- **Beautiful Images**: High-quality vehicle photos from Unsplash

## Technology Stack

- **Backend**: Python Flask
- **Database**: SQLite (easily switchable to MySQL/PostgreSQL)
- **Frontend**: HTML5, CSS3, JavaScript, Bootstrap 5
- **Authentication**: Flask-Login
- **Forms**: Flask-WTF with validation
- **Icons**: Font Awesome 6

## Installation & Setup

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd rental-application
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Run the application**
   ```bash
   python app.py
   ```

4. **Access the application**
   - Open your browser and go to `http://localhost:5000`
   - Admin login: username: `admin`, password: `admin123`

## Usage

### For Regular Users
1. **Sign Up**: Create a new account with your details
2. **Browse Vehicles**: View available cars and bikes
3. **Select Vehicles**: Choose one or more vehicles to rent
4. **Set Dates**: Select rental start and end dates
5. **Confirm Rental**: Review and confirm your booking
6. **Manage Rentals**: View and return your rented vehicles

### For Administrators
1. **Login**: Use admin credentials to access dashboard
2. **Monitor Rentals**: View all active rentals and today's activity
3. **Track Revenue**: Monitor total revenue and statistics
4. **Manage Returns**: Mark vehicles as returned when needed

## Database Schema

### Users Table
- `id`: Primary key
- `username`: Unique username
- `email`: Unique email address
- `phone`: Phone number
- `password_hash`: Encrypted password
- `is_admin`: Admin flag
- `created_at`: Account creation timestamp

### Vehicles Table
- `id`: Primary key
- `name`: Vehicle name
- `model`: Vehicle model
- `vehicle_type`: 'car' or 'bike'
- `mileage`: Fuel efficiency
- `price_per_day`: Daily rental rate
- `image_url`: Vehicle image URL
- `is_available`: Availability status
- `created_at`: Vehicle addition timestamp

### Rentals Table
- `id`: Primary key
- `user_id`: Foreign key to users
- `vehicle_id`: Foreign key to vehicles
- `start_date`: Rental start date
- `end_date`: Rental end date
- `total_price`: Total rental cost
- `is_returned`: Return status
- `created_at`: Rental creation timestamp

## API Endpoints

- `GET /`: Home page
- `GET/POST /login`: User login
- `GET/POST /signup`: User registration
- `GET /logout`: User logout
- `GET /vehicle-selection`: Browse vehicles
- `GET/POST /rental-details`: Rental details form
- `POST /confirm-rental`: Confirm rental booking
- `GET /my-rentals`: User's rental history
- `GET /return-vehicle/<id>`: Return a vehicle
- `GET /admin`: Admin dashboard
- `GET /api/vehicles`: API for vehicle search

## Features in Detail

### Search & Filter
- Real-time search by vehicle name or model
- Filter by vehicle type (cars/bikes)
- Clear filters functionality

### Responsive Design
- Mobile-first approach
- Bootstrap 5 grid system
- Touch-friendly interface
- Optimized for all screen sizes

### Error Handling
- Form validation
- Duplicate user prevention
- Date validation
- Vehicle availability checks

### Security
- Password hashing with Werkzeug
- CSRF protection
- Input validation
- Admin access control

## Customization

### Adding New Vehicles
Edit the `sample_vehicles` list in `app.py` to add more vehicles:

```python
Vehicle(name='New Car', model='2024', vehicle_type='car', 
        mileage='30 MPG', price_per_day=60.0, 
        image_url='https://example.com/image.jpg')
```

### Changing Database
To use MySQL or PostgreSQL, update the `SQLALCHEMY_DATABASE_URI` in `app.py`:

```python
# For MySQL
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://user:password@localhost/rental_db'

# For PostgreSQL
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://user:password@localhost/rental_db'
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## License

This project is open source and available under the MIT License.

## Support

For support or questions, please open an issue in the repository.
