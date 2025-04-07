"""
User Authentication routes for the Gambit API.
Handles signup, login, profile management, and token generation for regular users.
Separate from admin authentication routes.
"""

import logging
import traceback
import uuid
from flask import Blueprint, request, jsonify, g, current_app
from flask_jwt_extended import get_jwt_identity, jwt_required, create_access_token, create_refresh_token
from datetime import datetime, timedelta
from models import UserModel, db
from utils.response_formatter import format_response, format_error
from sqlalchemy.exc import IntegrityError
# Randomly assign a subscription plan
from models import PlanModel, SubscriberModel
import random
from datetime import datetime, timedelta

# Configure logging
logger = logging.getLogger(__name__)

user_auth_bp = Blueprint('user_auth', __name__)

@user_auth_bp.route('/test', methods=['GET'])
def test():
    """Test route to verify API is running"""
    return format_response({"message": "User Auth API is working"})

@user_auth_bp.route('/signup', methods=['POST'])
def signup():
    """Register a new user account"""
    try:
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['email', 'username', 'password', 'full_name']
        for field in required_fields:
            if not data or not data.get(field):
                return format_error(f"Missing required field: {field}", status_code=400)
        
        # Check if email or username already exists
        email_exists = UserModel.query.filter_by(email=data['email']).first()
        if email_exists:
            return format_error("Email already registered", status_code=409)
        
        username_exists = UserModel.query.filter_by(username=data['username']).first()
        if username_exists:
            return format_error("Username already taken", status_code=409)
        
        # Create new user
        new_user = UserModel(
            uuid=str(uuid.uuid4()),
            email=data['email'],
            username=data['username'],
            full_name=data['full_name'],
            registration_date=datetime.now(),
            last_login=datetime.now(),
            status='active',
            profile_image=data.get('profile_image', f"https://ui-avatars.com/api/?name={data['username']}&background=random"),
            bio=data.get('bio', ''),
            role=data.get('role', 'user')  # Default role is 'user'
        )
        
        # Set password (this will hash it)
        new_user.set_password(data['password'])
        
        # Save to database
        db.session.add(new_user)
        db.session.flush()  # Flush to get the new user's ID
        
       
        
        # Get all active plans
        plans = PlanModel.query.filter_by(is_active=True).all()
        
        if plans:
            # Randomly select a plan
            selected_plan = random.choice(plans)
            
            # Set up subscription start and end dates
            start_date = datetime.now()
            end_date = start_date + timedelta(days=selected_plan.duration_days)
            
            # Create subscription with random payment method
            payment_methods = ["credit_card", "paypal", "apple_pay", "google_pay"]
            payment_method = random.choice(payment_methods)
            
            # Create a simple payment details object
            payment_details = {
                "last_four": f"{random.randint(1000, 9999)}",
                "expiry": f"{random.randint(1, 12)}/24"
            }
            
            # Create the subscription
            subscription = SubscriberModel(
                user_id=new_user.id,
                plan_id=selected_plan.id,
                start_date=start_date,
                end_date=end_date,
                status="active",
                payment_method=payment_method,
                payment_details=payment_details,
                auto_renew=True,
                created_at=start_date,
                updated_at=start_date
            )
            
            db.session.add(subscription)
            logger.info(f"Created subscription plan '{selected_plan.name}' for user {new_user.id}")
        else:
            logger.warning("No active plans found. User created without subscription.")
            
        db.session.commit()
        
        # Generate JWT tokens
        access_token = create_access_token(identity=str(new_user.id))
        refresh_token = create_refresh_token(identity=str(new_user.id))
        
        return format_response({
            'message': 'User registered successfully',
            'user': new_user.to_dict(),
            'access_token': access_token,
            'refresh_token': refresh_token
        })
        
    except IntegrityError as e:
        db.session.rollback()
        logger.error(f"Database integrity error: {str(e)}")
        return format_error("Database integrity error. User may already exist.", status_code=409)
    
    except Exception as e:
        db.session.rollback()
        logger.error(f"Signup error: {str(e)}")
        logger.error(traceback.format_exc())
        return format_error(f"Signup error: {str(e)}", status_code=500)

@user_auth_bp.route('/login', methods=['POST'])
def login():
    """Login route for users"""
    try:
        data = request.get_json()
        
        if not data or not data.get('username') or not data.get('password'):
            return format_error("Missing username/email or password", status_code=400)
        
        # Find user by username or email
        user = UserModel.query.filter(
            (UserModel.username == data['username']) | 
            (UserModel.email == data['username'])
        ).first()
        
        # Check if user exists and password is correct
        if not user or not user.check_password(data['password']):
            return format_error("Invalid username/email or password", status_code=401)
        
        # Check if account is active
        if user.status != 'active':
            return format_error("Your account has been deactivated or suspended", status_code=403)
        
        # Update last login time
        user.last_login = datetime.now()
        db.session.commit()
        
        # Generate tokens
        access_token = create_access_token(identity=str(user.id))
        refresh_token = create_refresh_token(identity=str(user.id))
        
        # Create the response with the token and user data
        response = format_response({
            'access_token': access_token,
            'refresh_token': refresh_token,
            'user': user.to_dict()
        })
        
        return response
    
    except Exception as e:
        logger.error(f"Login error: {str(e)}")
        logger.error(traceback.format_exc())
        return format_error(f"Login error: {str(e)}", status_code=500)

@user_auth_bp.route('/refresh', methods=['POST'])
@jwt_required(refresh=True)
def refresh_token():
    """Refresh access token using refresh token"""
    try:
        # Get the user identity from the refresh token
        user_id = get_jwt_identity()
        
        # Create a new access token
        access_token = create_access_token(identity=user_id)
        
        return format_response({
            'access_token': access_token
        })
    
    except Exception as e:
        logger.error(f"Token refresh error: {str(e)}")
        return format_error(f"Token refresh error: {str(e)}", status_code=500)

@user_auth_bp.route('/me', methods=['GET'])
@jwt_required()
def get_user_profile():
    """Get current authenticated user profile"""
    try:
        user_id = get_jwt_identity()
        
        # Convert user_id back to integer if it's a string
        if isinstance(user_id, str):
            user_id = int(user_id)
        
        user = UserModel.query.get(user_id)
        
        if not user:
            return format_error("Invalid authentication credentials", status_code=401)
        
        return format_response(user.to_dict())
    
    except Exception as e:
        return format_error(f"Error retrieving user profile: {str(e)}", status_code=500)

@user_auth_bp.route('/me', methods=['PUT'])
@jwt_required()
def update_user_profile():
    """Update current authenticated user profile"""
    try:
        user_id = get_jwt_identity()
        
        # Convert user_id back to integer if it's a string
        if isinstance(user_id, str):
            user_id = int(user_id)
        
        user = UserModel.query.get(user_id)
        
        if not user:
            return format_error("Invalid authentication credentials", status_code=401)
        
        data = request.get_json()
        
        # Update user fields (except sensitive ones like id, email, username which should have separate endpoints)
        allowed_fields = ['full_name', 'bio', 'profile_image']
        for field in allowed_fields:
            if field in data:
                setattr(user, field, data[field])
        
        user.updated_at = datetime.now()
        db.session.commit()
        
        return format_response({
            'message': 'Profile updated successfully',
            'user': user.to_dict()
        })
    
    except Exception as e:
        db.session.rollback()
        return format_error(f"Error updating profile: {str(e)}", status_code=500)

@user_auth_bp.route('/change-password', methods=['POST'])
@jwt_required()
def change_password():
    """Change password for current user"""
    try:
        user_id = get_jwt_identity()
        
        # Convert user_id back to integer if it's a string
        if isinstance(user_id, str):
            user_id = int(user_id)
            
        user = UserModel.query.get(user_id)
        
        if not user:
            return format_error("Invalid authentication credentials", status_code=401)
        
        data = request.get_json()
        
        if not data or not data.get('current_password') or not data.get('new_password'):
            return format_error("Missing current password or new password", status_code=400)
        
        # Verify current password
        if not user.check_password(data['current_password']):
            return format_error("Current password is incorrect", status_code=400)
        
        # Set new password
        user.set_password(data['new_password'])
        user.updated_at = datetime.now()
        db.session.commit()
        
        return format_response({"message": "Password changed successfully"})
    
    except Exception as e:
        db.session.rollback()
        return format_error(f"Error changing password: {str(e)}", status_code=500)

@user_auth_bp.route('/subscription', methods=['GET'])
@jwt_required()
def get_user_subscription():
    """Get current authenticated user's subscription details"""
    try:
        user_id = get_jwt_identity()
        
        # Convert user_id back to integer if it's a string
        if isinstance(user_id, str):
            user_id = int(user_id)
        
        user = UserModel.query.get(user_id)
        
        if not user:
            return format_error("Invalid authentication credentials", status_code=401)
        
        from models import SubscriberModel, PlanModel
        
        # Get the user's subscription with plan details
        subscription = (db.session.query(SubscriberModel, PlanModel)
                        .join(PlanModel, SubscriberModel.plan_id == PlanModel.id)
                        .filter(SubscriberModel.user_id == user_id)
                        .first())
        
        subscription_data = None
        
        if subscription:
            sub, plan = subscription
            days_remaining = 0
            if sub.end_date > datetime.now():
                days_remaining = (sub.end_date - datetime.now()).days
            
            # Format the price with 2 decimal places
            formatted_price = f"${plan.price:.2f}"
                
            subscription_data = {
                "id": sub.id,
                "status": sub.status,
                "start_date": sub.start_date.isoformat(),
                "end_date": sub.end_date.isoformat(),
                "expiry_date": sub.end_date.strftime("%d %b, %Y"),
                "days_remaining": days_remaining,
                "auto_renew": sub.auto_renew,
                "payment_method": sub.payment_method,
                "payment_details": sub.payment_details,
                "plan": {
                    "id": plan.id,
                    "name": plan.name,
                    "description": plan.description,
                    "price": plan.price,
                    "formatted_price": formatted_price,
                    "duration_days": plan.duration_days
                }
            }
        
        # Determine if user has premium access
        is_premium = False
        if subscription_data and subscription_data["status"] == "active":
            is_premium = True
        
        return format_response({
            "subscription": subscription_data,
            "is_premium": is_premium
        })
    
    except Exception as e:
        logger.error(f"Error retrieving user subscription: {str(e)}")
        logger.error(traceback.format_exc())
        return format_error(f"Error retrieving subscription details: {str(e)}", status_code=500)