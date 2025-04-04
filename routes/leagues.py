from flask import Blueprint, request, jsonify
import logging
from models import leagues_data, LeagueModel, PermissionType
from datetime import datetime
from utils.response_formatter import format_response, format_error
from utils.auth import require_permission
from flask_jwt_extended import jwt_required
from app import db
from sqlalchemy import desc

# Configure logger
logger = logging.getLogger(__name__)

# Create Blueprint
leagues_bp = Blueprint('leagues', __name__)

@leagues_bp.route('/', methods=['GET'])
@jwt_required()
def get_leagues():
    """Get all leagues with optional filtering"""
    try:
        # Query parameters for filtering
        category = request.args.get('category')
        country = request.args.get('country')
        enabled_only = request.args.get('enabled') == 'true'
        
        # Start with a query
        query = LeagueModel.query
        
        # Apply filters if provided
        if category:
            query = query.filter(LeagueModel.category.ilike(f"%{category}%"))
        if country:
            query = query.filter(LeagueModel.country.ilike(f"%{country}%"))
        if enabled_only:
            query = query.filter(LeagueModel.enabled == True)
            
        # Execute query
        leagues = query.all()
        
        # Convert to dictionary representation
        leagues_list = [league.to_dict() for league in leagues]
            
        return format_response(leagues_list)
    except Exception as e:
        logger.error(f"Error getting leagues: {str(e)}")
        return format_error(str(e)), 500

@leagues_bp.route('/<int:league_id>', methods=['GET'])
@jwt_required()
def get_league(league_id):
    """Get a specific league by ID"""
    try:
        league = LeagueModel.query.get(league_id)
        if league:
            return format_response(league.to_dict())
        return format_error("League not found"), 404
    except Exception as e:
        logger.error(f"Error getting league {league_id}: {str(e)}")
        return format_error(str(e)), 500

@leagues_bp.route('/', methods=['POST'])
@jwt_required()
@require_permission(PermissionType.LEAGUES)
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
                
        # Parse founded_date if provided
        founded_date = None
        if 'founded_date' in data and data['founded_date']:
            try:
                founded_date = datetime.fromisoformat(data['founded_date'])
            except ValueError:
                return format_error("Invalid date format for 'founded_date'. Use ISO format (YYYY-MM-DDTHH:MM:SS)"), 400
        
        # Create new league using SQLAlchemy model
        new_league = LeagueModel(
            name=data['name'],
            category=data['category'],
            country=data['country'],
            logo_url=data['logo_url'],
            popularity=data.get('popularity', 0),
            founded_date=founded_date,
            headquarters=data.get('headquarters', ''),
            commissioner=data.get('commissioner', ''),
            divisions=data.get('divisions', []),
            num_teams=data.get('num_teams', 0),
            enabled=data.get('enabled', True)
        )
        
        # Add and commit to database
        db.session.add(new_league)
        db.session.commit()
        
        return format_response(new_league.to_dict(), status_code=201)
    except Exception as e:
        logger.error(f"Error creating league: {str(e)}")
        db.session.rollback()
        return format_error(str(e)), 500

@leagues_bp.route('/<int:league_id>', methods=['PUT'])
@jwt_required()
@require_permission(PermissionType.LEAGUES)
def update_league(league_id):
    """Update an existing league"""
    try:
        data = request.json
        if not data:
            return format_error("Invalid request data"), 400
            
        # Find league
        league = LeagueModel.query.get(league_id)
        if league is None:
            return format_error("League not found"), 404
            
        # Update fields
        for key, value in data.items():
            # Special handling for founded_date
            if key == 'founded_date' and value:
                try:
                    league.founded_date = datetime.fromisoformat(value)
                except ValueError:
                    return format_error("Invalid date format for 'founded_date'. Use ISO format (YYYY-MM-DDTHH:MM:SS)"), 400
            # Update other fields
            elif key != 'id' and hasattr(league, key):
                setattr(league, key, value)
                
        # Commit changes to database
        db.session.commit()
        
        return format_response(league.to_dict())
    except Exception as e:
        logger.error(f"Error updating league {league_id}: {str(e)}")
        db.session.rollback()
        return format_error(str(e)), 500

@leagues_bp.route('/<int:league_id>/toggle-status', methods=['PATCH'])
@jwt_required()
@require_permission(PermissionType.LEAGUES)
def toggle_league_status(league_id):
    """Toggle league enabled/disabled status"""
    try:
        # Find league
        league = LeagueModel.query.get(league_id)
        if league is None:
            return format_error("League not found"), 404
            
        # Toggle the enabled status
        league.enabled = not league.enabled
                
        # Commit changes to database
        db.session.commit()
        
        return format_response({
            "message": f"League status toggled to {'enabled' if league.enabled else 'disabled'}",
            "league": league.to_dict()
        })
    except Exception as e:
        logger.error(f"Error toggling league status {league_id}: {str(e)}")
        db.session.rollback()
        return format_error(str(e)), 500

@leagues_bp.route('/<int:league_id>', methods=['DELETE'])
@jwt_required()
@require_permission(PermissionType.LEAGUES)
def delete_league(league_id):
    """Delete a league"""
    try:
        # Find league
        league = LeagueModel.query.get(league_id)
        if league is None:
            return format_error("League not found"), 404
            
        # Save league data before deletion
        league_dict = league.to_dict()
        
        # Remove league from database
        db.session.delete(league)
        db.session.commit()
        
        return format_response({
            "message": "League deleted successfully", 
            "deleted": league_dict
        })
    except Exception as e:
        logger.error(f"Error deleting league {league_id}: {str(e)}")
        db.session.rollback()
        return format_error(str(e)), 500

@leagues_bp.route('/popular', methods=['GET'])
@jwt_required()
def get_popular_leagues():
    """Get most popular leagues"""
    try:
        # Limit to top N
        limit = request.args.get('limit', default=5, type=int)
        
        # Query popular leagues with SQLAlchemy
        popular_leagues = LeagueModel.query.filter_by(enabled=True).order_by(
            desc(LeagueModel.popularity)
        ).limit(limit).all()
        
        # Convert to dictionary representation
        popular_leagues_list = [league.to_dict() for league in popular_leagues]
        
        return format_response(popular_leagues_list)
    except Exception as e:
        logger.error(f"Error getting popular leagues: {str(e)}")
        return format_error(str(e)), 500
