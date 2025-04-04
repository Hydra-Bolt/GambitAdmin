from datetime import datetime
from flask import Blueprint, request, jsonify
import logging
from models import subscribers_data, PermissionType
from utils.response_formatter import format_response, format_error
from utils.auth import require_permission
from flask_jwt_extended import jwt_required
from math import ceil

# Configure logger
logger = logging.getLogger(__name__)

# Create Blueprint
subscribers_bp = Blueprint('subscribers', __name__)

@subscribers_bp.route('/', methods=['GET'])
@jwt_required()
@require_permission(PermissionType.SUBSCRIBERS)
def get_subscribers():
    """Get all subscribers with optional filtering and pagination"""
    try:
        # Query parameters for filtering
        subscription_type = request.args.get('subscription_type')
        status = request.args.get('status')
        
        # Pagination parameters
        page = int(request.args.get('page', 1))
        per_page = int(request.args.get('per_page', 10))
        
        # Apply filters if provided
        filtered_data = subscribers_data
        if subscription_type:
            filtered_data = [s for s in filtered_data if s['subscription_type'] == subscription_type]
        if status:
            filtered_data = [s for s in filtered_data if s['status'] == status]
            
        # Calculate total pages
        total_items = len(filtered_data)
        total_pages = ceil(total_items / per_page)
        
        # Apply pagination
        start_idx = (page - 1) * per_page
        end_idx = start_idx + per_page
        paginated_data = filtered_data[start_idx:end_idx]
        
        # Prepare response with pagination info
        response_data = {
            'items': paginated_data,
            'pagination': {
                'total_items': total_items,
                'total_pages': total_pages,
                'current_page': page,
                'per_page': per_page,
                'has_next': page < total_pages,
                'has_prev': page > 1
            }
        }
            
        return format_response(response_data)
    except Exception as e:
        logger.error(f"Error getting subscribers: {str(e)}")
        return format_error(str(e)), 500

@subscribers_bp.route('/<int:subscriber_id>', methods=['GET'])
@jwt_required()
@require_permission(PermissionType.SUBSCRIBERS)
def get_subscriber(subscriber_id):
    """Get a specific subscriber by ID"""
    try:
        subscriber = next((s for s in subscribers_data if s['id'] == subscriber_id), None)
        if subscriber:
            return format_response(subscriber)
        return format_error("Subscriber not found"), 404
    except Exception as e:
        logger.error(f"Error getting subscriber {subscriber_id}: {str(e)}")
        return format_error(str(e)), 500

@subscribers_bp.route('/', methods=['POST'])
@jwt_required()
@require_permission(PermissionType.SUBSCRIBERS)
def create_subscriber():
    """Create a new subscriber"""
    try:
        data = request.json
        if not data:
            return format_error("Invalid request data"), 400
            
        # Validate required fields
        required_fields = ['email', 'name', 'subscription_type', 'start_date', 'end_date', 'status']
        for field in required_fields:
            if field not in data:
                return format_error(f"Missing required field: {field}"), 400
                
        # Generate new ID
        new_id = max([s['id'] for s in subscribers_data], default=0) + 1
        
        # Create new subscriber
        from models import Subscriber
        from datetime import datetime
        
        new_subscriber = Subscriber.create_record(
            id=new_id,
            email=data['email'],
            name=data['name'],
            subscription_type=data['subscription_type'],
            start_date=datetime.fromisoformat(data['start_date']),
            end_date=datetime.fromisoformat(data['end_date']),
            status=data['status']
        )
        
        subscribers_data.append(new_subscriber)
        return format_response(new_subscriber, status_code=201)
    except Exception as e:
        logger.error(f"Error creating subscriber: {str(e)}")
        return format_error(str(e)), 500

@subscribers_bp.route('/<int:subscriber_id>', methods=['PUT'])
@jwt_required()
@require_permission(PermissionType.SUBSCRIBERS)
def update_subscriber(subscriber_id):
    """Update an existing subscriber"""
    try:
        data = request.json
        if not data:
            return format_error("Invalid request data"), 400
            
        # Find subscriber
        subscriber_index = next((i for i, s in enumerate(subscribers_data) if s['id'] == subscriber_id), None)
        if subscriber_index is None:
            return format_error("Subscriber not found"), 404
            
        # Update fields
        current_subscriber = subscribers_data[subscriber_index]
        for key, value in data.items():
            if key in current_subscriber and key != 'id':
                current_subscriber[key] = value
                
        # Update timestamp
        current_subscriber['updated_at'] = datetime.now().isoformat()
        
        return format_response(current_subscriber)
    except Exception as e:
        logger.error(f"Error updating subscriber {subscriber_id}: {str(e)}")
        return format_error(str(e)), 500

@subscribers_bp.route('/<int:subscriber_id>', methods=['DELETE'])
@jwt_required()
@require_permission(PermissionType.SUBSCRIBERS)
def delete_subscriber(subscriber_id):
    """Delete a subscriber"""
    try:
        # Find subscriber
        subscriber_index = next((i for i, s in enumerate(subscribers_data) if s['id'] == subscriber_id), None)
        if subscriber_index is None:
            return format_error("Subscriber not found"), 404
            
        # Remove subscriber
        deleted_subscriber = subscribers_data.pop(subscriber_index)
        
        return format_response({"message": "Subscriber deleted successfully", "id": subscriber_id})
    except Exception as e:
        logger.error(f"Error deleting subscriber {subscriber_id}: {str(e)}")
        return format_error(str(e)), 500

@subscribers_bp.route('/stats', methods=['GET'])
@jwt_required()
@require_permission(PermissionType.SUBSCRIBERS)
def get_subscriber_stats():
    """Get subscriber statistics"""
    try:
        # Count subscribers by type
        total_subscribers = len(subscribers_data)
        monthly_subscribers = len([s for s in subscribers_data if s['subscription_type'] == 'monthly' and s['status'] == 'active'])
        yearly_subscribers = len([s for s in subscribers_data if s['subscription_type'] == 'yearly' and s['status'] == 'active'])
        
        stats = {
            'total': total_subscribers,
            'monthly': monthly_subscribers,
            'yearly': yearly_subscribers,
            'growth_rate': 0.8  # This would be calculated from historical data
        }
        
        return format_response(stats)
    except Exception as e:
        logger.error(f"Error getting subscriber stats: {str(e)}")
        return format_error(str(e)), 500
