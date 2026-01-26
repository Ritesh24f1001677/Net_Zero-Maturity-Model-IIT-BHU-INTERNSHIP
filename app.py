# app.py
from flask import Flask, session, redirect, url_for, flash
from flask_login import LoginManager
from dotenv import load_dotenv
from models import db, User, Admin
import os

# Load environment variables from .env
load_dotenv()


def create_app():
    app = Flask(__name__)
    
    # Load config from config.py
    app.config.from_object("config")

    # Ensure SECRET_KEY is set
    app.secret_key = os.getenv("SECRET_KEY", "supersecret123")

    # Initialize SQLAlchemy
    db.init_app(app)

    # Initialize LoginManager
    login_manager = LoginManager()
    login_manager.login_view = "login"  # default login route
    login_manager.init_app(app)

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    # ----------------------------------------------------
    # Admin helper decorator
    # ----------------------------------------------------
    from functools import wraps

    def admin_required(f):
        @wraps(f)
        def decorated(*args, **kwargs):
            if not session.get("is_admin"):
                flash("Admin login required", "danger")
                return redirect(url_for("admin_login"))
            return f(*args, **kwargs)
        return decorated

    # Make admin_required available for routes.py
    app.admin_required = admin_required

    # ----------------------------------------------------
    # Import and register routes
    # ----------------------------------------------------
    from routes import register_routes
    register_routes(app)

    # ----------------------------------------------------
    # CLI command to initialize DB
    # ----------------------------------------------------
    @app.cli.command("initdb")
    def initdb_command():
        """Initialize the PostgreSQL database"""
        with app.app_context():
            db.create_all()
            print("Database tables created successfully.")

    return app


app = create_app()

if __name__ == "__main__":
    with app.app_context():
        db.create_all()

    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))




