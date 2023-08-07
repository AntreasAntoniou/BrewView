from werkzeug.security import generate_password_hash

from brewview.app import (  # Assuming app and db are defined in your app.py
    User,
    app,
    db,
)

# Enter the app context
with app.app_context():

    # Details for the first admin user
    username = "su"
    email = "su@brewprice.watch"
    password = "supersecurepassword"  # Change this to a secure password

    # Hash the password
    password_hash = generate_password_hash(password)

    # Create the user object
    admin_user = User(
        username=username,
        email=email,
        password_hash=password_hash,
        email_verified=True,  # Assuming the first admin's email is verified
        role="admin"  # Assigning admin role
    )

    # Add the user to the database
    db.session.add(admin_user)
    db.session.commit()

    print(f"Admin user {username} created successfully!")
