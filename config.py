# config.py
import os

# Secret key for session management
SECRET_KEY = os.getenv("SECRET_KEY", "super_secret_key")

# PostgreSQL database configuration
# Format: postgresql://username:password@host:port/database
SQLALCHEMY_DATABASE_URI = os.getenv(
    "DATABASE_URL",
    "postgresql://maturity_level_user:MikXlc4b9WxPlU48pJe13aofgti2Vo6S@dpg-d5rs5fvgi27c73bnh7u0-a/maturity_level"
)

# Disable track modifications to save resources
SQLALCHEMY_TRACK_MODIFICATIONS = False

