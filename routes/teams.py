from flask import Blueprint, request, jsonify
import logging
from models import teams_data
from datetime import datetime
from utils.response_formatter import format_response, format_error

# Configure logger
logger = logging.getLogger(__name__)

# Create Blueprint
teams_bp = Blueprint('teams', __name__)

@teams_bp.route('/', methods=['GET'])
def get_teams():
    """Get all teams with optional filtering"""
    try:
        # Query parameters for filtering
        league_id = request.args.get('league_id', type=int)
        
        # Apply filters if provided
        filtered_data = teams_data
        if league_id:
            filtered_data = [t for t in filtered_data if t['league_id'] == league_id]
            
        return format_response(filtered_data)
    except Exception as e:
        logger.error(f"Error getting teams: {str(e)}")
        return format_error(str(e)), 500

@teams_bp.route('/<int:team_id>', methods=['GET'])
def get_team(team_id):
    """Get a specific team by ID"""
    try:
        team = next((t for t in teams_data if t['id'] == team_id), None)
        if team:
            return format_response(team)
        return format_error("Team not found"), 404
    except Exception as e:
        logger.error(f"Error getting team {team_id}: {str(e)}")
        return format_error(str(e)), 500

@teams_bp.route('/', methods=['POST'])
def create_team():
    """Create a new team"""
    try:
        data = request.json
        if not data:
            return format_error("Invalid request data"), 400
            
        # Validate required fields
        required_fields = ['name', 'league_id', 'logo_url']
        for field in required_fields:
            if field not in data:
                return format_error(f"Missing required field: {field}"), 400
                
        # Generate new ID
        new_id = max([t['id'] for t in teams_data], default=0) + 1
        
        # Create new team
        from models import Team
        
        new_team = Team.create_record(
            id=new_id,
            name=data['name'],
            league_id=data['league_id'],
            logo_url=data['logo_url'],
            popularity=data.get('popularity', 0)
        )
        
        teams_data.append(new_team)
        return format_response(new_team, status_code=201)
    except Exception as e:
        logger.error(f"Error creating team: {str(e)}")
        return format_error(str(e)), 500

@teams_bp.route('/<int:team_id>', methods=['PUT'])
def update_team(team_id):
    """Update an existing team"""
    try:
        data = request.json
        if not data:
            return format_error("Invalid request data"), 400
            
        # Find team
        team_index = next((i for i, t in enumerate(teams_data) if t['id'] == team_id), None)
        if team_index is None:
            return format_error("Team not found"), 404
            
        # Update fields
        current_team = teams_data[team_index]
        for key, value in data.items():
            if key in current_team and key != 'id':
                current_team[key] = value
                
        # Update timestamp
        current_team['updated_at'] = datetime.now().isoformat()
        
        return format_response(current_team)
    except Exception as e:
        logger.error(f"Error updating team {team_id}: {str(e)}")
        return format_error(str(e)), 500

@teams_bp.route('/<int:team_id>', methods=['DELETE'])
def delete_team(team_id):
    """Delete a team"""
    try:
        # Find team
        team_index = next((i for i, t in enumerate(teams_data) if t['id'] == team_id), None)
        if team_index is None:
            return format_error("Team not found"), 404
            
        # Remove team
        deleted_team = teams_data.pop(team_index)
        
        return format_response({"message": "Team deleted successfully", "id": team_id})
    except Exception as e:
        logger.error(f"Error deleting team {team_id}: {str(e)}")
        return format_error(str(e)), 500

@teams_bp.route('/popular', methods=['GET'])
def get_popular_teams():
    """Get most popular teams"""
    try:
        # Sort teams by popularity
        sorted_teams = sorted(teams_data, key=lambda x: x['popularity'], reverse=True)
        
        # Limit to top N
        limit = request.args.get('limit', default=5, type=int)
        top_teams = sorted_teams[:limit]
        
        return format_response(top_teams)
    except Exception as e:
        logger.error(f"Error getting popular teams: {str(e)}")
        return format_error(str(e)), 500
