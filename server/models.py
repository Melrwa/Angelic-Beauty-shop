


from sqlalchemy.ext.associationproxy import association_proxy
from datetime import datetime
from sqlalchemy import Enum, func
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy_serializer import SerializerMixin 
from config import db, bcrypt

# User Model
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

    # Relationships
    reviews = db.relationship('Review', back_populates='client', cascade='all, delete-orphan')
    transactions = db.relationship('Transaction', back_populates='client', cascade='all, delete-orphan')

    # Password hashing
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

    def __repr__(self):
        return f"<User {self.name}>"

# Association table for Staff and Services
class StaffService(db.Model):
    __tablename__ = 'staff_service'
    staff_id = db.Column(db.Integer, db.ForeignKey('staff.id'), primary_key=True)
    service_id = db.Column(db.Integer, db.ForeignKey('services.id'), primary_key=True)

    # Relationships
    staff = db.relationship('Staff', back_populates='staff_services')
    service = db.relationship('Service', back_populates='service_staff')

    def __repr__(self):
        return f"<StaffService staff_id={self.staff_id} service_id={self.service_id}>"

# Staff Model
class Staff(db.Model, SerializerMixin):
    __tablename__ = 'staff'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    picture = db.Column(db.String, nullable=True, default='image_url')
    gender = db.Column(Enum('male', 'female', 'other', name='gender_enum'), nullable=True)

    # Relationships
    staff_services = db.relationship('StaffService', back_populates='staff', cascade='all, delete-orphan')
    services = association_proxy('staff_services', 'service')
    reviews = db.relationship('Review', back_populates='staff', cascade='all, delete-orphan')
    transactions = db.relationship('Transaction', back_populates='staff', cascade='all, delete-orphan')

    @hybrid_property
    def average_rating(self):
        """Dynamically calculate the staff's average rating."""
        if not self.reviews or len(self.reviews) == 0:
            return None  # No reviews yet
        return sum(review.rating for review in self.reviews) / len(self.reviews)

    def __repr__(self):
        return f"<Staff {self.name}>"

# Service Model
class Service(db.Model, SerializerMixin):
    __tablename__ = 'services'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    picture = db.Column(db.String, nullable=True, default='image_url')
    price = db.Column(db.Float, nullable=False)
    time_taken = db.Column(db.Float, nullable=False)  # Time in hours

    # Relationships
    service_staff = db.relationship('StaffService', back_populates='service', cascade='all, delete-orphan')
    staff = association_proxy('service_staff', 'staff')
    transactions = db.relationship('Transaction', back_populates='service', cascade='all, delete-orphan')

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "picture": self.picture,
            "price": self.price,
            "time_taken": self.time_taken
        }

    def __repr__(self):
        return f"<Service {self.name}>"

# Review Model
class Review(db.Model, SerializerMixin):
    __tablename__ = 'reviews'

    id = db.Column(db.Integer, primary_key=True)
    staff_id = db.Column(db.Integer, db.ForeignKey('staff.id'))
    client_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    rating = db.Column(db.Float, nullable=False)
    review = db.Column(db.Text, nullable=True)

    # Relationships
    staff = db.relationship('Staff', back_populates='reviews')
    client = db.relationship('User', back_populates='reviews')

    def __repr__(self):
        return f"<Review {self.rating} - {self.staff.name}>"

# Transaction Model
class Transaction(db.Model, SerializerMixin):
    __tablename__ = 'transactions'

    id = db.Column(db.Integer, primary_key=True)
    service_id = db.Column(db.Integer, db.ForeignKey('services.id'))
    staff_id = db.Column(db.Integer, db.ForeignKey('staff.id'))
    client_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    amount_paid = db.Column(db.Float, nullable=False)
    time_taken = db.Column(db.Float, nullable=False)  # Hours
    booking_time = db.Column(db.DateTime, default=datetime.utcnow)
    completed_at = db.Column(db.DateTime, nullable=True)

    # Relationships
    service = db.relationship('Service', back_populates='transactions')
    staff = db.relationship('Staff', back_populates='transactions')
    client = db.relationship('User', back_populates='transactions')

    def __repr__(self):
        return f"<Transaction {self.service.name} by {self.staff.name}>"

