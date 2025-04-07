from flask import Blueprint, request, jsonify
import logging
from models import OddsModel, PermissionType
from datetime import datetime
from utils.response_formatter import format_response, format_error
from utils.auth import require_permission
from flask_jwt_extended import jwt_required
from app import db
from sqlalchemy import desc, func
from utils.odds_api import OddsAPI
import os

# Configure logger
logger = logging.getLogger(__name__)

# Create Blueprint
odds_bp = Blueprint('odds', __name__)

# Initialize the Odds API client
odds_api = OddsAPI()

def parse_iso_date(date_string):
    """
    Parse ISO 8601 date string to datetime object.
    Handles the 'Z' timezone designator which datetime.fromisoformat() doesn't support.
    """
    if date_string.endswith('Z'):
        # Replace 'Z' with '+00:00' (UTC timezone) which fromisoformat supports
        date_string = date_string[:-1] + '+00:00'
    return datetime.fromisoformat(date_string)

@odds_bp.route('/sports', methods=['GET'])
@jwt_required()
@require_permission(PermissionType.ODDS)
def get_sports():
    """Get all available sports from the Odds API"""
    try:
        sports = odds_api.get_sports()
        return format_response(sports)
    except Exception as e:
        logger.error(f"Error getting sports: {str(e)}")
        return format_error(str(e))  # format_error already returns status 500 by default

@odds_bp.route('/odds/<sport_key>', methods=['GET'])
@jwt_required()
@require_permission(PermissionType.ODDS)
def get_odds_for_sport(sport_key):
    """Get odds for a specific sport"""
    try:
        regions = request.args.get('regions', 'us')
        markets = request.args.get('markets', 'h2h')
        
        odds_data = odds_api.get_odds(
            sport=sport_key,
            regions=regions,
            markets=markets
        )
        
        # Store odds in database for future reference
        for event in odds_data:
            # Check if event already exists
            existing = OddsModel.query.filter_by(event_id=event['id']).first()
            
            # Convert ISO timestamp to datetime
            event_time = parse_iso_date(event['commence_time'])
            
            if existing:
                # Update existing event
                existing.home_team = event['home_team']
                existing.away_team = event['away_team']
                existing.event_time = event_time
                existing.bookmakers = event['bookmakers']
                existing.last_update = datetime.now()
                existing.updated_at = datetime.now()
            else:
                # Create new event
                new_odds = OddsModel(
                    sport_key=event['sport_key'],
                    sport_title=event['sport_title'],
                    event_id=event['id'],
                    event_time=event_time,
                    home_team=event['home_team'],
                    away_team=event['away_team'],
                    bookmakers=event['bookmakers']
                )
                db.session.add(new_odds)
        
        # Commit changes to database
        db.session.commit()
        
        return format_response(odds_data)
    except Exception as e:
        logger.error(f"Error getting odds for sport {sport_key}: {str(e)}")
        db.session.rollback()
        return format_error(str(e))

@odds_bp.route('/event/<sport_key>/<event_id>', methods=['GET'])
@jwt_required()
@require_permission(PermissionType.ODDS)
def get_event_odds(sport_key, event_id):
    """Get odds for a specific event"""
    try:
        regions = request.args.get('regions', 'us')
        markets = request.args.get('markets', 'h2h')
        
        event_odds = odds_api.get_event_odds(
            sport=sport_key,
            event_id=event_id,
            regions=regions,
            markets=markets
        )
        
        return format_response(event_odds)
    except Exception as e:
        logger.error(f"Error getting event odds for {sport_key}/{event_id}: {str(e)}")
        return format_error(str(e))

@odds_bp.route('/cached', methods=['GET'])
@jwt_required()
@require_permission(PermissionType.ODDS)
def get_cached_odds():
    """Get cached odds from the database"""
    try:
        # Query parameters for filtering
        sport_key = request.args.get('sport_key')
        home_team = request.args.get('home_team')
        away_team = request.args.get('away_team')
        limit = request.args.get('limit', 20, type=int)
        
        # Start with a query
        query = OddsModel.query
        
        # Apply filters if provided
        if sport_key:
            query = query.filter(OddsModel.sport_key == sport_key)
        if home_team:
            query = query.filter(OddsModel.home_team.ilike(f"%{home_team}%"))
        if away_team:
            query = query.filter(OddsModel.away_team.ilike(f"%{away_team}%"))
            
        # Get only upcoming events
        query = query.filter(OddsModel.event_time > func.now())
        
        # Order by event time (ascending) and apply limit
        odds_list = query.order_by(OddsModel.event_time).limit(limit).all()
        
        # Convert to dictionary representation
        odds_dict_list = [odds.to_dict() for odds in odds_list]
            
        return format_response(odds_dict_list)
    except Exception as e:
        logger.error(f"Error getting cached odds: {str(e)}")
        return format_error(str(e))

@odds_bp.route('/sync', methods=['POST'])
@jwt_required()
@require_permission(PermissionType.ODDS)
def sync_odds():
    """Force sync odds for all or specific sports"""
    try:
        data = request.json or {}
        sport_keys = data.get('sport_keys', [])
        
        if not sport_keys:
            # Get all sports if none specified
            sports = odds_api.get_sports()
            sport_keys = [sport['key'] for sport in sports]
            
        results = {}
        
        for sport_key in sport_keys:
            try:
                # Get odds for this sport
                odds_data = odds_api.get_odds(sport=sport_key)
                
                # Count how many events were fetched
                results[sport_key] = len(odds_data)
                
                # Store in database (same logic as get_odds_for_sport)
                for event in odds_data:
                    existing = OddsModel.query.filter_by(event_id=event['id']).first()
                    event_time = parse_iso_date(event['commence_time'])
                    
                    if existing:
                        existing.home_team = event['home_team']
                        existing.away_team = event['away_team']
                        existing.event_time = event_time
                        existing.bookmakers = event['bookmakers']
                        existing.last_update = datetime.now()
                        existing.updated_at = datetime.now()
                    else:
                        new_odds = OddsModel(
                            sport_key=event['sport_key'],
                            sport_title=event['sport_title'],
                            event_id=event['id'],
                            event_time=event_time,
                            home_team=event['home_team'],
                            away_team=event['away_team'],
                            bookmakers=event['bookmakers']
                        )
                        db.session.add(new_odds)
                
                # Commit changes for this sport
                db.session.commit()
                
            except Exception as e:
                logger.error(f"Error syncing odds for sport {sport_key}: {str(e)}")
                results[sport_key] = f"Error: {str(e)}"
                db.session.rollback()
        
        return format_response({
            "message": "Odds sync completed",
            "results": results
        })
    except Exception as e:
        logger.error(f"Error in odds sync process: {str(e)}")
        return format_error(str(e))