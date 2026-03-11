from datetime import date

from flask_wtf import FlaskForm
from wtforms import (
    BooleanField,
    DateField,
    FloatField,
    IntegerField,
    PasswordField,
    SelectField,
    StringField,
    SubmitField,
)
from wtforms.validators import DataRequired, Email, EqualTo, Length, NumberRange, Optional


# ------------------------
# User Authentication Forms
# ------------------------
class LoginForm(FlaskForm):
    # Input for username with a maximum of 64 characters
    username = StringField("Username", validators=[DataRequired(), Length(max=64)])
    
    # Password input (hidden characters)
    password = PasswordField("Password", validators=[DataRequired()])
    
    # Checkbox to remember user login session
    remember_me = BooleanField("Remember Me")
    
    # Submit button for the form
    submit = SubmitField("Login")


class RegistrationForm(FlaskForm):
    # Username field with validation
    username = StringField("Username", validators=[DataRequired(), Length(max=64)])
    
    # Email field with email format validation
    email = StringField("Email", validators=[DataRequired(), Email(), Length(max=120)])
    
    # Password field with minimum length requirement
    password = PasswordField("Password", validators=[DataRequired(), Length(min=6)])
    
    # Confirmation password field, must match 'password'
    password2 = PasswordField(
        "Confirm Password", validators=[DataRequired(), EqualTo("password")]
    )
    
    # Dropdown selection for user role
    role = SelectField(
        "Role",
        choices=[("admin", "Admin"), ("manager", "Property Manager")],
        default="manager",
    )
    
    # Submit button for registration
    submit = SubmitField("Register")


# ------------------------
# Property Management Forms
# ------------------------
class PropertyForm(FlaskForm):
    # Name of the property
    name = StringField("Property Name", validators=[DataRequired(), Length(max=128)])
    
    # Location/address of the property
    location = StringField("Location", validators=[DataRequired(), Length(max=255)])
    
    # Type of property (dropdown)
    property_type = SelectField(
        "Property Type",
        choices=[("Apartment", "Apartment"), ("House", "House"), ("Commercial", "Commercial")],
        validators=[DataRequired()],
    )
    
    # Number of units in the property
    num_units = IntegerField(
        "Number of Units", validators=[DataRequired(), NumberRange(min=0)]
    )
    
    # Rent per unit
    rent_price = FloatField(
        "Monthly Rent per Unit", validators=[DataRequired(), NumberRange(min=0)]
    )
    
    # Submit button to save property
    submit = SubmitField("Save")


class UnitForm(FlaskForm):
    # Name or number of the unit
    name = StringField("Unit Name/Number", validators=[DataRequired(), Length(max=64)])
    
    # Checkbox to indicate if the unit is occupied
    is_occupied = BooleanField("Occupied")
    
    # Submit button
    submit = SubmitField("Save")


class TenantForm(FlaskForm):
    # Full name of tenant
    full_name = StringField("Full Name", validators=[DataRequired(), Length(max=128)])
    
    # Optional email of tenant
    email = StringField("Email", validators=[Optional(), Email(), Length(max=120)])
    
    # Optional phone number
    phone = StringField("Phone", validators=[Optional(), Length(max=50)])
    
    # Move-in date, defaults to today
    move_in_date = DateField(
        "Move-in Date", validators=[Optional()], default=date.today, format="%Y-%m-%d"
    )
    
    # Dropdown to select which unit the tenant occupies
    unit_id = SelectField("Unit", coerce=int, validators=[Optional()])
    
    # Checkbox for active/inactive tenant
    active = BooleanField("Active", default=True)
    
    # Submit button
    submit = SubmitField("Save")


class PaymentForm(FlaskForm):
    # Tenant associated with the payment
    tenant_id = SelectField("Tenant", coerce=int, validators=[DataRequired()])
    
    # Unit associated with the payment
    unit_id = SelectField("Unit", coerce=int, validators=[DataRequired()])
    
    # Payment amount
    amount = FloatField("Amount", validators=[DataRequired(), NumberRange(min=0)])
    
    # Month of payment (1–12)
    month = IntegerField(
        "Month (1-12)", validators=[DataRequired(), NumberRange(min=1, max=12)]
    )
    
    # Year of payment
    year = IntegerField(
        "Year", validators=[DataRequired(), NumberRange(min=2000, max=2100)]
    )
    
    # Submit button to record payment
    submit = SubmitField("Record Payment")

