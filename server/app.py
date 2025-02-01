#!/usr/bin/env python3

from datetime import datetime, timedelta

from flask import request, session, jsonify, make_response
from flask_restful import Resource
from flask_jwt_extended import create_access_token, jwt_required, set_access_cookies, unset_jwt_cookies, get_jwt_identity
from config import app, db, api, avatar
from models import User, Staff, Service, StaffService, Review, Transaction

from utils import role_required
from sqlalchemy.exc import IntegrityError
from reports import ReportsResource
# import traceback
# from werkzeug.utils import secure_filename
# import os


class ClearSession(Resource):
    @jwt_required()
    def delete(self):
        session.clear()
        return {"message": "Session cleared"}, 200
    

class Signup(Resource):
    def post(self):
        try:
            data = request.json

            # Validate input fields
            required_fields = ["name", "username", "email", "password", "image"]
            missing_fields = [field for field in required_fields if field not in data]
            if missing_fields:
                return {"message": f"Missing fields: {', '.join(missing_fields)}"}, 400

            # Check if email and username are unique
            try:
                User.validate_uniqueness(email=data["email"], username=data["username"])
            except ValueError as e:
                return {"message": str(e)}, 400

            # Create a new user instance
            user = User(
                name=data["name"],
                username=data["username"],
                email=data["email"],
                gender=data.get("gender"),
                picture=data.get("image", avatar),
                role=data.get("role", "user"),
            )
            user.password_hash = data["password"]  # Hash password

            # Save the user to the database
            db.session.add(user)
            db.session.commit()

            # Create a JWT token
            access_token = create_access_token(
                identity=str(user.id),  # Pass user ID as a string
                expires_delta=timedelta(days=30)
            )

            # Create a response object
            response = make_response({"message": "User registered successfully"}, 201)

            # Set the token in an HTTP-only cookie
            set_access_cookies(response, access_token)

            return response

        except IntegrityError:
            db.session.rollback()
            return {"message": "A user with this email or username already exists"}, 409

        except KeyError as e:
            return {"message": f"Missing required field: {str(e)}"}, 400

        except Exception as e:
            return {"message": f"An error occurred: {str(e)}"}, 500
        


class CheckSession(Resource):
    @jwt_required(locations=["cookies"])  # Ensure JWT is read from cookies
    def get(self):
        current_user_id = get_jwt_identity()  # Extract user ID from JWT
        user = db.session.get(User, current_user_id)  

        if user:
            return {
                "id": user.id,
                "username": user.username,
                "email": user.email,
                "role": user.role  # Return role if needed
            }, 200

        return {"message": "User not found"}, 404



class Login(Resource):
    def post(self):
        data = request.json
        user = User.query.filter_by(username=data['username']).first()

        if user and user.check_password(data['password']):
            # Create JWT Token
            access_token = create_access_token(
                identity=str(user.id),
                additional_claims={"role": user.role}
            )

            # Create JSON response with token & user info
            response = jsonify({
                "message": "Login successful",
                "access_token": access_token,  # <-- Add this!
                "id": user.id,
                "username": user.username,
                "email": user.email,
                "role": user.role
            })

            # Set JWT token in cookies
            set_access_cookies(response, access_token)
            return response

        return {"message": "Invalid credentials"}, 401
    
    
class ServiceResource(Resource):
    def get(self):
        services = Service.query.all()
        return [service.to_dict() for service in services], 200

    def post(self):
        data = request.get_json()

        if not data or "name" not in data or "picture" not in data or "price" not in data or "time_taken" not in data:
            return {"message": "Missing required fields"}, 400

        try:
            new_service = Service(
                name=data["name"],
                picture=data["picture"],
                price=float(data["price"]),
                time_taken=float(data["time_taken"]),
            )
            db.session.add(new_service)
            db.session.commit()

            return {"message": "Service added successfully!", "service": new_service.to_dict()}, 201
        except Exception as e:
            return {"message": str(e)}, 500
        
    def patch(self, service_id):
        service = Service.query.get(service_id)
        if not service:
            return jsonify({"error": "Service not found"}), 404

        data = request.get_json()
        new_price = data.get("price")

        if new_price is None or new_price <= 0:
            return jsonify({"error": "Invalid price"}), 400

        service.price = new_price
        db.session.commit()

        return jsonify({"id": service.id, "price": service.price})

        

    @jwt_required()
    def delete(self, service_id):
        service = db.session.get(Service, service_id)  # Use Session.get() for SQLAlchemy 2.0+
        
        if not service:
            return {"message": "Service not found"}, 404

        db.session.delete(service)
        db.session.commit()
        return {"message": "Service deleted successfully"}, 200


class StaffResource(Resource):
    def get(self):
        # Fetch all staff members from the database
        staff_members = Staff.query.all()
        
        # Return the list of staff as a dictionary
        return [staff.to_dict() for staff in staff_members], 200
        
    @jwt_required()
    def post(self):
        data = request.get_json()
        
        required_fields = ["name", "picture", "gender", "role"]
        if not data or any(field not in data for field in required_fields):
            return {"message": "Missing required fields"}, 400

        # Ensure role is valid
        valid_roles = {"stylist", "barber", "spa_therapist"}
        role = data["role"].lower()
        if role not in valid_roles:
            return {"message": "Invalid role"}, 400

        try:
            new_staff = Staff(
                name=data["name"],
                picture=data["picture"],
                gender=data["gender"],
                role=role,  # Ensure it's correctly stored
            )
            db.session.add(new_staff)
            db.session.commit()

            return {"message": "Staff added successfully!", "staff": new_staff.to_dict()}, 201
        except Exception as e:
            return {"message": str(e)}, 500
        


    def delete(self, id):
        """Delete a staff member by ID."""
        staff = Staff.query.get(id)
        if not staff:
            return {"error": "Staff not found"}, 404

        db.session.delete(staff)
        db.session.commit()
        return {"message": "Staff deleted successfully"}, 200
class StaffReviewsResource(Resource):
    def get(self):
        staff_list = Staff.query.all()
        
        staff_reviews = []
        for staff in staff_list:
            reviews = [
                {
                    "rating": review.rating,
                    "review": review.review,
                    "client": review.client.name
                } 
                for review in staff.reviews
            ]
            
            staff_reviews.append({
                "id": staff.id,
                "name": staff.name,
                "picture": staff.picture,
                "role": staff.role,
                "average_rating": staff.average_rating,
                "reviews": reviews
            })

        return jsonify(staff_reviews)

# Register the resource
class TransactionResource(Resource):
    def get(self):
        transactions = Transaction.query.all()
        result = []

        for transaction in transactions:
            result.append({
                "id": transaction.id,
                "service_name": transaction.service.name if transaction.service else "Unknown",
                "staff_name": transaction.staff.name if transaction.staff else "Unknown",
                "client_name": transaction.client.name if transaction.client else transaction.client_name,
                "amount_paid": transaction.amount_paid,
                "time_taken": transaction.time_taken,
                "booking_time": transaction.booking_time.isoformat() if transaction.booking_time else None,
            })

        return jsonify(result)
    def post(self):
        data = request.get_json()

        # Extract fields
        service_id = data.get("service_id")
        staff_id = data.get("staff_id")
        client_id = data.get("client_id")  # Optional
        client_name = data.get("client_name")  # Required
        amount_paid = data.get("amount_paid")
        time_taken = data.get("time_taken")

        # Validate required fields
        if not service_id or not staff_id or not client_name or amount_paid is None or time_taken is None:
            return {"error": "Missing required fields"}, 400

        # Ensure service exists
        service = Service.query.get(service_id)
        if not service:
            return {"error": "Service not found"}, 404

        # Validate amount paid
        if amount_paid != service.price:
            return {"error": f"Incorrect amount. Expected: {service.price}, Received: {amount_paid}"}, 400

        # Ensure staff exists
        staff = Staff.query.get(staff_id)
        if not staff:
            return {"error": "Staff not found"}, 404

        # If client_id is provided, ensure it exists
        if client_id:
            client = User.query.get(client_id)
            if not client:
                return {"error": "Client not found"}, 404

        try:
            # Create new transaction
            new_transaction = Transaction(
                service_id=service_id,
                staff_id=staff_id,
                client_id=client_id if client_id else None,  # Optional
                client_name=client_name.strip(),  # Ensure not null
                amount_paid=amount_paid,
                time_taken=time_taken,
                booking_time=datetime.utcnow(),
            )

            db.session.add(new_transaction)
            db.session.commit()

            return {"message": "Transaction successfully added"}, 201

        except Exception as e:
            db.session.rollback()
            return {"error": str(e)}, 500

class Logout(Resource):
    def post(self):
        response = jsonify({"message": "Logout successful"})
        unset_jwt_cookies(response)
        return response



api.add_resource(ClearSession, '/clear_session')
api.add_resource(Signup, '/signup')
api.add_resource(CheckSession, '/check_session')
api.add_resource(Login, '/login')
api.add_resource(Logout, '/logout')
api.add_resource(ServiceResource, "/services", endpoint="services_list")  
api.add_resource(ServiceResource, "/services/<int:service_id>", endpoint="service_detail")  
api.add_resource(StaffResource, "/staff", "/staff/<int:id>")
api.add_resource(StaffReviewsResource, "/staff/reviews")
api.add_resource(TransactionResource, "/transactions")
api.add_resource(ReportsResource, "/reports")


if __name__ == '__main__':
    app.run(port=5555, debug=True)
