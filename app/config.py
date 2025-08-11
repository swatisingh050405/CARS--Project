import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY', 'fallback-secret')

    # Get and normalize DB URL (supports PostgreSQL + MySQL)
    db_url = os.environ.get('DATABASE_URL')

    if db_url:
        # Fix Heroku postgres:// -> postgresql://
        if db_url.startswith("postgres://"):
            db_url = db_url.replace("postgres://", "postgresql://", 1)

        # Ensure MySQL URLs have a driver specified
        elif db_url.startswith("mysql://"):
            db_url = db_url.replace("mysql://", "mysql+pymysql://", 1)

    SQLALCHEMY_DATABASE_URI = db_url
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # File upload location
    UPLOAD_FOLDER = 'app/static/uploads'
