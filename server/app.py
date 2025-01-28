#!/usr/bin/env python3

from datetime import timedelta

from flask import request, session, jsonify, make_response
from flask_restful import Resource
from flask_jwt_extended import create_access_token, jwt_required, set_access_cookies, unset_jwt_cookies, get_jwt_identity
from config import app, db, api, avatar
from models import User
from utils import role_required
from sqlalchemy.exc import IntegrityError
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
    @jwt_required()
    def get(self):
        # Get the user ID or other details from the JWT
        user_id = get_jwt_identity()
        return {
            "message": "Session active",
            "user_id": user_id,
        }, 200



class Login(Resource):
    def post(self):
        data = request.json
        user = User.query.filter_by(username=data['username']).first()

        if user and user.check_password(data['password']):
            # Create a JWT with the user ID as identity and role in custom claims
            access_token = create_access_token(
                identity=str(user.id),  # Use user ID as a string for identity
                additional_claims={"role": user.role}  # Add role to JWT claims
            )

            # Create a response with the access token set in cookies
            response = jsonify({"message": "Login successful"})
            set_access_cookies(response, access_token)
            return response

        # Return an error for invalid credentials
        return {"message": "Invalid credentials"}, 401
    
    


class Logout(Resource):
    def post(self):
        response = jsonify({"message": "Logout successful"})
        unset_jwt_cookies(response)
        return response

class AdminOnly(Resource):
    @role_required('admin')
    def get(self):
        return {"message": "Welcome, Admin!"}, 200
    

class UserOnlyEndpoint(Resource):
    @role_required('user')
    def get(self):
        return {"message": "Welcome, User!"}, 200

api.add_resource(ClearSession, '/clear_session')
api.add_resource(Signup, '/signup')
api.add_resource(CheckSession, '/check_session')
api.add_resource(Login, '/login')
api.add_resource(Logout, '/logout')
api.add_resource(AdminOnly, '/admin-only')
api.add_resource(UserOnlyEndpoint, '/user-only')

if __name__ == '__main__':
    app.run(port=5555, debug=True)
