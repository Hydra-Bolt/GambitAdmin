from flask import Blueprint, jsonify
import logging
from models import SubscriberModel, UserModel, LeagueModel, TeamModel, UserActivityModel
from utils.response_formatter import format_response, format_error
from flask_jwt_extended import jwt_required
from utils.auth import require_permission
from models import PermissionType
from datetime import datetime, timedelta

# Configure logger
logger = logging.getLogger(__name__)

# Create Blueprint
dashboard_bp = Blueprint('dashboard', __name__)

@dashboard_bp.route('/', methods=['GET'])
def get_dashboard_data():
    """Get all dashboard data in a single request"""
    try:
        # Get subscriber counts from database
        total_subscribers = SubscriberModel.query.count()
        monthly_subscribers = SubscriberModel.query.filter_by(subscription_type='monthly', status='active').count()
        yearly_subscribers = SubscriberModel.query.filter_by(subscription_type='yearly', status='active').count()
        
        # Get most popular league
        most_viewed_league = LeagueModel.query.order_by(LeagueModel.popularity.desc()).first()
        
        # Get most popular team
        most_viewed_team = TeamModel.query.order_by(TeamModel.popularity.desc()).first()
        
        # Get user activity for the last 30 days
        thirty_days_ago = datetime.now() - timedelta(days=30)
        user_activity = UserActivityModel.query\
            .filter(UserActivityModel.date >= thirty_days_ago)\
            .order_by(UserActivityModel.date.asc())\
            .all()
        
        # Compile dashboard data
        dashboard_data = {
            "subscribers": {
                "total": total_subscribers,
                "monthly": monthly_subscribers,
                "yearly": yearly_subscribers
            },
            "popular_content": {
                "most_viewed_league": most_viewed_league.to_dict() if most_viewed_league else {"name": "No leagues found"},
                "most_viewed_team": most_viewed_team.to_dict() if most_viewed_team else {"name": "No teams found"}
            },
            "user_activity": [activity.to_dict() for activity in user_activity]
        }
        
        return format_response(dashboard_data)
    except Exception as e:
        logger.error(f"Error getting dashboard data: {str(e)}")
        return format_error(str(e), status_code=500)

@dashboard_bp.route('/subscribers', methods=['GET'])
def get_subscriber_overview():
    """Get subscriber overview data"""
    try:
        # Get subscriber counts
        total_subscribers = SubscriberModel.query.count()
        monthly_subscribers = SubscriberModel.query.filter_by(subscription_type='monthly', status='active').count()
        yearly_subscribers = SubscriberModel.query.filter_by(subscription_type='yearly', status='active').count()
        
        subscriber_overview = {
            "total": total_subscribers,
            "monthly": monthly_subscribers,
            "yearly": yearly_subscribers
        }
        
        return format_response(subscriber_overview)
    except Exception as e:
        logger.error(f"Error getting subscriber overview: {str(e)}")
        return format_error(str(e)), 500

@dashboard_bp.route('/users', methods=['GET'])
def get_user_overview():
    """Get user statistics overview"""
    try:
        # Get active users count
        active_users = UserModel.query.filter_by(status='active').count()
        
        # Get new users count (registered in the last 30 days)
        thirty_days_ago = datetime.now() - timedelta(days=30)
        new_users = UserModel.query.filter(UserModel.registration_date > thirty_days_ago).count()
        
        user_overview = {
            "total_users": UserModel.query.count(),
            "active_users": active_users,
            "new_users": new_users
        }
        
        return format_response(user_overview)
    except Exception as e:
        logger.error(f"Error getting user overview: {str(e)}")
        return format_error(str(e)), 500

@dashboard_bp.route('/popular', methods=['GET'])
def get_popular_content():
    """Get most popular content"""
    try:
        # Get most popular leagues
        top_leagues = LeagueModel.query.order_by(LeagueModel.popularity.desc()).limit(5).all()
        
        # Get most popular teams
        top_teams = TeamModel.query.order_by(TeamModel.popularity.desc()).limit(5).all()
        
        popular_content = {
            "top_leagues": [league.to_dict() for league in top_leagues],
            "top_teams": [team.to_dict() for team in top_teams]
        }
        
        return format_response(popular_content)
    except Exception as e:
        logger.error(f"Error getting popular content: {str(e)}")
        return format_error(str(e)), 500

@dashboard_bp.route('/manage-leagues', methods=['GET'])
def manage_leagues():
    """Serve the Manage Leagues page"""
    try:
        # Fetch leagues data (this can be extended to fetch from the database or API)
        from flask import render_template
        return render_template('manage_leagues.html')
    except Exception as e:
        logger.error(f"Error loading Manage Leagues page: {str(e)}")
        return format_error(str(e)), 500
