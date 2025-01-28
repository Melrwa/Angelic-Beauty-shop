from sqlalchemy import Enum
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy_serializer import SerializerMixin
from config import db, bcrypt

class User(db.Model, SerializerMixin):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    username = db.Column(db.String(50), nullable=False, unique=True, index=True)
    email = db.Column(db.String(100), nullable=False, unique=True, index=True)
    _password_hash = db.Column(db.String(255), nullable=False)
    gender = db.Column(Enum('male', 'female', 'other', name='gender_enum'), nullable=True)
    picture = db.Column(db.String, nullable=True, default='image_url')
    role = db.Column(Enum('user', 'admin', name='role_enum'), default='user', nullable=False)

    # Hybrid property for password hashing
    @hybrid_property
    def password_hash(self):
        return self._password_hash

    @password_hash.setter
    def password_hash(self, plaintext_password):
        self._password_hash = bcrypt.generate_password_hash(plaintext_password).decode('utf-8')

    def check_password(self, plaintext_password):
        return bcrypt.check_password_hash(self._password_hash, plaintext_password)
    
    @classmethod
    def validate_uniqueness(cls, email, username):
        if cls.query.filter_by(email=email).first():
            raise ValueError("Email is already registered")
        if cls.query.filter_by(username=username).first():
            raise ValueError("Username is already taken")
        
    
