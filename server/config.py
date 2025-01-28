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

# Load configuration from environment variables
app.config['DEBUG'] = True
app.secret_key = os.getenv("SECRET_KEY", "default_secret_key")  # Default fallback if not in .env
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv("SQLALCHEMY_DATABASE_URI", 'sqlite:///angelic.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['JWT_SECRET_KEY'] = os.getenv("JWT_SECRET_KEY", "default_jwt_secret_key")  # Fallback
CORS(app, resources={r"/api/*": {"origins": "http://localhost:3000"}})
# Configurations
# UPLOAD_FOLDER = './uploads'  # Set this to your desired folder for uploaded images
# ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
# app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER



db = SQLAlchemy()
db.init_app(app)  

bcrypt = Bcrypt(app)
migrate = Migrate(app, db)
api = Api(app)
jwt = JWTManager(app)

# def allowed_file(filename):
#     return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

avatar="https://res.cloudinary.com/dmnytetf0/image/upload/v1738094972/default-profile-picture-avatar-photo-placeholder-vector-illustration-default-profile-picture-avatar-photo-placeholder-vector-189495158_lgcjxv.jpg"