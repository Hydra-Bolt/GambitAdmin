"""
User Authentication utilities for the Gambit API.
Handles JWT token validation and role-based access control for users.
"""

import logging
from functools import wraps

from flask import jsonify, g, request, redirect, url_for
from flask_jwt_extended import verify_jwt_in_request, get_jwt_identity, jwt_required

from models import UserModel

logger = logging.getLogger(__name__)

def require_user_role(role):
    """Decorator to check if user has the required role"""
    def decorator(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            # First verify JWT is valid
            verify_jwt_in_request()
            
            # Get user ID from token
            user_id = get_jwt_identity()
            
            # Convert user_id back to integer if it's a string
            if isinstance(user_id, str):
                user_id = int(user_id)
                
            # Get user from database
            user = UserModel.query.get(user_id)
            
            if not user:
                return jsonify({"success": False, "message": "Invalid user account"}), 401
            
            if user.status != 'active':
                return jsonify({"success": False, "message": "Account is deactivated or suspended"}), 403
            
            # Store user for potential use in the view function
            g.user = user
            
            # Check role (special case for 'any' which allows any authenticated user)
            if role == 'any' or user.role == role:
                return fn(*args, **kwargs)
            
            return jsonify({
                "success": False, 
                "message": f"Access denied: requires {role} role"
            }), 403
        
        return wrapper
    
    return decorator

def user_jwt_required(fn):
    """Decorator to check if user is authenticated for dashboard routes"""
    @wraps(fn)
    def decorated_function(*args, **kwargs):
        try:
            # Skip authentication check for login/signup pages and static files
            if request.path in ['/user/login', '/user/signup'] or request.path.startswith('/static/'):
                return fn(*args, **kwargs)

            # Verify JWT token
            verify_jwt_in_request()
            
            # Get user ID from token
            user_id = get_jwt_identity()
            
            # Convert user_id back to integer if it's a string
            if isinstance(user_id, str):
                user_id = int(user_id)
                
            # Get user from database
            user = UserModel.query.get(user_id)
            
            if not user:
                return redirect(url_for('user.login'))
            
            if user.status != 'active':
                return jsonify({"success": False, "message": "Account is deactivated or suspended"}), 403
            
            # Store user for potential use in the view function
            g.user = user
            
            return fn(*args, **kwargs)
            
        except Exception as e:
            logger.error(f"Authentication error: {str(e)}")
            return redirect(url_for('user.login'))
    
    return decorated_function

def is_premium_user():
    """Check if current user is a premium user"""
    try:
        # Get user ID from token
        user_id = get_jwt_identity()
        
        # Convert user_id back to integer if it's a string
        if isinstance(user_id, str):
            user_id = int(user_id)
            
        # Get user from database
        user = UserModel.query.get(user_id)
        
        if not user:
            return False
        
        return user.role == 'premium'
        
    except Exception:
        return False