
# Lets you work with timestamps
from datetime import datetime

# Adds methods like is_authenticated, is_active, and get_id() to your User model so Flask-Login can work smoothly.
from flask_login import UserMixin

# Lets you define Python classes as database tables and query them easily.
from flask_sqlalchemy import SQLAlchemy

# Safely store and verify passwords
from werkzeug.security import check_password_hash, generate_password_hash


# Initialize the SQLAlchemy ORM instance
# This will be used to define models and interact with the database
db = SQLAlchemy()


class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    role = db.Column(db.String(20), default="manager")

    
    def set_password(self, password: str) -> None:
        """
            Hashes a plain-text password and stores it in the user object.

            Args:
                password (str): The plain-text password to hash and store.

            Returns:
                None
        """
        self.password_hash = generate_password_hash(password)

    def check_password(self, password: str) -> bool:

        """
            Verifies if a given plain-text password matches the stored password hash.

            Args:
                password (str): The plain-text password to check.

            Returns:
                bool: True if the password matches, False otherwise.
        """
        return check_password_hash(self.password_hash, password)
    
class Property(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(128), nullable=False)
    location = db.Column(db.String(255), nullable=False)
    property_type = db.Column(db.String(50), nullable=False)
    num_units = db.Column(db.Integer, nullable=False, default=0)
    rent_price = db.Column(db.Float, nullable=False, default=0.0)

    # Define a one-to-many relationship between Property and Unit.
    # back_populates allows you to navigate the relationship from both sides (Property → Units, Unit → Property).
    # cascade="all, delete-orphan" ensures database integrity automatically.
    units = db.relationship("Unit", back_populates="property", cascade="all, delete-orphan")
    payments = db.relationship("Payment", back_populates="property", cascade="all, delete-orphan")