"""
User Activity routes for the Gambit API.
Tracks and provides endpoints for user activity statistics and analytics.
"""

import logging
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from datetime import datetime, timedelta
from models import UserActivityModel, db
from utils.response_formatter import format_response, format_error
from utils.auth import require_permission
from models import PermissionType

# Configure logging
logger = logging.getLogger(__name__)

user_activity_bp = Blueprint('user_activity', __name__)

@user_activity_bp.route('/', methods=['GET'])
@jwt_required()
@require_permission(PermissionType.USERS)
def get_user_activity():
    """Get user activity statistics for a specified time period"""
    try:
        # Get query parameters
        days = request.args.get('days', 30, type=int)
        
        # Calculate start date
        start_date = datetime.now() - timedelta(days=days)
        
        # Query the database
        activities = UserActivityModel.query.filter(
            UserActivityModel.date >= start_date
        ).order_by(UserActivityModel.date).all()
        
        # Format the response
        result = {
            "activities": [activity.to_dict() for activity in activities],
            "total_active_users": sum(activity.active_users for activity in activities),
            "total_new_users": sum(activity.new_users for activity in activities),
        }
        
        return format_response(result)
        
    except Exception as e:
        logger.error(f"Error getting user activity: {str(e)}")
        return format_error(f"Error getting user activity: {str(e)}", status_code=500)

@user_activity_bp.route('/', methods=['POST'])
@jwt_required()
@require_permission(PermissionType.USERS)
def add_user_activity():
    """Add a new user activity record (used for manual updates or corrections)"""
    try:
        data = request.get_json()
        
        if not data:
            return format_error("No data provided", status_code=400)
            
        # Validate required fields
        required_fields = ['date', 'active_users', 'new_users']
        for field in required_fields:
            if field not in data:
                return format_error(f"Missing required field: {field}", status_code=400)
        
        # Parse the date
        try:
            activity_date = datetime.fromisoformat(data['date'].replace('Z', '+00:00'))
        except (ValueError, TypeError):
            return format_error("Invalid date format. Use ISO format (YYYY-MM-DDTHH:MM:SS.sssZ)", status_code=400)
        
        # Check if entry for this date already exists
        existing = UserActivityModel.query.filter_by(date=activity_date.date()).first()
        if existing:
            # Update existing record
            existing.active_users = data['active_users']
            existing.new_users = data['new_users']
            db.session.commit()
            return format_response({
                "message": "User activity updated successfully",
                "activity": existing.to_dict()
            })
        
        # Create new record
        new_activity = UserActivityModel(
            date=activity_date,
            active_users=data['active_users'],
            new_users=data['new_users']
        )
        
        db.session.add(new_activity)
        db.session.commit()
        
        return format_response({
            "message": "User activity added successfully",
            "activity": new_activity.to_dict()
        })
        
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error adding user activity: {str(e)}")
        return format_error(f"Error adding user activity: {str(e)}", status_code=500)

@user_activity_bp.route('/summary', methods=['GET'])
@jwt_required()
@require_permission(PermissionType.USERS)
def get_user_activity_summary():
    """Get summary statistics on user activity"""
    try:
        # Get total counts
        total_active = db.session.query(db.func.sum(UserActivityModel.active_users)).scalar() or 0
        total_new = db.session.query(db.func.sum(UserActivityModel.new_users)).scalar() or 0
        
        # Get recent activity (last 7 days)
        recent_date = datetime.now() - timedelta(days=7)
        recent_active = db.session.query(
            db.func.sum(UserActivityModel.active_users)
        ).filter(UserActivityModel.date >= recent_date).scalar() or 0
        
        recent_new = db.session.query(
            db.func.sum(UserActivityModel.new_users)
        ).filter(UserActivityModel.date >= recent_date).scalar() or 0
        
        # Return summary
        return format_response({
            "total_active_users": total_active,
            "total_new_users": total_new,
            "recent_active_users": recent_active,
            "recent_new_users": recent_new,
            "recent_period_days": 7
        })
        
    except Exception as e:
        logger.error(f"Error getting user activity summary: {str(e)}")
        return format_error(f"Error getting user activity summary: {str(e)}", status_code=500)