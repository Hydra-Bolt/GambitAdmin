from flask import Blueprint, request, jsonify
from models import players_data, reels_data, teams_data, leagues_data
from utils.response_formatter import format_response, format_error

reels_bp = Blueprint('reels', __name__)

@reels_bp.route('/', methods=['GET'])
def get_reels():
    """Get all reels with optional filtering"""
    try:
        # Get query parameters for filtering
        player_id = request.args.get('player_id')
        limit = request.args.get('limit', default=20, type=int)
        
        # Apply filters if provided
        filtered_reels = reels_data
        
        if player_id:
            filtered_reels = [r for r in filtered_reels if r['player_id'] == int(player_id)]
        
        # Limit the number of results
        limited_reels = filtered_reels[:limit]
        
        return format_response(limited_reels)
    
    except Exception as e:
        return format_error(f"Error retrieving reels: {str(e)}")

@reels_bp.route('/<int:reel_id>', methods=['GET'])
def get_reel(reel_id):
    """Get a specific reel by ID"""
    try:
        reel = next((r for r in reels_data if r['id'] == reel_id), None)
        
        if not reel:
            return format_error(f"Reel with ID {reel_id} not found", status_code=404)
        
        # Get player information
        player_id = reel['player_id']
        player = next((p for p in players_data if p['id'] == player_id), None)
        
        # Get team and league information
        team_id = player['team_id'] if player else None
        league_id = player['league_id'] if player else None
        
        team = next((t for t in teams_data if t['id'] == team_id), None) if team_id else None
        league = next((l for l in leagues_data if l['id'] == league_id), None) if league_id else None
        
        # Prepare enriched reel data
        enriched_reel = {
            **reel,
            'player': player,
            'team': team,
            'league': league
        }
        
        return format_response(enriched_reel)
    
    except Exception as e:
        return format_error(f"Error retrieving reel: {str(e)}")

@reels_bp.route('/popular', methods=['GET'])
def get_popular_reels():
    """Get most popular reels"""
    try:
        # Sort reels by view count for popularity
        sorted_reels = sorted(reels_data, key=lambda r: r.get('view_count', 0), reverse=True)
        popular_reels = sorted_reels[:5]  # Top 5 reels
        
        return format_response(popular_reels)
    
    except Exception as e:
        return format_error(f"Error retrieving popular reels: {str(e)}")

@reels_bp.route('/manage', methods=['GET'])
def get_reels_with_player_details():
    """Get all reels with player, league, and team details for the manage reels page"""
    try:
        # Create a list of reels with player, team, and league details
        enriched_reels = []
        
        for player in players_data:
            player_id = player['id']
            player_name = player['name']
            team_id = player['team_id']
            league_id = player['league_id']
            
            # Get team and league information
            team = next((t for t in teams_data if t['id'] == team_id), None)
            league = next((l for l in leagues_data if l['id'] == league_id), None)
            
            if team and league:
                enriched_reels.append({
                    'player_id': player_id,
                    'player_name': player_name,
                    'player_image': player['profile_image'],
                    'team_name': team['name'],
                    'team_logo': team['logo_url'],
                    'league_name': league['name'],
                    'league_logo': league['logo_url']
                })
        
        return format_response(enriched_reels)
    
    except Exception as e:
        return format_error(f"Error retrieving reels with details: {str(e)}")