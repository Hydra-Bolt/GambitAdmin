"""
User Authentication routes for the Gambit API.
Handles signup, login, profile management, and token generation for regular users.
Separate from admin authentication routes.
"""

import logging
import traceback
import uuid
from flask import Blueprint, request, jsonify, g, current_app
from flask_jwt_extended import get_jwt_identity, jwt_required, create_access_token, create_refresh_token
from datetime import datetime, timedelta
from models import UserModel, db
from utils.response_formatter import format_response, format_error
from sqlalchemy.exc import IntegrityError

# Configure logging
logger = logging.getLogger(__name__)

user_auth_bp = Blueprint('user_auth', __name__)

@user_auth_bp.route('/test', methods=['GET'])
def test():
    """Test route to verify API is running"""
    return format_response({"message": "User Auth API is working"})

@user_auth_bp.route('/signup', methods=['POST'])
def signup():
    """Register a new user account"""
    try:
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['email', 'username', 'password', 'full_name']
        for field in required_fields:
            if not data or not data.get(field):
                return format_error(f"Missing required field: {field}", status_code=400)
        
        # Check if email or username already exists
        email_exists = UserModel.query.filter_by(email=data['email']).first()
        if email_exists:
            return format_error("Email already registered", status_code=409)
        
        username_exists = UserModel.query.filter_by(username=data['username']).first()
        if username_exists:
            return format_error("Username already taken", status_code=409)
        
        # Create new user
        new_user = UserModel(
            uuid=str(uuid.uuid4()),
            email=data['email'],
            username=data['username'],
            full_name=data['full_name'],
            registration_date=datetime.now(),
            last_login=datetime.now(),
            status='active',
            profile_image=data.get('profile_image', f"https://ui-avatars.com/api/?name={data['username']}&background=random"),
            bio=data.get('bio', ''),
            role=data.get('role', 'user')  # Default role is 'user'
        )
        
        # Set password (this will hash it)
        new_user.set_password(data['password'])
        
        # Save to database
        db.session.add(new_user)
        db.session.commit()
        
        # Generate JWT tokens
        access_token = create_access_token(identity=str(new_user.id))
        refresh_token = create_refresh_token(identity=str(new_user.id))
        
        return format_response({
            'message': 'User registered successfully',
            'user': new_user.to_dict(),
            'access_token': access_token,
            'refresh_token': refresh_token
        })
        
    except IntegrityError as e:
        db.session.rollback()
        logger.error(f"Database integrity error: {str(e)}")
        return format_error("Database integrity error. User may already exist.", status_code=409)
    
    except Exception as e:
        db.session.rollback()
        logger.error(f"Signup error: {str(e)}")
        logger.error(traceback.format_exc())
        return format_error(f"Signup error: {str(e)}", status_code=500)

@user_auth_bp.route('/login', methods=['POST'])
def login():
    """Login route for users"""
    try:
        data = request.get_json()
        
        if not data or not data.get('username') or not data.get('password'):
            return format_error("Missing username/email or password", status_code=400)
        
        # Find user by username or email
        user = UserModel.query.filter(
            (UserModel.username == data['username']) | 
            (UserModel.email == data['username'])
        ).first()
        
        # Check if user exists and password is correct
        if not user or not user.check_password(data['password']):
            return format_error("Invalid username/email or password", status_code=401)
        
        # Check if account is active
        if user.status != 'active':
            return format_error("Your account has been deactivated or suspended", status_code=403)
        
        # Update last login time
        user.last_login = datetime.now()
        db.session.commit()
        
        # Generate tokens
        access_token = create_access_token(identity=str(user.id))
        refresh_token = create_refresh_token(identity=str(user.id))
        
        # Create the response with the token and user data
        response = format_response({
            'access_token': access_token,
            'refresh_token': refresh_token,
            'user': user.to_dict()
        })
        
        return response
    
    except Exception as e:
        logger.error(f"Login error: {str(e)}")
        logger.error(traceback.format_exc())
        return format_error(f"Login error: {str(e)}", status_code=500)

@user_auth_bp.route('/refresh', methods=['POST'])
@jwt_required(refresh=True)
def refresh_token():
    """Refresh access token using refresh token"""
    try:
        # Get the user identity from the refresh token
        user_id = get_jwt_identity()
        
        # Create a new access token
        access_token = create_access_token(identity=user_id)
        
        return format_response({
            'access_token': access_token
        })
    
    except Exception as e:
        logger.error(f"Token refresh error: {str(e)}")
        return format_error(f"Token refresh error: {str(e)}", status_code=500)

@user_auth_bp.route('/me', methods=['GET'])
@jwt_required()
def get_user_profile():
    """Get current authenticated user profile"""
    try:
        user_id = get_jwt_identity()
        
        # Convert user_id back to integer if it's a string
        if isinstance(user_id, str):
            user_id = int(user_id)
        
        user = UserModel.query.get(user_id)
        
        if not user:
            return format_error("Invalid authentication credentials", status_code=401)
        
        return format_response(user.to_dict())
    
    except Exception as e:
        return format_error(f"Error retrieving user profile: {str(e)}", status_code=500)

@user_auth_bp.route('/me', methods=['PUT'])
@jwt_required()
def update_user_profile():
    """Update current authenticated user profile"""
    try:
        user_id = get_jwt_identity()
        
        # Convert user_id back to integer if it's a string
        if isinstance(user_id, str):
            user_id = int(user_id)
        
        user = UserModel.query.get(user_id)
        
        if not user:
            return format_error("Invalid authentication credentials", status_code=401)
        
        data = request.get_json()
        
        # Update user fields (except sensitive ones like id, email, username which should have separate endpoints)
        allowed_fields = ['full_name', 'bio', 'profile_image']
        for field in allowed_fields:
            if field in data:
                setattr(user, field, data[field])
        
        user.updated_at = datetime.now()
        db.session.commit()
        
        return format_response({
            'message': 'Profile updated successfully',
            'user': user.to_dict()
        })
    
    except Exception as e:
        db.session.rollback()
        return format_error(f"Error updating profile: {str(e)}", status_code=500)

@user_auth_bp.route('/change-password', methods=['POST'])
@jwt_required()
def change_password():
    """Change password for current user"""
    try:
        user_id = get_jwt_identity()
        
        # Convert user_id back to integer if it's a string
        if isinstance(user_id, str):
            user_id = int(user_id)
            
        user = UserModel.query.get(user_id)
        
        if not user:
            return format_error("Invalid authentication credentials", status_code=401)
        
        data = request.get_json()
        
        if not data or not data.get('current_password') or not data.get('new_password'):
            return format_error("Missing current password or new password", status_code=400)
        
        # Verify current password
        if not user.check_password(data['current_password']):
            return format_error("Current password is incorrect", status_code=400)
        
        # Set new password
        user.set_password(data['new_password'])
        user.updated_at = datetime.now()
        db.session.commit()
        
        return format_response({"message": "Password changed successfully"})
    
    except Exception as e:
        db.session.rollback()
        return format_error(f"Error changing password: {str(e)}", status_code=500)