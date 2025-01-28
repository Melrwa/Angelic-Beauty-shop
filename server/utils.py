from flask_jwt_extended import get_jwt, jwt_required
from functools import wraps
from flask import jsonify

def role_required(required_role):
    def decorator(fn):
        @wraps(fn)
        @jwt_required()
        def wrapper(*args, **kwargs):
            claims = get_jwt()
            if claims.get('role') != required_role:
                return jsonify({"message": "Access forbidden: Insufficient role"}), 403
            return fn(*args, **kwargs)
        return wrapper
    return decorator
