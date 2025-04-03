"""
Authentication routes for the Gambit Admin API.
Handles login, logout, and password management.
"""

from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import get_jwt_identity, jwt_required
from datetime import datetime
from models import AdminModel, db
from utils.auth import create_auth_token
from utils.response_formatter import format_response, format_error

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/test', methods=['GET'])
def test():
    """Test route to verify API is running"""
    return format_response({"message": "Auth API is working"})

@auth_bp.route('/test-jwt', methods=['GET'])
def test_jwt():
    """Test route to verify JWT authentication"""
    auth_header = request.headers.get('Authorization', '')
    
    # Add manual JWT verification for debugging
    if auth_header.startswith('Bearer '):
        token = auth_header.split(' ')[1]
        try:
            from flask_jwt_extended import decode_token
            decoded = decode_token(token)
            return format_response({
                "message": "JWT verification successful",
                "decoded": decoded,
                "auth_header": auth_header
            })
        except Exception as e:
            import traceback
            return format_response({
                "message": "JWT verification failed",
                "error": str(e),
                "traceback": traceback.format_exc(),
                "auth_header": auth_header
            })
    else:
        return format_response({
            "message": "No valid Bearer token found",
            "auth_header": auth_header
        })

@auth_bp.route('/login', methods=['POST'])
def login():
    """Login route for admin users"""
    try:
        data = request.get_json()
        
        if not data or not data.get('username') or not data.get('password'):
            return format_error("Missing username or password", status_code=400)
        
        # Find admin by username
        admin = AdminModel.query.filter_by(username=data['username']).first()
        
        # Check if admin exists and password is correct
        if not admin or not admin.check_password(data['password']):
            return format_error("Invalid username or password", status_code=401)
        
        # Check if account is active
        if not admin.is_active:
            return format_error("Your account has been deactivated", status_code=403)
        
        # Update last login time
        admin.last_login = datetime.now()
        db.session.commit()
        
        # Generate token
        token = create_auth_token(admin.id)
        
        return format_response({
            'token': token,
            'admin': admin.to_dict()
        })
    
    except Exception as e:
        return format_error(f"Login error: {str(e)}")

@auth_bp.route('/me', methods=['GET'])
@jwt_required()
def get_current_user():
    """Get current authenticated admin user"""
    try:
        admin_id = get_jwt_identity()
        # Convert admin_id back to integer if it's a string
        if isinstance(admin_id, str):
            admin_id = int(admin_id)
        
        admin = AdminModel.query.get(admin_id)
        
        if not admin:
            return format_error("Invalid authentication credentials", status_code=401)
        
        return format_response(admin.to_dict())
    
    except Exception as e:
        return format_error(f"Error retrieving user profile: {str(e)}")

@auth_bp.route('/change-password', methods=['POST'])
@jwt_required()
def change_password():
    """Change password for current admin user"""
    try:
        admin_id = get_jwt_identity()
        # Convert admin_id back to integer if it's a string
        if isinstance(admin_id, str):
            admin_id = int(admin_id)
            
        admin = AdminModel.query.get(admin_id)
        
        if not admin:
            return format_error("Invalid authentication credentials", status_code=401)
        
        data = request.get_json()
        
        if not data or not data.get('current_password') or not data.get('new_password'):
            return format_error("Missing current password or new password", status_code=400)
        
        # Verify current password
        if not admin.check_password(data['current_password']):
            return format_error("Current password is incorrect", status_code=400)
        
        # Set new password
        admin.set_password(data['new_password'])
        admin.updated_at = datetime.now()
        db.session.commit()
        
        return format_response({"message": "Password changed successfully"})
    
    except Exception as e:
        return format_error(f"Error changing password: {str(e)}")