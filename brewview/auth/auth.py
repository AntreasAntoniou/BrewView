# from flask import (
#     Blueprint,
#     flash,
#     redirect,
#     render_template,
#     request,
#     session,
#     url_for,
# )
# from werkzeug.security import generate_password_hash

# from brewview.app import User, db

# # Auth Blueprint
# auth_routes = Blueprint('auth', __name__)

# @auth_routes.route('/register', methods=['GET', 'POST'])
# def register():
#     if request.method == 'POST':
#         username = request.form.get('username')
#         email = request.form.get('email')
#         password = request.form.get('password')
        
#         # Check if a user already exists with this email
#         user = User.query.filter_by(email=email).first()
#         if user:
#             flash('Email address already exists', 'error')
#             return redirect(url_for('auth.register'))

#         # Create a new user
#         new_user = User(username=username, email=email, password_hash=generate_password_hash(password, method='sha256'))
#         db.session.add(new_user)
#         db.session.commit()
        
#         flash('Registration successful. Please log in.', 'success')
#         return redirect(url_for('auth.login'))
        

#     return render_template('auth/register.html')

# @auth_routes.route('/login', methods=['GET', 'POST'])
# def login():
#     if request.method == 'POST':
#         email = request.form.get('email')
#         password = request.form.get('password')
        
#         user = User.query.filter_by(email=email).first()
        
#         # Check if the user exists and the password is correct
#         if user and check_password_hash(user.password_hash, password):
#             session['user_id'] = user.id
#             flash('Login Successful', 'success')
#             return redirect(url_for('index'))  # Redirect to the main page or dashboard
#         else:
#             flash('Login Unsuccessful. Please check email and password', 'error')
#             return redirect(url_for('auth.login'))
#     return render_template('auth/login.html')
