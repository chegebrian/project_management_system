import os

# Get the absolute path of the directory containing this file
basedir = os.path.abspath(os.path.dirname(__file__))


class Config:
    """
    Configuration class for Flask application.
    Stores secret keys, database URI, and SQLAlchemy settings.
    """
    
    # Secret key used by Flask for session management, CSRF protection, etc.
    # Defaults to "dev-secret-change-me" if not set in environment variables.
    SECRET_KEY = os.environ.get("SECRET_KEY", "dev-secret-change-me")
    
    # Database URI for SQLAlchemy
    # Uses DATABASE_URL environment variable if set, otherwise defaults to a local SQLite database.
    SQLALCHEMY_DATABASE_URI = os.environ.get(
        "DATABASE_URL",
        "sqlite:///" + os.path.join(basedir, "database.db"),
    )
    
    # Disable Flask-SQLAlchemy event system to save resources.
    # Set to True only if you need it (usually not needed in most apps).
    SQLALCHEMY_TRACK_MODIFICATIONS = False