from flask import Blueprint, request, jsonify
import logging
from app import db
from sqlalchemy import desc
from flask_jwt_extended import jwt_required
from models import ReelModel, PlayerModel, TeamModel, LeagueModel, PermissionType
from utils.response_formatter import format_response, format_error
from utils.auth import require_permission

# Configure logger
logger = logging.getLogger(__name__)

reels_bp = Blueprint('reels', __name__)

@reels_bp.route('/', methods=['GET'])
@jwt_required()
@require_permission(PermissionType.REELS)
def get_reels():
    """Get all reels with optional filtering"""
    try:
        # Get query parameters for filtering
        player_id = request.args.get('player_id')
        limit = request.args.get('limit', default=20, type=int)
        
        # Start with base query
        query = ReelModel.query
        
        # Apply filters if provided
        if player_id:
            try:
                player_id_int = int(player_id)
                query = query.filter(ReelModel.player_id == player_id_int)
            except ValueError:
                return format_error("Invalid player_id format. Must be an integer.")
        
        # Order by creation date - newest first
        query = query.order_by(desc(ReelModel.created_at))
        
        # Limit the number of results
        query = query.limit(limit)
        
        # Execute query and convert to list of dictionaries
        reels = [reel.to_dict() for reel in query.all()]
        
        return format_response(reels)
    except Exception as e:
        logger.error(f"Error retrieving reels: {str(e)}")
        return format_error(str(e), status_code=500)

@reels_bp.route('/<int:reel_id>', methods=['GET'])
@jwt_required()
@require_permission(PermissionType.REELS)
def get_reel(reel_id):
    """Get a specific reel by ID"""
    try:
        # Get reel by ID
        reel = ReelModel.query.get(reel_id)
        
        if not reel:
            return format_error(f"Reel with ID {reel_id} not found", status_code=404)
        
        # Get associated player with eager loading of team and league
        player = PlayerModel.query.get(reel.player_id)
        
        if not player:
            return format_error(f"Player with ID {reel.player_id} not found", status_code=404)
        
        # Get team and league
        team = TeamModel.query.get(player.team_id)
        league = LeagueModel.query.get(player.league_id)
        
        # Prepare enriched reel data
        enriched_reel = {
            **reel.to_dict(),
            'player': player.to_dict() if player else None,
            'team': team.to_dict() if team else None,
            'league': league.to_dict() if league else None
        }
        
        return format_response(enriched_reel)
    except Exception as e:
        logger.error(f"Error retrieving reel {reel_id}: {str(e)}")
        return format_error(str(e), status_code=500)

@reels_bp.route('/popular', methods=['GET'])
@jwt_required()
@require_permission(PermissionType.REELS)
def get_popular_reels():
    """Get most popular reels"""
    try:
        # Get limit parameter
        limit = request.args.get('limit', default=5, type=int)
        
        # Query for popular reels by view count
        popular_reels = ReelModel.query.order_by(
            desc(ReelModel.view_count)
        ).limit(limit).all()
        
        # Convert to list of dictionaries
        reels_list = [reel.to_dict() for reel in popular_reels]
        
        return format_response(reels_list)
    except Exception as e:
        logger.error(f"Error retrieving popular reels: {str(e)}")
        return format_error(str(e), status_code=500)

@reels_bp.route('/with-player-details', methods=['GET'])
@jwt_required()
@require_permission(PermissionType.REELS)
def get_reels_with_player_details():
    """Get all reels with player, league, and team details for the manage reels page"""
    try:
        # Query all players with eager loading of teams and leagues
        players = PlayerModel.query.all()
        
        # Create a list of players with team and league details
        enriched_data = []
        
        for player in players:
            # Get team and league
            team = TeamModel.query.get(player.team_id)
            league = LeagueModel.query.get(player.league_id)
            
            if team and league:
                # Get reels for this player
                player_reels = ReelModel.query.filter_by(player_id=player.id).all()
                
                # Only include players who have reels
                if player_reels:
                    enriched_data.append({
                        'player_id': player.id,
                        'player_name': player.name,
                        'player_image': player.profile_image,
                        'team_name': team.name,
                        'team_logo': team.logo_url,
                        'league_name': league.name,
                        'league_logo': league.logo_url,
                        'reels_count': len(player_reels),
                        'reels': [reel.to_dict() for reel in player_reels]
                    })
        
        return format_response(enriched_data)
    except Exception as e:
        logger.error(f"Error retrieving reels with player details: {str(e)}")
        return format_error(str(e), status_code=500)