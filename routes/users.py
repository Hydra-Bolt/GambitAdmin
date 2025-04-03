from flask import Blueprint, request, jsonify
import logging
from datetime import datetime
from app import db
from sqlalchemy import desc
from models import UserModel, UserActivityModel
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
        
        # Base query
        query = UserModel.query
        
        # Apply filters if provided
        if status:
            query = query.filter(UserModel.status == status)
            
        # Execute query and convert to list of dictionaries
        users = [user.to_dict() for user in query.all()]
            
        return format_response(users)
    except Exception as e:
        logger.error(f"Error getting users: {str(e)}")
        return format_error(str(e), status_code=500)

@users_bp.route('/<int:user_id>', methods=['GET'])
def get_user(user_id):
    """Get a specific user by ID"""
    try:
        user = UserModel.query.get(user_id)
        if user:
            return format_response(user.to_dict())
        return format_error("User not found", status_code=404)
    except Exception as e:
        logger.error(f"Error getting user {user_id}: {str(e)}")
        return format_error(str(e), status_code=500)
        
@users_bp.route('/uuid/<string:user_uuid>', methods=['GET'])
def get_user_by_uuid(user_uuid):
    """Get a specific user by UUID"""
    try:
        user = UserModel.query.filter_by(uuid=user_uuid).first()
        if user:
            return format_response(user.to_dict())
        return format_error("User not found", status_code=404)
    except Exception as e:
        logger.error(f"Error getting user by UUID {user_uuid}: {str(e)}")
        return format_error(str(e), status_code=500)

@users_bp.route('/', methods=['POST'])
def create_user():
    """Create a new user"""
    try:
        data = request.json
        if not data:
            return format_error("Invalid request data", status_code=400)
            
        # Validate required fields
        required_fields = ['email', 'username', 'status', 'full_name']
        for field in required_fields:
            if field not in data:
                return format_error(f"Missing required field: {field}", status_code=400)
        
        # Create a UUID if one wasn't provided
        if 'uuid' not in data or not data['uuid']:
            import uuid
            data['uuid'] = f"user-{str(uuid.uuid4())}"
        
        # Create new user object
        new_user = UserModel(
            email=data['email'],
            username=data['username'],
            uuid=data['uuid'],
            full_name=data['full_name'],
            profile_image=data.get('profile_image', f"https://ui-avatars.com/api/?name={data['username']}&background=random"),
            registration_date=datetime.now(),
            last_login=datetime.now(),
            status=data['status']
        )
        
        # Add to database
        db.session.add(new_user)
        db.session.commit()
        
        return format_response(new_user.to_dict(), status_code=201)
    except Exception as e:
        logger.error(f"Error creating user: {str(e)}")
        db.session.rollback()
        return format_error(str(e), status_code=500)

@users_bp.route('/<int:user_id>', methods=['PUT'])
def update_user(user_id):
    """Update an existing user"""
    try:
        data = request.json
        if not data:
            return format_error("Invalid request data", status_code=400)
            
        # Find user
        user = UserModel.query.get(user_id)
        if not user:
            return format_error("User not found", status_code=404)
            
        # Update fields
        for key, value in data.items():
            if hasattr(user, key) and key not in ['id', 'created_at', 'updated_at']:
                setattr(user, key, value)
                
        # Save to database
        db.session.commit()
        
        return format_response(user.to_dict())
    except Exception as e:
        logger.error(f"Error updating user {user_id}: {str(e)}")
        db.session.rollback()
        return format_error(str(e), status_code=500)

@users_bp.route('/<int:user_id>', methods=['DELETE'])
def delete_user(user_id):
    """Delete a user"""
    try:
        # Find user
        user = UserModel.query.get(user_id)
        if not user:
            return format_error("User not found", status_code=404)
        
        # Save user data before deletion for response
        user_dict = user.to_dict()
            
        # Remove from database
        db.session.delete(user)
        db.session.commit()
        
        return format_response({"message": "User deleted successfully", "user": user_dict})
    except Exception as e:
        logger.error(f"Error deleting user {user_id}: {str(e)}")
        db.session.rollback()
        return format_error(str(e), status_code=500)

@users_bp.route('/stats', methods=['GET'])
def get_user_stats():
    """Get user statistics"""
    try:
        # Calculate user statistics
        total_users = UserModel.query.count()
        active_users = UserModel.query.filter_by(status='active').count()
        inactive_users = UserModel.query.filter_by(status='inactive').count()
        suspended_users = UserModel.query.filter_by(status='suspended').count()
        
        # Calculate recent registrations - users registered in the last 30 days
        import datetime as dt
        thirty_days_ago = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0) - dt.timedelta(days=30)
        recent_users = UserModel.query.filter(UserModel.registration_date >= thirty_days_ago).count()
        
        # Format response
        stats = {
            "total_users": total_users,
            "active_users": active_users,
            "inactive_users": inactive_users,
            "suspended_users": suspended_users,
            "recent_registrations": recent_users
        }
        return format_response(stats)
    except Exception as e:
        logger.error(f"Error getting user stats: {str(e)}")
        return format_error(str(e), status_code=500)

@users_bp.route('/activity', methods=['GET'])
def get_user_activity():
    """Get user activity data for charting"""
    try:
        # Parse date range parameters
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')
        
        # Base query
        query = UserActivityModel.query
        
        # Apply date filters if provided
        if start_date:
            start = datetime.fromisoformat(start_date)
            query = query.filter(UserActivityModel.date >= start)
            
        if end_date:
            end = datetime.fromisoformat(end_date)
            query = query.filter(UserActivityModel.date <= end)
        
        # Order by date
        query = query.order_by(UserActivityModel.date)
        
        # Execute query and convert to list of dictionaries
        activity_data = [activity.to_dict() for activity in query.all()]
        
        return format_response(activity_data)
    except Exception as e:
        logger.error(f"Error getting user activity: {str(e)}")
        return format_error(str(e), status_code=500)
