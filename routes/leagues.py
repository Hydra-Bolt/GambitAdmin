from flask import Blueprint, request, jsonify
import logging
from models import leagues_data
from datetime import datetime
from utils.response_formatter import format_response, format_error

# Configure logger
logger = logging.getLogger(__name__)

# Create Blueprint
leagues_bp = Blueprint('leagues', __name__)

@leagues_bp.route('/', methods=['GET'])
def get_leagues():
    """Get all leagues with optional filtering"""
    try:
        # Query parameters for filtering
        category = request.args.get('category')
        country = request.args.get('country')
        
        # Apply filters if provided
        filtered_data = leagues_data
        if category:
            filtered_data = [l for l in filtered_data if l['category'] == category]
        if country:
            filtered_data = [l for l in filtered_data if l['country'] == country]
            
        return format_response(filtered_data)
    except Exception as e:
        logger.error(f"Error getting leagues: {str(e)}")
        return format_error(str(e)), 500

@leagues_bp.route('/<int:league_id>', methods=['GET'])
def get_league(league_id):
    """Get a specific league by ID"""
    try:
        league = next((l for l in leagues_data if l['id'] == league_id), None)
        if league:
            return format_response(league)
        return format_error("League not found"), 404
    except Exception as e:
        logger.error(f"Error getting league {league_id}: {str(e)}")
        return format_error(str(e)), 500

@leagues_bp.route('/', methods=['POST'])
def create_league():
    """Create a new league"""
    try:
        data = request.json
        if not data:
            return format_error("Invalid request data"), 400
            
        # Validate required fields
        required_fields = ['name', 'category', 'country', 'logo_url']
        for field in required_fields:
            if field not in data:
                return format_error(f"Missing required field: {field}"), 400
                
        # Generate new ID
        new_id = max([l['id'] for l in leagues_data], default=0) + 1
        
        # Create new league
        from models import League
        
        new_league = League.create_record(
            id=new_id,
            name=data['name'],
            category=data['category'],
            country=data['country'],
            logo_url=data['logo_url'],
            popularity=data.get('popularity', 0)
        )
        
        leagues_data.append(new_league)
        return format_response(new_league, status_code=201)
    except Exception as e:
        logger.error(f"Error creating league: {str(e)}")
        return format_error(str(e)), 500

@leagues_bp.route('/<int:league_id>', methods=['PUT'])
def update_league(league_id):
    """Update an existing league"""
    try:
        data = request.json
        if not data:
            return format_error("Invalid request data"), 400
            
        # Find league
        league_index = next((i for i, l in enumerate(leagues_data) if l['id'] == league_id), None)
        if league_index is None:
            return format_error("League not found"), 404
            
        # Update fields
        current_league = leagues_data[league_index]
        for key, value in data.items():
            if key in current_league and key != 'id':
                current_league[key] = value
                
        # Update timestamp
        current_league['updated_at'] = datetime.now().isoformat()
        
        return format_response(current_league)
    except Exception as e:
        logger.error(f"Error updating league {league_id}: {str(e)}")
        return format_error(str(e)), 500

@leagues_bp.route('/<int:league_id>/toggle', methods=['PUT'])
def toggle_league_status(league_id):
    """Toggle league enabled/disabled status"""
    try:
        # Find league
        league_index = next((i for i, l in enumerate(leagues_data) if l['id'] == league_id), None)
        if league_index is None:
            return format_error("League not found"), 404
            
        # Toggle the enabled status
        current_league = leagues_data[league_index]
        current_league['enabled'] = not current_league.get('enabled', True)
                
        # Update timestamp
        current_league['updated_at'] = datetime.now().isoformat()
        
        return format_response(current_league)
    except Exception as e:
        logger.error(f"Error toggling league status {league_id}: {str(e)}")
        return format_error(str(e)), 500

@leagues_bp.route('/<int:league_id>', methods=['DELETE'])
def delete_league(league_id):
    """Delete a league"""
    try:
        # Find league
        league_index = next((i for i, l in enumerate(leagues_data) if l['id'] == league_id), None)
        if league_index is None:
            return format_error("League not found"), 404
            
        # Remove league
        deleted_league = leagues_data.pop(league_index)
        
        return format_response({"message": "League deleted successfully", "id": league_id})
    except Exception as e:
        logger.error(f"Error deleting league {league_id}: {str(e)}")
        return format_error(str(e)), 500

@leagues_bp.route('/popular', methods=['GET'])
def get_popular_leagues():
    """Get most popular leagues"""
    try:
        # Sort leagues by popularity
        sorted_leagues = sorted(leagues_data, key=lambda x: x['popularity'], reverse=True)
        
        # Limit to top N
        limit = request.args.get('limit', default=5, type=int)
        top_leagues = sorted_leagues[:limit]
        
        return format_response(top_leagues)
    except Exception as e:
        logger.error(f"Error getting popular leagues: {str(e)}")
        return format_error(str(e)), 500
