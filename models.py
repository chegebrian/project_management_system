
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

class Unit(db.Model):
    """
    Represents a unit (apartment, office, etc.) within a property.
    Each unit can have a tenant, belong to a property, and have multiple payments.
    """
    
    # Primary key for the Unit table
    id = db.Column(db.Integer, primary_key=True)
    
    # Name of the unit (e.g., "Unit 1", "Apt 101")
    name = db.Column(db.String(64), nullable=False)
    
    # Indicates whether the unit is currently occupied by a tenant
    is_occupied = db.Column(db.Boolean, default=False)
    
    # Foreign key linking this unit to its parent Property
    property_id = db.Column(db.Integer, db.ForeignKey("property.id"), nullable=False)
    
    # ORM relationship to the Property model
    # - back_populates="units" allows bidirectional access (Property.units ↔ Unit.property)
    property = db.relationship("Property", back_populates="units")
    
    # One-to-one relationship to Tenant
    # - A unit can have at most one active tenant
    # - uselist=False ensures only a single Tenant object is returned, not a list
    tenant = db.relationship("Tenant", back_populates="unit", uselist=False)
    
    # One-to-many relationship to Payment
    # - back_populates="unit" allows Payment.unit to access this unit
    # - cascade="all, delete-orphan" ensures that if a Unit is deleted,
    #   all associated Payments are also deleted
    payments = db.relationship("Payment", back_populates="unit", cascade="all, delete-orphan")

class Tenant(db.Model):
    """
    Represents a tenant who rents a unit within a property.
    A tenant may occupy a unit and make multiple payments.
    """
    
    # Primary key for the Tenant table
    id = db.Column(db.Integer, primary_key=True)
    
    # Tenant's full name (required)
    full_name = db.Column(db.String(128), nullable=False)
    
    # Tenant's email address (optional)
    email = db.Column(db.String(120))
    
    # Tenant's phone number (optional)
    phone = db.Column(db.String(50))
    
    # Date the tenant moved in; defaults to current date/time
    move_in_date = db.Column(db.Date, default=datetime.utcnow)
    
    # Whether the tenant is currently active/occupying a unit
    active = db.Column(db.Boolean, default=True)
    
    # Foreign key linking this tenant to their assigned Unit
    unit_id = db.Column(db.Integer, db.ForeignKey("unit.id"))
    
    # One-to-one relationship to Unit
    # - back_populates="tenant" allows bidirectional access (Unit.tenant ↔ Tenant.unit)
    unit = db.relationship("Unit", back_populates="tenant")
    
    # One-to-many relationship to Payment
    # - back_populates="tenant" allows Payment.tenant to access this tenant
    # - cascade="all, delete-orphan" ensures that if a Tenant is deleted,
    #   all associated Payments are also deleted
    payments = db.relationship("Payment", back_populates="tenant", cascade="all, delete-orphan")