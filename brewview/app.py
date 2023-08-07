# brewview/app.py

import datetime
import secrets  # Import for token generation
from functools import wraps

from flask import (
    Blueprint,
    Flask,
    abort,
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
app.secret_key = 'yoursecretkey'  # Choose a secret key here. This should be a random and secure string in production.

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
    score = db.Column(db.Integer, default=0)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    email_verified = db.Column(db.Boolean, default=False)
    email_verification_token = db.Column(db.String(128), nullable=True)  # Added column for email verification token
    interacted_pubs = db.Column(db.PickleType, default={})
    role = db.Column(db.String(80), default='user')  # Added role field

# Add a new model for Evidence
class Evidence(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    pub_id = db.Column(db.Integer, db.ForeignKey('pub.id'), nullable=False)
    price_id = db.Column(db.Integer, db.ForeignKey('price.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    price = db.relationship('Price', backref=db.backref('evidences', lazy=True))
    evidence_url = db.Column(db.String(256), nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    upvotes = db.Column(db.Integer, default=0)
    downvotes = db.Column(db.Integer, default=0)
    
class UserVote(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    evidence_id = db.Column(db.Integer, db.ForeignKey('evidence.id'), nullable=False)
    vote = db.Column(db.Boolean, nullable=False) # True for upvote, False for downvote


auth_routes = Blueprint('auth', __name__)

@auth_routes.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')

        user = User.query.filter_by(email=email).first()
        if user:
            # If the user's email is not verified, resend the verification email
            if not user.email_verified:
                email_verification_token = secrets.token_urlsafe(16)
                user.email_verification_token = email_verification_token
                db.session.commit()

                # Resend verification email
                verification_link = url_for('auth.verify_email', token=email_verification_token, _external=True)
                send_email(email, 'Email Verification for BrewPrice.Watch', 'Click the link below to verify your email:', verification_link)
                
                flash('A new verification email has been sent. Please check your email.', 'info')
                return render_template('auth/register.html')
            else:
                flash('Email address already registered', 'error')
                return render_template('auth/register.html')

        # Generate email verification token
        email_verification_token = secrets.token_urlsafe(16)

        # Hash the password and create a new user
        user = User(
            username=username,
            email=email,
            password_hash=generate_password_hash(password),
            email_verification_token=email_verification_token,  # Store the generated token
        )
        db.session.add(user)
        db.session.commit()

        # Send verification email
        verification_link = url_for('auth.verify_email', token=email_verification_token, _external=True)
        send_email(email, 'Email Verification for BrewPrice.Watch', 'Click the link below to verify your email:', verification_link)
        
        flash('Registration successful! Please check your email to verify your account.', 'success')
        return redirect(url_for('index'))

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

@auth_routes.route('/verify_email/<token>')
def verify_email(token):
    user = User.query.filter_by(email_verification_token=token).first()
    if not user:
        return render_template('auth/email_verification.html', verification_status='failure')
    user.email_verified = True
    user.email_verification_token = None
    db.session.commit()
    return render_template('auth/email_verification.html', verification_status='success')

@auth_routes.route('/resend_verification', methods=['GET', 'POST'])
def resend_verification():
    if request.method == 'POST':
        email = request.form.get('email')
        user = User.query.filter_by(email=email).first()

        if user and not user.email_verified:
            email_verification_token = secrets.token_urlsafe(16)
            user.email_verification_token = email_verification_token
            db.session.commit()

            # Resend verification email
            verification_link = url_for('auth.verify_email', token=email_verification_token, _external=True)
            send_email(email, 'Email Verification for BrewPrice.Watch', 'Click the link below to verify your email:', verification_link)

            flash('Verification email has been resent. Please check your email.', 'info')
        else:
            flash('Email address not found or already verified.', 'error')

    return render_template('auth/resend_verification.html')


@auth_routes.route('/auth/logout')
def logout():
    # Remove user_id from the session
    session.pop('user_id', None)
    flash('You have been logged out.', 'success')
    return redirect(url_for('index'))


# Register the blueprint
app.register_blueprint(auth_routes, url_prefix='/auth')

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Please log in to view this page.', 'danger')
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated_function

@app.route('/upload_evidence', methods=['POST'])
@login_required
def upload_evidence():
    pub_id = request.form.get('pub_id')
    price_id = request.form.get('price_id')
    evidence_url = request.form.get('evidence_url')
    
    # Create a new evidence record
    new_evidence = Evidence(pub_id=pub_id, price_id=price_id, user_id=session['user_id'], evidence_url=evidence_url)
    db.session.add(new_evidence)
    db.session.commit()

    flash('Evidence uploaded successfully!', 'success')
    return redirect(url_for('index'))

@app.route('/pub/<int:pub_id>', methods=['GET'])
@login_required
def pub_details(pub_id):
    pub = Pub.query.get(pub_id)
    evidence_records = Evidence.query.filter_by(pub_id=pub_id).all()
    return render_template('pub_details.html', pub=pub, evidence_records=evidence_records)

@app.route('/upvote/<int:evidence_id>', methods=['POST'])
@login_required
def upvote(evidence_id):
    # Fetch the evidence
    evidence = db.session.get(Evidence, evidence_id)

    
    # Check if the evidence exists
    if evidence is None:
        flash('Evidence not found!', 'error')
        return redirect(url_for('index'))

    # Check if the user has already voted
    user_vote = UserVote.query.filter_by(user_id=session['user_id'], evidence_id=evidence_id).first()
    
    if user_vote:
        # User has already voted. Update their choice
        if user_vote.vote == False:
            # This was previously a downvote, so increment the score by 2
            evidence.price.score += 2
            evidence.upvotes += 1
            evidence.downvotes -= 1
            user_vote.vote = True
    else:
        # This is a new vote
        evidence.upvotes += 1
        evidence.price.score += 1
        new_vote = UserVote(user_id=session['user_id'], evidence_id=evidence_id, vote=True)
        db.session.add(new_vote)
    
    # Commit changes
    db.session.commit()
    
    flash('Upvoted successfully!', 'success')
    return redirect(url_for('index'))


@app.route('/downvote/<int:evidence_id>', methods=['POST'])
@login_required
def downvote(evidence_id):
    # Fetch the evidence
    evidence = db.session.get(Evidence, evidence_id)

    
    # Check if the user has already voted
    user_vote = UserVote.query.filter_by(user_id=session['user_id'], evidence_id=evidence_id).first()
    
    if user_vote:
        # User has already voted. Update their choice
        if user_vote.vote == True:
            # This was previously an upvote, so decrement the score by 2
            evidence.price.score -= 2
            evidence.downvotes += 1
            evidence.upvotes -= 1
            user_vote.vote = False
    else:
        # This is a new vote
        evidence.downvotes += 1
        evidence.price.score -= 1
        new_vote = UserVote(user_id=session['user_id'], evidence_id=evidence_id, vote=False)
        db.session.add(new_vote)
    
    # Commit changes
    db.session.commit()
    
    flash('Downvoted successfully!', 'success')
    return redirect(url_for('index'))


# Define the routes
@app.route('/add_entry')
@login_required
def add_entry():
    pubs = Pub.query.all()
    cities = db.session.query(Pub.city).distinct().all()
    return render_template('add_entry.html', pubs=pubs, cities=cities)



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

@app.route('/fetch_pubs/<city>', methods=['GET'])
@login_required
def fetch_pubs(city):
    try:
        pubs = Pub.query.filter_by(city=city).all()

        # This dictionary will store user's votes
        user_votes = {}

        # Assuming current user ID is stored in the session
        current_user_id = session['user_id']

        # Fetch user's votes and populate the user_votes dictionary
        votes = UserVote.query.filter_by(user_id=current_user_id).all()
        for vote in votes:
            user_votes[vote.evidence_id] = vote.vote

        pub_data = []

        # Loop through each pub and construct data for frontend
        for pub in pubs:
            pub_prices = Price.query.filter_by(pub_id=pub.id).all()
            
            prices_data = []
            # Loop through each price and construct evidences data
            for price in pub_prices:
                evidences = Evidence.query.filter_by(price_id=price.id).all()
                evidences_data = []
                for ev in evidences:
                    vote = user_votes.get(ev.id)
                    evidences_data.append({
                        'id': ev.id,
                        'pub_id': ev.pub_id,
                        'price_id': ev.price_id,
                        'evidence_url': ev.evidence_url,
                        'upvotes': ev.upvotes,
                        'downvotes': ev.downvotes,
                        'user_vote': vote if vote else None
                    })
                
                # Append price data including evidences
                prices_data.append({
                    'id': price.id,
                    'beer_type': price.beer_type,
                    'price': price.price,
                    'score': price.score,
                    'evidences': evidences_data
                })

            # Append this pub's data including prices to the array to send to frontend
            pub_data.append({
                'id': pub.id,
                'name': pub.name,
                'city': pub.city,
                'prices': prices_data,
            })

        return jsonify(pub_data)

    except Exception as e:
        # Optionally, log the error message
        print(f"Error fetching pubs: {e}")
        return jsonify({'error': f'Something went wrong {e}'}), 500



@app.route('/')
def index():
    cities = db.session.query(Pub.city).distinct().all()
    return render_template('pages/landing_page.html', cities=cities)

# Decorator to restrict access to admins and mods
def admin_or_mod_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        user_id = session.get('user_id')
        user = db.session.query(User).get(user_id)

        if not user or user.role not in ['admin', 'mod']:
            abort(403)
        return f(*args, **kwargs)
    return decorated_function

@app.route("/admin/dashboard")
@admin_or_mod_required
def admin_dashboard():
    """Display the admin dashboard."""
    users = User.query.all()  # Fetch all users
    return render_template("admin_dashboard.html", users=users)

@app.route("/admin/manage_user/<int:user_id>", methods=['GET', 'POST'])
@admin_or_mod_required
def manage_user(user_id):
    """Admin/Mod manage users (update role or remove)."""
    user = db.session.query(User).get(user_id)

    if request.method == 'POST':
        new_role = request.form.get('role')
        if new_role:
            user.role = new_role
            db.session.commit()
        return redirect(url_for('admin_dashboard'))
    return render_template("manage_user.html", user=user)


import os

from postmarker.core import PostmarkClient


def send_email(to, subject, text_body, html_body):
    postmark = PostmarkClient(server_token=os.environ.get('POSTMARK_API_TOKEN'))
    
    postmark.emails.send(
        From="noreply@brewprice.watch",
        To=to,
        Subject=subject,
        HtmlBody=html_body,
        TextBody=text_body
    )



if __name__ == '__main__':
    with app.app_context():
        db.create_all()  # Create the database
    app.run(debug=True)
