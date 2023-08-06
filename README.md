# BrewPrice.Watch Project Summary

## Introduction

BrewPrice.Watch is a web platform where users can view and compare beer prices across different pubs in various UK cities. Users can add new entries for pubs and beer prices, and there is an authentication system for user registration and login.

## Objectives:

1. **Landing Page:** A dropdown list allowing users to select a UK city (default to Edinburgh). Upon selection, display a list of pubs along with their beer prices, sorted from lowest to highest. Also, show the average price for each pub.

2. **Add Entry Feature:** Allow users to add new pubs and beer prices. Users can either select a pub from a list or add a new one, then input beer prices.

3. **User Authentication System:** Allow user registration and login. Only logged-in users can add new entries. 

4. **Email Verification:** Implement email verification for new accounts.

5. **Additional Features and Enhancements (TBD)**: Include additional features and optimizations for performance, security, and user experience.

## Current Status:

1. **Backend Setup:**
   - Flask app has been set up.
   - SQLite is configured as the database using Flask-SQLAlchemy.
   - Two database models: `Pub` (to store pub details) and `Price` (to store beer prices for each pub) have been defined.
   - Basic routes for the landing page and fetching pub data are created.
   - Dummy data has been added to the database for testing.

2. **Frontend:**
   - Landing page has been designed and implemented.
   - City dropdown list has been implemented and is populating pub names and beer prices.
   - The average price per pub is being displayed.

3. **User Authentication:**
   - User registration and login have been implemented.
   - Basic frontend templates for registration and login have been created.

4. **Email Verification:**
   - Postmark has been chosen as the email service provider.
   - A script has been developed for sending emails through Postmark.
   - Domain `brewprice.watch` has been acquired for the project.

## Next Steps:

1. **Complete Email Verification:**
   - Generate a unique token for email verification when a new user registers.
   - Send an email to the user with a link to verify their email.
   - Create an endpoint to handle email verification and mark the email as verified in the database.
   - Provide feedback to the user (e.g. "Email verified successfully").

2. **User Roles and Permissions:**
   - Define user roles (e.g. admin, regular user) and implement permissions (e.g. only admin can approve new pubs).

3. **Adding Entries:**
   - Implement the functionality for logged-in users to add entries for new pubs and beer prices.

4. **Enhancements and Optimization:**
   - Implement error handling and user feedback mechanisms.
   - Ensure mobile responsiveness.
   - Optimize for performance and security.

5. **Deployment:**
   - Consider deploying the application on a platform such as Heroku or AWS for public access.

6. **Documentation and Handover:**
   - Write documentation for the code, APIs, and user manual.
   - Handover the project to the maintenance team or the client.

## Notes for the Software Engineer:

The project is being developed using Flask, a Python web development framework. The database is SQLite, managed by SQLAlchemy ORM. The frontend is HTML, CSS, and JS.

To run the project locally, navigate to the project directory and use the following command:

```sh
python brewview/app.py
```

The Postmark API key is required for sending emails. Please set this as an environment variable or within the Flask app config.

You will also need to ensure that all required Python libraries are installed. These can be installed using pip:

```sh
pip install -r requirements.txt
```

Please review the code in brewview/app.py, and the templates in the brewview/templates directory to familiarize yourself with the project. The project is at a development stage and ongoing.
