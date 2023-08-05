# brewview/app.py

from functools import wraps

from flask import (
    Blueprint,
    Flask,
    flash,
    jsonify,
    redirect,
    render_template,
    request,
    session,
    url_for,
)
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import check_password_hash, generate_password_hash

app = Flask(__name__)
app.secret_key = 'yoursecretkey' # Choose a secret key here. This should be a random and secure string in production.

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:////tmp/test.db'


# Initialize the database
db = SQLAlchemy(app)

# Define the database models
class Pub(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), nullable=False)
    city = db.Column(db.String(80), nullable=False)
    prices = db.relationship('Price', backref='pub', lazy=True)

class Price(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    beer_type = db.Column(db.String(80), nullable=False)
    price = db.Column(db.Float, nullable=False)
    pub_id = db.Column(db.Integer, db.ForeignKey('pub.id'), nullable=False)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    email_verified = db.Column(db.Boolean, default=False)

auth_routes = Blueprint('auth', __name__)

@auth_routes.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        
        # Check if a user already exists with this email
        user = User.query.filter_by(email=email).first()
        if user:
            flash('Email address already exists', 'error')
            return redirect(url_for('auth.register'))

        # Create a new user
        new_user = User(username=username, email=email, password_hash=generate_password_hash(password, method='scrypt'))
        db.session.add(new_user)
        db.session.commit()
        
        flash('Registration successful. Please log in.', 'success')
        return redirect(url_for('auth.login'))
        

    return render_template('auth/register.html')

@auth_routes.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        
        user = User.query.filter_by(email=email).first()
        
        # Check if the user exists and the password is correct
        if user and check_password_hash(user.password_hash, password):
            session['user_id'] = user.id
            flash('Login Successful', 'success')
            return redirect(url_for('index'))  # Redirect to the main page or dashboard
        else:
            flash('Login Unsuccessful. Please check email and password', 'error')
            return redirect(url_for('auth.login'))
    return render_template('auth/login.html')

# Register the blueprint
app.register_blueprint(auth_routes, url_prefix='/auth')

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Please log in to view this page.', 'danger')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function


# Define the routes
@app.route('/add_entry')
@login_required
def add_entry():
    pubs = Pub.query.all()
    cities = db.session.query(Pub.city).distinct().all()
    return render_template('add_entry.html', pubs=pubs, cities=cities)

@app.route('/auth/logout')
def logout():
    # Remove user_id from the session
    session.pop('user_id', None)
    flash('You have been logged out.', 'success')
    return redirect(url_for('index'))


@app.route('/submit_entry', methods=['POST'])
def submit_entry():
    # Extracting the form data
    pub_id = request.form.get('pub')
    new_pub_name = request.form.get('new_pub')
    city = request.form.get('city')
    guinness_price = request.form.get('guinness')
    tennant_price = request.form.get('tennant')
    ipa_price = request.form.get('ipa')
    
    # Adding a new pub or updating an existing one
    if new_pub_name:
        pub = Pub(name=new_pub_name, city=city)
        db.session.add(pub)
        db.session.commit()
        pub_id = pub.id
    elif pub_id:
        pub = Pub.query.get(pub_id)
        pub.city = city
        db.session.commit()
    
    # Adding the beer prices
    if guinness_price:
        guinness = Price(beer_type="Guinness", price=float(guinness_price), pub_id=pub_id)
        db.session.add(guinness)
    if tennant_price:
        tennant = Price(beer_type="Tennant", price=float(tennant_price), pub_id=pub_id)
        db.session.add(tennant)
    if ipa_price:
        ipa = Price(beer_type="IPA", price=float(ipa_price), pub_id=pub_id)
        db.session.add(ipa)
    
    # Commit changes to the database
    db.session.commit()

    # Redirect back to the landing page
    return redirect(url_for('index'))

@app.route('/fetch_pubs/<city>')
def fetch_pubs(city):
    pubs = Pub.query.filter_by(city=city).all()
    pub_data = []
    for pub in pubs:
        prices = {price.beer_type: price.price for price in pub.prices}
        pub_data.append({
            'name': pub.name,
            'guinness': prices.get('Guinness', 'N/A'),
            'tennant': prices.get('Tennant', 'N/A'),
            'ipa': prices.get('IPA', 'N/A')
        })
    return jsonify(pub_data)

@app.route('/')
def index():
    cities = db.session.query(Pub.city).distinct().all()
    return render_template('pages/landing_page.html', cities=cities)

# Start the app
if __name__ == '__main__':
    with app.app_context():
        db.create_all()  # Create the database
    app.run(debug=True)
