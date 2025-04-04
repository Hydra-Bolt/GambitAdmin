from flask import Blueprint, jsonify
import logging
from models import subscribers_data, users_data, leagues_data, teams_data, user_activity_data
from utils.response_formatter import format_response, format_error

# Configure logger
logger = logging.getLogger(__name__)

# Create Blueprint
dashboard_bp = Blueprint('dashboard', __name__)

@dashboard_bp.route('/', methods=['GET'])
def get_dashboard_data():
    """Get all dashboard data in a single request"""
    try:
        # Get subscriber counts
        total_subscribers = len(subscribers_data)
        monthly_subscribers = len([s for s in subscribers_data if s['subscription_type'] == 'monthly' and s['status'] == 'active'])
        yearly_subscribers = len([s for s in subscribers_data if s['subscription_type'] == 'yearly' and s['status'] == 'active'])
        
        # Get most popular league
        most_viewed_league = max(leagues_data, key=lambda x: x['popularity']) if leagues_data else None
        
        # Get most popular team
        most_viewed_team = max(teams_data, key=lambda x: x['popularity']) if teams_data else None
        
        # Compile dashboard data
        dashboard_data = {
            "subscribers": {
                "total": total_subscribers,
                "monthly": monthly_subscribers,
                "yearly": yearly_subscribers,
                "growth_rate": 0.8  # This would be calculated from historical data
            },
            "popular_content": {
                "most_viewed_league": most_viewed_league,
                "most_viewed_team": most_viewed_team
            },
            "user_activity": user_activity_data
        }
        
        return format_response(dashboard_data)
    except Exception as e:
        logger.error(f"Error getting dashboard data: {str(e)}")
        return format_error(str(e)), 500

@dashboard_bp.route('/subscribers', methods=['GET'])
def get_subscriber_overview():
    """Get subscriber overview data"""
    try:
        # Get subscriber counts
        total_subscribers = len(subscribers_data)
        monthly_subscribers = len([s for s in subscribers_data if s['subscription_type'] == 'monthly' and s['status'] == 'active'])
        yearly_subscribers = len([s for s in subscribers_data if s['subscription_type'] == 'yearly' and s['status'] == 'active'])
        
        # Get subscription growth rate
        growth_rate = 0.8  # This would be calculated from historical data
        
        subscriber_overview = {
            "total": total_subscribers,
            "monthly": monthly_subscribers,
            "yearly": yearly_subscribers,
            "growth_rate": growth_rate
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
        active_users = len([u for u in users_data if u['status'] == 'active'])
        
        # Get new users count (registered in the last 30 days)
        from datetime import datetime, timedelta
        thirty_days_ago = (datetime.now() - timedelta(days=30)).isoformat()
        new_users = len([u for u in users_data if u['registration_date'] > thirty_days_ago])
        
        user_overview = {
            "total_users": len(users_data),
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
        sorted_leagues = sorted(leagues_data, key=lambda x: x['popularity'], reverse=True)
        top_leagues = sorted_leagues[:5] if sorted_leagues else []
        
        # Get most popular teams
        sorted_teams = sorted(teams_data, key=lambda x: x['popularity'], reverse=True)
        top_teams = sorted_teams[:5] if sorted_teams else []
        
        popular_content = {
            "top_leagues": top_leagues,
            "top_teams": top_teams
        }
        
        return format_response(popular_content)
    except Exception as e:
        logger.error(f"Error getting popular content: {str(e)}")
        return format_error(str(e)), 500
