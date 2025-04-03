from flask import Blueprint, request, jsonify
import logging
from models import users_data, user_activity_data
from datetime import datetime
from utils.response_formatter import format_response, format_error

# Configure logger
logger = logging.getLogger(__name__)

# Create Blueprint
users_bp = Blueprint('users', __name__)

@users_bp.route('/', methods=['GET'])
def get_users():
    """Get all users with optional filtering"""
    try:
        # Query parameters for filtering
        status = request.args.get('status')
        
        # Apply filters if provided
        filtered_data = users_data
        if status:
            filtered_data = [u for u in filtered_data if u['status'] == status]
            
        return format_response(filtered_data)
    except Exception as e:
        logger.error(f"Error getting users: {str(e)}")
        return format_error(str(e)), 500

@users_bp.route('/<int:user_id>', methods=['GET'])
def get_user(user_id):
    """Get a specific user by ID"""
    try:
        user = next((u for u in users_data if u['id'] == user_id), None)
        if user:
            return format_response(user)
        return format_error("User not found"), 404
    except Exception as e:
        logger.error(f"Error getting user {user_id}: {str(e)}")
        return format_error(str(e)), 500

@users_bp.route('/', methods=['POST'])
def create_user():
    """Create a new user"""
    try:
        data = request.json
        if not data:
            return format_error("Invalid request data"), 400
            
        # Validate required fields
        required_fields = ['email', 'username', 'status']
        for field in required_fields:
            if field not in data:
                return format_error(f"Missing required field: {field}"), 400
                
        # Generate new ID
        new_id = max([u['id'] for u in users_data], default=0) + 1
        
        # Create new user
        from models import User
        
        new_user = User.create_record(
            id=new_id,
            email=data['email'],
            username=data['username'],
            registration_date=datetime.now(),
            last_login=datetime.now(),
            status=data['status']
        )
        
        users_data.append(new_user)
        return format_response(new_user, status_code=201)
    except Exception as e:
        logger.error(f"Error creating user: {str(e)}")
        return format_error(str(e)), 500

@users_bp.route('/<int:user_id>', methods=['PUT'])
def update_user(user_id):
    """Update an existing user"""
    try:
        data = request.json
        if not data:
            return format_error("Invalid request data"), 400
            
        # Find user
        user_index = next((i for i, u in enumerate(users_data) if u['id'] == user_id), None)
        if user_index is None:
            return format_error("User not found"), 404
            
        # Update fields
        current_user = users_data[user_index]
        for key, value in data.items():
            if key in current_user and key != 'id':
                current_user[key] = value
                
        # Update timestamp
        current_user['updated_at'] = datetime.now().isoformat()
        
        return format_response(current_user)
    except Exception as e:
        logger.error(f"Error updating user {user_id}: {str(e)}")
        return format_error(str(e)), 500

@users_bp.route('/<int:user_id>', methods=['DELETE'])
def delete_user(user_id):
    """Delete a user"""
    try:
        # Find user
        user_index = next((i for i, u in enumerate(users_data) if u['id'] == user_id), None)
        if user_index is None:
            return format_error("User not found"), 404
            
        # Remove user
        deleted_user = users_data.pop(user_index)
        
        return format_response({"message": "User deleted successfully", "id": user_id})
    except Exception as e:
        logger.error(f"Error deleting user {user_id}: {str(e)}")
        return format_error(str(e)), 500

@users_bp.route('/stats', methods=['GET'])
def get_user_stats():
    """Get user statistics"""
    try:
        # Get stats from user activity data
        return format_response(user_activity_data)
    except Exception as e:
        logger.error(f"Error getting user stats: {str(e)}")
        return format_error(str(e)), 500

@users_bp.route('/activity', methods=['GET'])
def get_user_activity():
    """Get user activity data for charting"""
    try:
        # Parse date range parameters
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')
        
        filtered_data = user_activity_data
        
        if start_date:
            start = datetime.fromisoformat(start_date)
            filtered_data = [a for a in filtered_data if datetime.fromisoformat(a['date']) >= start]
            
        if end_date:
            end = datetime.fromisoformat(end_date)
            filtered_data = [a for a in filtered_data if datetime.fromisoformat(a['date']) <= end]
        
        return format_response(filtered_data)
    except Exception as e:
        logger.error(f"Error getting user activity: {str(e)}")
        return format_error(str(e)), 500
