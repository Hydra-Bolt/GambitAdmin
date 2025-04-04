from flask import Blueprint, request, jsonify
from models import NotificationModel, notifications_data, PermissionType
from utils.response_formatter import format_response, format_error
from datetime import datetime
import uuid
from app import db
from sqlalchemy import or_
from flask_jwt_extended import jwt_required
from utils.auth import require_permission

notifications_bp = Blueprint('notifications', __name__)

@notifications_bp.route('/', methods=['GET'])
@jwt_required()
@require_permission(PermissionType.NOTIFICATION)
def get_notifications():
    """Get all notifications with optional filtering"""
    target_type = request.args.get('target_type')
    target_user_id = request.args.get('target_user_id')
    sent_status = request.args.get('sent')
    
    query = NotificationModel.query
    
    if target_type:
        query = query.filter(NotificationModel.target_type == target_type)
    
    if target_user_id:
        try:
            user_id = int(target_user_id)
            query = query.filter(NotificationModel.target_user_id == user_id)
        except ValueError:
            return format_error("Invalid user_id format. Must be an integer.")
    
    if sent_status:
        sent = sent_status.lower() == 'true'
        query = query.filter(NotificationModel.sent == sent)
    
    notifications = query.all()
    
    # Convert to dictionary representation
    notification_list = [notification.to_dict() for notification in notifications]
    
    return format_response(notification_list)


@notifications_bp.route('/<int:notification_id>', methods=['GET'])
@jwt_required()
@require_permission(PermissionType.NOTIFICATION)
def get_notification(notification_id):
    """Get a specific notification by ID"""
    notification = NotificationModel.query.get(notification_id)
    
    if not notification:
        return format_error(f"Notification with ID {notification_id} not found", status_code=404)
    
    return format_response(notification.to_dict())


@notifications_bp.route('/', methods=['POST'])
@jwt_required()
@require_permission(PermissionType.NOTIFICATION)
def create_notification():
    """Create a new notification"""
    data = request.json
    
    if not data:
        return format_error("No data provided", status_code=400)
    
    # Validate required fields
    required_fields = ['title', 'message', 'destination_url']
    for field in required_fields:
        if field not in data:
            return format_error(f"Missing required field: {field}", status_code=400)
    
    # Determine target type and user ID
    target_type = data.get('target_type', 'all')
    target_user_id = data.get('target_user_id')
    
    # Validate target_user_id if target_type is 'user'
    if target_type == 'user' and target_user_id is None:
        return format_error("target_user_id is required when target_type is 'user'", status_code=400)
    
    # Create new notification record
    new_notification = NotificationModel(
        title=data['title'],
        message=data['message'],
        destination_url=data['destination_url'],
        image_url=data.get('image_url', ''),
        icon_url=data.get('icon_url', ''),
        target_type=target_type,
        target_user_id=target_user_id,
        sent=data.get('sent', False)
    )
    
    db.session.add(new_notification)
    db.session.commit()
    
    return format_response(new_notification.to_dict(), status_code=201)


@notifications_bp.route('/<int:notification_id>', methods=['PUT'])
@jwt_required()
@require_permission(PermissionType.NOTIFICATION)
def update_notification(notification_id):
    """Update an existing notification"""
    notification = NotificationModel.query.get(notification_id)
    
    if not notification:
        return format_error(f"Notification with ID {notification_id} not found", status_code=404)
    
    data = request.json
    
    if not data:
        return format_error("No data provided", status_code=400)
    
    # Update fields
    for field in ['title', 'message', 'destination_url', 'image_url', 'icon_url']:
        if field in data:
            setattr(notification, field, data[field])
    
    # Handle target_type and target_user_id separately
    if 'target_type' in data:
        notification.target_type = data['target_type']
        
        if data['target_type'] == 'user':
            if 'target_user_id' not in data:
                return format_error("target_user_id is required when target_type is 'user'", status_code=400)
            notification.target_user_id = data['target_user_id']
        elif data['target_type'] == 'all':
            notification.target_user_id = None
    
    # Handle sent status separately
    if 'sent' in data:
        notification.sent = data['sent']
    
    # Save changes
    db.session.commit()
    
    return format_response(notification.to_dict())


@notifications_bp.route('/<int:notification_id>', methods=['DELETE'])
@jwt_required()
@require_permission(PermissionType.NOTIFICATION)
def delete_notification(notification_id):
    """Delete a notification"""
    notification = NotificationModel.query.get(notification_id)
    
    if not notification:
        return format_error(f"Notification with ID {notification_id} not found", status_code=404)
    
    # Save notification data before deletion for response
    notification_dict = notification.to_dict()
    
    # Delete the notification
    db.session.delete(notification)
    db.session.commit()
    
    return format_response({
        "message": f"Notification with ID {notification_id} deleted successfully", 
        "deleted": notification_dict
    })


@notifications_bp.route('/<int:notification_id>/send', methods=['POST'])
@jwt_required()
@require_permission(PermissionType.NOTIFICATION)
def send_notification(notification_id):
    """Send a notification (mark it as sent)"""
    notification = NotificationModel.query.get(notification_id)
    
    if not notification:
        return format_error(f"Notification with ID {notification_id} not found", status_code=404)
    
    if notification.sent:
        return format_error(f"Notification with ID {notification_id} has already been sent", status_code=400)
    
    # In a real application, you would integrate with a notification service here
    notification.sent = True
    db.session.commit()
    
    return format_response({
        "message": f"Notification with ID {notification_id} sent successfully", 
        "notification": notification.to_dict()
    })