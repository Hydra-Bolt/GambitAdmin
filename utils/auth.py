"""
Authentication utilities for the Gambit Admin API.
Handles JWT token generation, validation, and permission checks.
"""

import logging
from functools import wraps

from flask import jsonify, g
from flask_jwt_extended import create_access_token, verify_jwt_in_request, get_jwt_identity

from models import AdminModel, PermissionType

logger = logging.getLogger(__name__)

def create_auth_token(admin_id):
    """Create a JWT token for an admin user"""
    # Convert the admin_id to a string to avoid JWT subject validation error
    token = create_access_token(identity=str(admin_id))
    return token

def require_permission(permission):
    """Decorator to check if user has the required permission"""
    def decorator(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            # First verify JWT is valid
            verify_jwt_in_request()
            
            # Get admin ID from token
            admin_id = get_jwt_identity()
            
            # Convert admin_id back to integer if it's a string
            if isinstance(admin_id, str):
                admin_id = int(admin_id)
                
            # Get admin from database
            admin = AdminModel.query.get(admin_id)
            
            if not admin:
                return jsonify({"success": False, "message": "Invalid admin account"}), 401
            
            if not admin.is_active:
                return jsonify({"success": False, "message": "Account is deactivated"}), 403
            
            # Store admin for potential use in the view function
            g.admin = admin
            
            # If super admin or has the 'all' permission, allow access
            if admin.has_permission(PermissionType.ALL):
                return fn(*args, **kwargs)
            
            # Check specific permission
            if not admin.has_permission(permission):
                return jsonify({
                    "success": False, 
                    "message": f"You don't have the required permission: {permission}"
                }), 403
            
            return fn(*args, **kwargs)
        
        return wrapper
    
    return decorator

def register_jwt_error_handlers(jwt):
    """Register error handlers for JWT token errors"""
    
    @jwt.expired_token_loader
    def expired_token_callback(jwt_header, jwt_payload):
        return jsonify({
            "success": False,
            "message": "Token has expired",
            "error": "token_expired"
        }), 401
    
    @jwt.invalid_token_loader
    def invalid_token_callback(error):
        return jsonify({
            "success": False,
            "message": "Signature verification failed",
            "error": "invalid_token"
        }), 401
    
    @jwt.unauthorized_loader
    def missing_token_callback(error):
        return jsonify({
            "success": False,
            "message": "Authentication token is missing",
            "error": "missing_token"
        }), 401
    
    @jwt.needs_fresh_token_loader
    def token_not_fresh_callback(jwt_header, jwt_payload):
        return jsonify({
            "success": False,
            "message": "Fresh token required",
            "error": "fresh_token_required"
        }), 401
    
    @jwt.revoked_token_loader
    def revoked_token_callback(jwt_header, jwt_payload):
        return jsonify({
            "success": False,
            "message": "Token has been revoked",
            "error": "token_revoked"
        }), 401