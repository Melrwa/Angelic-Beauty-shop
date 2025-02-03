from datetime import timedelta
from flask import Flask
from flask_bcrypt import Bcrypt
from flask_jwt_extended import JWTManager
from flask_migrate import Migrate
from flask_restful import Api
from flask_sqlalchemy import SQLAlchemy
from dotenv import load_dotenv
from flask_cors import CORS
import os

# Load environment variables from .env
load_dotenv()

app = Flask(__name__)

# Deployment Configuration
app.config['DEBUG'] = False  # Turn off debug mode in production
app.secret_key = os.getenv("SECRET_KEY", "default_secret_key")  # Default fallback

# DATABASE CONFIGURATION
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv("SQLALCHEMY_DATABASE_URI", 'sqlite:///angelic.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# JWT Configurations (More Secure for Deployment)
app.config['JWT_SECRET_KEY'] = os.getenv("JWT_SECRET_KEY", "default_jwt_secret_key")  # Fallback
app.config["JWT_ACCESS_TOKEN_EXPIRES"] = timedelta(minutes=15)
app.config["JWT_TOKEN_LOCATION"] = ["cookies"]  # Store JWT in cookies
app.config["JWT_COOKIE_SECURE"] = True  # Set to True for HTTPS in production
app.config["JWT_COOKIE_CSRF_PROTECT"] = True  # Enable CSRF protection for production

# CORS (Temporarily allow all origins for deployment)
CORS(app, resources={r"/*": {"origins": "*"}}, supports_credentials=True, allow_headers=["Content-Type", "Authorization"])

# Initialize Flask Extensions
db = SQLAlchemy()
db.init_app(app)

bcrypt = Bcrypt(app)
migrate = Migrate(app, db)
api = Api(app)
jwt = JWTManager(app)

# Default Avatar
avatar = "https://res.cloudinary.com/dmnytetf0/image/upload/v1738094972/default-profile-picture-avatar-photo-placeholder-vector-illustration-default-profile-picture-avatar-photo-placeholder-vector-189495158_lgcjxv.jpg"
