from flask import Blueprint, request, jsonify
from models import players_data, reels_data
from utils.response_formatter import format_response, format_error
from flask_jwt_extended import jwt_required
from utils.auth import require_permission
from models import PermissionType

players_bp = Blueprint('players', __name__)

@players_bp.route('/', methods=['GET'])
@jwt_required()
def get_players():
    """Get all players with optional filtering"""
    try:
        # Get query parameters for filtering
        league_id = request.args.get('league_id')
        team_id = request.args.get('team_id')
        status = request.args.get('status')
        
        # Apply filters if provided
        filtered_players = players_data
        
        if league_id:
            filtered_players = [p for p in filtered_players if p['league_id'] == int(league_id)]
        
        if team_id:
            filtered_players = [p for p in filtered_players if p['team_id'] == int(team_id)]
            
        if status:
            filtered_players = [p for p in filtered_players if p['status'].lower() == status.lower()]
        
        return format_response(filtered_players)
    
    except Exception as e:
        return format_error(f"Error retrieving players: {str(e)}")

@players_bp.route('/<int:player_id>', methods=['GET'])
@jwt_required()
def get_player(player_id):
    """Get a specific player by ID"""
    try:
        player = next((p for p in players_data if p['id'] == player_id), None)
        
        if not player:
            return format_error(f"Player with ID {player_id} not found", status_code=404)
        
        # Get all reels associated with this player
        player_reels = [r for r in reels_data if r['player_id'] == player_id]
        
        # Add reels to the player data
        player_data = {**player, 'reels': player_reels}
        
        return format_response(player_data)
    
    except Exception as e:
        return format_error(f"Error retrieving player: {str(e)}")

@players_bp.route('/popular', methods=['GET'])
@jwt_required()
def get_popular_players():
    """Get most popular players"""
    try:
        # In a real application, this would be determined by metrics like views, followers, etc.
        # For mock data, we'll just return all players ordered by ID
        sorted_players = sorted(players_data, key=lambda p: p['id'], reverse=True)
        popular_players = sorted_players[:5]  # Top 5 players
        
        return format_response(popular_players)
    
    except Exception as e:
        return format_error(f"Error retrieving popular players: {str(e)}")