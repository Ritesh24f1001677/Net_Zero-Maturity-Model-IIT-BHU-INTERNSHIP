from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from datetime import datetime
import json
from sqlalchemy.dialects.postgresql import JSONB

db = SQLAlchemy()

class User(UserMixin, db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(200), unique=True, nullable=False)
    password_hash = db.Column(db.String(300))
    name = db.Column(db.String(200))
    created_at = db.Column(db.DateTime, nullable=False, server_default=db.func.now())

    # UI preferences + onboarding
    language = db.Column(db.String(10), nullable=False, server_default="en")
    onboard_complete = db.Column(db.Boolean, nullable=False, server_default="false")

    step1 = db.Column(db.String(200))
    step2 = db.Column(db.String(200))
    step3 = db.Column(db.Integer)
    step4 = db.Column(db.String(200))
    step5 = db.Column(db.String(300))

    responses = db.relationship("Response", backref="user", lazy=True)


class Response(db.Model):
    __tablename__ = "responses"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    level = db.Column(db.Integer, nullable=False)
    score = db.Column(db.Float, nullable=False, default=0.0)
    maturity_level = db.Column(db.Integer, nullable=False, default=1)
    details = db.Column(JSONB)  # Store details as JSONB in PostgreSQL
    attempt_number = db.Column(db.Integer, nullable=False, default=1)
    created_at = db.Column(db.DateTime, nullable=False, server_default=db.func.now())

    def details_json(self):
        try:
            if self.details:
                return self.details
            return {}
        except:
            return {}


# --------------------------------------------------
# ✅ Admin Table
# --------------------------------------------------

class Admin(db.Model):
    __tablename__ = "admins"

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True, nullable=False)
    password_hash = db.Column(db.String(300), nullable=False)

    def __repr__(self):
        return f"<Admin {self.username}>"
