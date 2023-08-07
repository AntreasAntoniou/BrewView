import random

from werkzeug.security import generate_password_hash

from brewview.app import Evidence, Price, Pub, User, UserVote, app, db

# This should be run within the Flask application context
# Example: 'flask shell' then 'run populate_dummy_data.py'

# Enter the app context
with app.app_context():
    # Check if the tables are empty
    
        # Adding dummy users
        dummy_users = [
            {"username": "john_doe", "email": "john_doe@example.com", "password": "password123", "role": "user"},
            {"username": "jane_doe", "email": "jane_doe@example.com", "password": "password123", "role": "user"},
            {"username": "admin", "email": "admin@example.com", "password": "admin123", "role": "admin"},
        ]

        for user_data in dummy_users:
            user = User(
                username=user_data["username"],
                email=user_data["email"],
                password_hash=generate_password_hash(user_data["password"]),  # Hashing password
                role=user_data["role"]
            )
            db.session.add(user)

        # Adding dummy pubs
        dummy_pubs = [
            {"name": "The Red Lion", "city": "London"},
            {"name": "The Blue Boar", "city": "Oxford"},
            {"name": "The Green Dragon", "city": "Cambridge"},
        ]

        for pub_data in dummy_pubs:
            pub = Pub(
                name=pub_data["name"],
                city=pub_data["city"]
            )
            db.session.add(pub)

        # Commit user and pub changes
        db.session.commit()

        # Adding dummy prices
        beer_types = ["Guinness", "Tennant", "IPA"]
        pubs = Pub.query.all()

        for pub in pubs:
            for beer_type in beer_types:
                price = Price(
                    beer_type=beer_type,
                    price=round(random.uniform(3, 6), 2),  # Random price between 3 and 6 rounded to 2 decimal places
                    pub_id=pub.id,
                    score=random.randint(-5, 5)  # Random score between -5 and 5
                )
                db.session.add(price)

        # Commit price changes
        db.session.commit()

        # Adding dummy evidences
        prices = Price.query.all()
        users = User.query.all()

        for price in prices:
            evidence = Evidence(
                pub_id=price.pub_id,
                price_id=price.id,
                user_id=random.choice(users).id,
                evidence_url='http://example.com/evidence.jpg',
                upvotes=random.randint(0, 10),
                downvotes=random.randint(0, 10)
            )
            db.session.add(evidence)

        # Commit evidence changes
        db.session.commit()

        # Adding dummy user votes
        evidences = Evidence.query.all()
        for evidence in evidences:
            user_vote = UserVote(
                user_id=random.choice(users).id,
                evidence_id=evidence.id,
                vote=random.choice([True, False])
            )
            db.session.add(user_vote)

        # Commit user votes
        db.session.commit()

    