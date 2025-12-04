# config.py
import os

# Secret key for session management
SECRET_KEY = os.getenv("SECRET_KEY", "super_secret_key")

# PostgreSQL database configuration
# Format: postgresql://username:password@host:port/database
SQLALCHEMY_DATABASE_URI = os.getenv(
    "DATABASE_URL",
    "postgresql://carbon_user:bhu123@localhost:5432/carbon_db"
)

# Disable track modifications to save resources
SQLALCHEMY_TRACK_MODIFICATIONS = False
