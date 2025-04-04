from flask import Blueprint, request, jsonify
import logging
from datetime import datetime
from app import db
from sqlalchemy import desc
from models import UserModel, UserActivityModel, TeamModel, LeagueModel, PlayerModel, SubscriberModel
from utils.response_formatter import format_response, format_error

# Configure logger
logger = logging.getLogger(__name__)

# Create Blueprint
users_bp = Blueprint('users', __name__)

@users_bp.route('/', methods=['GET'])
def get_users():
    """Get all users with optional filtering"""
    try:
        # Query parameters for filtering
        status = request.args.get('status')
        
        # Base query
        query = UserModel.query
        
        # Apply filters if provided
        if status:
            query = query.filter(UserModel.status == status)
            
        # Execute query and convert to list of dictionaries
        users = [user.to_dict() for user in query.all()]
            
        return format_response(users)
    except Exception as e:
        logger.error(f"Error getting users: {str(e)}")
        return format_error(str(e), status_code=500)

@users_bp.route('/<int:user_id>', methods=['GET'])
def get_user(user_id):
    """Get a specific user by ID"""
    try:
        user = UserModel.query.get(user_id)
        if user:
            return format_response(user.to_dict())
        return format_error("User not found", status_code=404)
    except Exception as e:
        logger.error(f"Error getting user {user_id}: {str(e)}")
        return format_error(str(e), status_code=500)
        
@users_bp.route('/uuid/<string:user_uuid>', methods=['GET'])
def get_user_by_uuid(user_uuid):
    """Get a specific user by UUID"""
    try:
        user = UserModel.query.filter_by(uuid=user_uuid).first()
        if user:
            return format_response(user.to_dict())
        return format_error("User not found", status_code=404)
    except Exception as e:
        logger.error(f"Error getting user by UUID {user_uuid}: {str(e)}")
        return format_error(str(e), status_code=500)

@users_bp.route('/', methods=['POST'])
def create_user():
    """Create a new user"""
    try:
        data = request.json
        if not data:
            return format_error("Invalid request data", status_code=400)
            
        # Validate required fields
        required_fields = ['email', 'username', 'status', 'full_name']
        for field in required_fields:
            if field not in data:
                return format_error(f"Missing required field: {field}", status_code=400)
        
        # Create a UUID if one wasn't provided
        if 'uuid' not in data or not data['uuid']:
            import uuid
            data['uuid'] = f"user-{str(uuid.uuid4())}"
        
        # Create new user object
        new_user = UserModel(
            email=data['email'],
            username=data['username'],
            uuid=data['uuid'],
            full_name=data['full_name'],
            profile_image=data.get('profile_image', f"https://ui-avatars.com/api/?name={data['username']}&background=random"),
            registration_date=datetime.now(),
            last_login=datetime.now(),
            status=data['status']
        )
        
        # Add to database
        db.session.add(new_user)
        db.session.commit()
        
        return format_response(new_user.to_dict(), status_code=201)
    except Exception as e:
        logger.error(f"Error creating user: {str(e)}")
        db.session.rollback()
        return format_error(str(e), status_code=500)

@users_bp.route('/<int:user_id>', methods=['PUT'])
def update_user(user_id):
    """Update an existing user"""
    try:
        data = request.json
        if not data:
            return format_error("Invalid request data", status_code=400)
            
        # Find user
        user = UserModel.query.get(user_id)
        if not user:
            return format_error("User not found", status_code=404)
            
        # Update fields
        for key, value in data.items():
            if hasattr(user, key) and key not in ['id', 'created_at', 'updated_at']:
                setattr(user, key, value)
                
        # Save to database
        db.session.commit()
        
        return format_response(user.to_dict())
    except Exception as e:
        logger.error(f"Error updating user {user_id}: {str(e)}")
        db.session.rollback()
        return format_error(str(e), status_code=500)

@users_bp.route('/<int:user_id>', methods=['DELETE'])
def delete_user(user_id):
    """Delete a user"""
    try:
        # Find user
        user = UserModel.query.get(user_id)
        if not user:
            return format_error("User not found", status_code=404)
        
        # Save user data before deletion for response
        user_dict = user.to_dict()
            
        # Remove from database
        db.session.delete(user)
        db.session.commit()
        
        return format_response({"message": "User deleted successfully", "user": user_dict})
    except Exception as e:
        logger.error(f"Error deleting user {user_id}: {str(e)}")
        db.session.rollback()
        return format_error(str(e), status_code=500)

@users_bp.route('/stats', methods=['GET'])
def get_user_stats():
    """Get user statistics"""
    try:
        # Calculate user statistics
        total_users = UserModel.query.count()
        active_users = UserModel.query.filter_by(status='active').count()
        inactive_users = UserModel.query.filter_by(status='inactive').count()
        suspended_users = UserModel.query.filter_by(status='suspended').count()
        
        # Calculate recent registrations - users registered in the last 30 days
        import datetime as dt
        thirty_days_ago = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0) - dt.timedelta(days=30)
        recent_users = UserModel.query.filter(UserModel.registration_date >= thirty_days_ago).count()
        
        # Format response
        stats = {
            "total_users": total_users,
            "active_users": active_users,
            "inactive_users": inactive_users,
            "suspended_users": suspended_users,
            "recent_registrations": recent_users
        }
        return format_response(stats)
    except Exception as e:
        logger.error(f"Error getting user stats: {str(e)}")
        return format_error(str(e), status_code=500)

@users_bp.route('/activity', methods=['GET'])
def get_user_activity():
    """Get user activity data for charting"""
    try:
        # Parse date range parameters
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')
        
        # Base query
        query = UserActivityModel.query
        
        # Apply date filters if provided
        if start_date:
            start = datetime.fromisoformat(start_date)
            query = query.filter(UserActivityModel.date >= start)
            
        if end_date:
            end = datetime.fromisoformat(end_date)
            query = query.filter(UserActivityModel.date <= end)
        
        # Order by date
        query = query.order_by(UserActivityModel.date)
        
        # Execute query and convert to list of dictionaries
        activity_data = [activity.to_dict() for activity in query.all()]
        
        return format_response(activity_data)
    except Exception as e:
        logger.error(f"Error getting user activity: {str(e)}")
        return format_error(str(e), status_code=500)

@users_bp.route('/profile/uuid/<string:user_uuid>', methods=['GET'])
def get_user_profile(user_uuid):
    """Get a detailed user profile by UUID with favorites data"""
    try:
        # Find user by UUID
        user = UserModel.query.filter_by(uuid=user_uuid).first()
        if not user:
            return format_error("User not found", status_code=404)
        
        # Get basic user data
        user_data = user.to_dict()
        
        # Get subscription details if they exist
        subscription = SubscriberModel.query.filter_by(email=user.email).first()
        subscription_data = None
        if subscription:
            subscription_data = {
                "type": subscription.subscription_type,
                "amount": "$450.9" if subscription.subscription_type == "yearly" else "$39.9",
                "expiry_date": subscription.end_date.strftime("%d/%m/%Y")
            }
        
        # Get favorite sports data (already stored as strings)
        favorite_sports_data = []
        for sport in user.favorite_sports or []:
            favorite_sports_data.append({
                "name": sport,
                "logo_url": get_sport_logo_url(sport)
            })
        
        # Get favorite teams data
        favorite_teams_data = []
        for team_id in user.favorite_teams or []:
            team = TeamModel.query.get(team_id)
            if team:
                favorite_teams_data.append({
                    "id": team.id,
                    "name": team.name,
                    "logo_url": team.logo_url
                })
        
        # Get favorite players data
        favorite_players_data = []
        for player_id in user.favorite_players or []:
            player = PlayerModel.query.get(player_id)
            if player:
                favorite_players_data.append({
                    "id": player.id,
                    "name": player.name,
                    "profile_image": player.profile_image
                })
        
        # Construct complete profile response
        profile_data = {
            "user": user_data,
            "subscription": subscription_data,
            "favorite_sports": favorite_sports_data,
            "favorite_teams": favorite_teams_data,
            "favorite_players": favorite_players_data
        }
        
        return format_response(profile_data)
    except Exception as e:
        logger.error(f"Error getting user profile by UUID {user_uuid}: {str(e)}")
        return format_error(str(e), status_code=500)

@users_bp.route('/profile/uuid/<string:user_uuid>/update-favorites', methods=['PUT'])
def update_user_favorites(user_uuid):
    """Update a user's favorite sports, teams, and players"""
    try:
        # Find user by UUID
        user = UserModel.query.filter_by(uuid=user_uuid).first()
        if not user:
            return format_error("User not found", status_code=404)
        
        data = request.json
        if not data:
            return format_error("No data provided", status_code=400)
        
        # Update favorites if provided
        if 'favorite_sports' in data:
            user.favorite_sports = data['favorite_sports']
            
        if 'favorite_teams' in data:
            user.favorite_teams = data['favorite_teams']
            
        if 'favorite_players' in data:
            user.favorite_players = data['favorite_players']
        
        # Save changes to database
        db.session.commit()
        
        # Return updated user data
        return format_response(user.to_dict())
    except Exception as e:
        logger.error(f"Error updating user favorites for UUID {user_uuid}: {str(e)}")
        db.session.rollback()
        return format_error(str(e), status_code=500)

@users_bp.route('/profile/uuid/<string:user_uuid>/restrict', methods=['POST'])
def restrict_user(user_uuid):
    """Restrict a user by changing their status to 'suspended'"""
    try:
        # Find user by UUID
        user = UserModel.query.filter_by(uuid=user_uuid).first()
        if not user:
            return format_error("User not found", status_code=404)
        
        # Change status to suspended
        user.status = 'suspended'
        db.session.commit()
        
        return format_response({
            "message": f"User {user.username} has been restricted",
            "user": user.to_dict()
        })
    except Exception as e:
        logger.error(f"Error restricting user with UUID {user_uuid}: {str(e)}")
        db.session.rollback()
        return format_error(str(e), status_code=500)

def get_sport_logo_url(sport_name):
    """Get a logo URL for a given sport name"""
    # Map of sport names to their logo URLs
    sport_logos = {
        "NFL": "https://upload.wikimedia.org/wikipedia/en/thumb/a/a2/National_Football_League_logo.svg/800px-National_Football_League_logo.svg.png",
        "NBA": "https://upload.wikimedia.org/wikipedia/en/thumb/0/03/National_Basketball_Association_logo.svg/800px-National_Basketball_Association_logo.svg.png",
        "MLB": "https://upload.wikimedia.org/wikipedia/en/thumb/a/a6/Major_League_Baseball_logo.svg/800px-Major_League_Baseball_logo.svg.png",
        "NCAA-Football": "https://upload.wikimedia.org/wikipedia/commons/thumb/d/dd/NCAA_logo.svg/800px-NCAA_logo.svg.png"
    }
    return sport_logos.get(sport_name, "https://placehold.co/400x400?text=Sport")
