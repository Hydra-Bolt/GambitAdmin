# Database models for the Gambit Admin API
# This file defines the SQLAlchemy models for the PostgreSQL database

from datetime import datetime
import uuid
from flask_bcrypt import Bcrypt
from typing import Dict, List, Any, Optional, Union
from sqlalchemy import String, Integer, DateTime, Boolean, Float, ForeignKey, Text, Table, Column
from sqlalchemy.dialects.postgresql import ARRAY, JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship
from flask_login import UserMixin
from app import db, app

bcrypt = Bcrypt(app)

# Global variables to maintain backward compatibility during transition
subscribers_data: List[Dict[str, Any]] = []
users_data: List[Dict[str, Any]] = []
leagues_data: List[Dict[str, Any]] = []
teams_data: List[Dict[str, Any]] = []
players_data: List[Dict[str, Any]] = []
reels_data: List[Dict[str, Any]] = []
user_activity_data: List[Dict[str, Any]] = []
notifications_data: List[Dict[str, Any]] = []

# Association table for admin-role many-to-many relationship
admin_roles = Table('admin_roles',
    db.Model.metadata,
    Column('admin_id', Integer, ForeignKey('admins.id'), primary_key=True),
    Column('role_id', Integer, ForeignKey('roles.id'), primary_key=True)
)

# Define role permissions
class PermissionType:
    CONTENT = "content"
    NOTIFICATION = "notification"
    LEAGUES = "leagues"
    REELS = "reels"
    USERS = "users"
    SUBSCRIBERS = "subscribers"
    ROLES = "roles"
    ODDS = "odds"  # New permission for odds data
    ALL = "all"

# Admin user model
class AdminModel(db.Model, UserMixin):
    __tablename__ = 'admins'
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    username: Mapped[str] = mapped_column(String(64), unique=True, nullable=False)
    name: Mapped[str] = mapped_column(String(120), nullable=False)
    email: Mapped[str] = mapped_column(String(120), unique=True, nullable=False)
    password_hash: Mapped[str] = mapped_column(String(256), nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    last_login: Mapped[datetime] = mapped_column(DateTime, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now, onupdate=datetime.now)
    
    # Relationship with roles
    roles = relationship('RoleModel', secondary=admin_roles, backref='admins')
    
    def set_password(self, password):
        """Hash the password for storage"""
        self.password_hash = bcrypt.generate_password_hash(password).decode('utf-8')
    
    def check_password(self, password):
        """Check if provided password matches the stored hash"""
        return bcrypt.check_password_hash(self.password_hash, password)
    
    def has_permission(self, permission):
        """Check if admin has a specific permission"""
        # Super admin has all permissions
        if any(role.has_permission(PermissionType.ALL) for role in self.roles):
            return True
        
        # Check specific permission
        return any(role.has_permission(permission) for role in self.roles)
    
    def to_dict(self):
        """Convert model to dictionary"""
        return {
            'id': self.id,
            'username': self.username,
            'name': self.name,
            'email': self.email,
            'is_active': self.is_active,
            'last_login': self.last_login.isoformat() if self.last_login else None,
            'roles': [role.to_dict() for role in self.roles],
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }

# Role model
class RoleModel(db.Model):
    __tablename__ = 'roles'
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(64), unique=True, nullable=False)
    description: Mapped[str] = mapped_column(String(255), nullable=True)
    permissions: Mapped[List[str]] = mapped_column(ARRAY(String), default=[])
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now, onupdate=datetime.now)
    
    def has_permission(self, permission):
        """Check if role has specific permission"""
        return PermissionType.ALL in self.permissions or permission in self.permissions
    
    def to_dict(self):
        """Convert model to dictionary"""
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'permissions': self.permissions,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }

# SQLAlchemy Models
class PlanModel(db.Model):
    """Subscription plan model"""
    __tablename__ = 'plans'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    description = db.Column(db.String(255), nullable=True)
    price = db.Column(db.Float, nullable=False)
    duration_days = db.Column(db.Integer, nullable=False)  # Duration in days
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.now)
    updated_at = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now)
    
    # Relationship: a plan can have many subscribers - using back_populates instead of backref
    subscribers = db.relationship('SubscriberModel', back_populates='plan', lazy=True)
    
    def __repr__(self):
        return f"<Plan {self.name} - ${self.price}>"
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'price': self.price,
            'formatted_price': f"${self.price:.2f}",
            'duration_days': self.duration_days,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

class SubscriberModel(db.Model):
    __tablename__ = 'subscribers'
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey('users.id'), nullable=False)
    plan_id: Mapped[int] = mapped_column(Integer, ForeignKey('plans.id'), nullable=False)
    start_date: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    end_date: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    status: Mapped[str] = mapped_column(String(20), nullable=False)  # active, expired, cancelled
    payment_method: Mapped[str] = mapped_column(String(50), nullable=True)  # credit_card, paypal, etc.
    payment_details: Mapped[dict] = mapped_column(JSONB, nullable=True)  # masked card info, transaction IDs
    auto_renew: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now, onupdate=datetime.now)
    
    # Relationships
    user = relationship("UserModel", back_populates="subscriptions", foreign_keys=[user_id])
    plan = relationship("PlanModel", back_populates="subscribers")
    
    def is_active(self):
        """Check if subscription is currently active"""
        return self.status == "active" and self.end_date > datetime.now()
    
    def days_remaining(self):
        """Calculate days remaining in subscription"""
        if self.end_date > datetime.now():
            return (self.end_date - datetime.now()).days
        return 0
    
    def to_dict(self):
        plan_data = None
        if self.plan:
            plan_data = {
                "id": self.plan.id,
                "name": self.plan.name,
                "price": self.plan.price
            }
            
        return {
            "id": self.id,
            "user_id": self.user_id,
            "plan_id": self.plan_id,
            "plan": plan_data,
            "start_date": self.start_date.isoformat(),
            "end_date": self.end_date.isoformat(),
            "status": self.status,
            "payment_method": self.payment_method,
            "auto_renew": self.auto_renew,
            "days_remaining": self.days_remaining(),
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat()
        }

class UserModel(db.Model, UserMixin):
    __tablename__ = 'users'
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    uuid: Mapped[str] = mapped_column(String(64), unique=True, nullable=False)
    email: Mapped[str] = mapped_column(String(120), unique=True, nullable=False)
    username: Mapped[str] = mapped_column(String(64), unique=True, nullable=False)
    full_name: Mapped[str] = mapped_column(String(120), nullable=False)
    password_hash: Mapped[str] = mapped_column(String(256), nullable=False)
    profile_image: Mapped[str] = mapped_column(String(255), nullable=True)
    bio: Mapped[str] = mapped_column(Text, nullable=True)
    registration_date: Mapped[datetime] = mapped_column(DateTime, default=datetime.now)
    last_login: Mapped[datetime] = mapped_column(DateTime, nullable=True)
    status: Mapped[str] = mapped_column(String(20), default="active")  # active, inactive, suspended
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now, onupdate=datetime.now)
    role: Mapped[str] = mapped_column(String(20), default="user")  # user, premium
    email_verified: Mapped[bool] = mapped_column(Boolean, default=False)  # New field for OTP verification
    
    # User favorites
    favorite_sports: Mapped[List[str]] = mapped_column(ARRAY(String), nullable=True, default=[])
    favorite_teams: Mapped[List[int]] = mapped_column(ARRAY(Integer), nullable=True, default=[])
    favorite_players: Mapped[List[int]] = mapped_column(ARRAY(Integer), nullable=True, default=[])
    
    # Subscription relationship
    subscriptions = relationship("SubscriberModel", back_populates="user", foreign_keys="SubscriberModel.user_id")
    
    def set_password(self, password):
        """Hash the password for storage"""
        self.password_hash = bcrypt.generate_password_hash(password).decode('utf-8')
    
    def check_password(self, password):
        """Check if provided password matches the stored hash"""
        return bcrypt.check_password_hash(self.password_hash, password)
        
    def is_premium(self):
        """Check if user has premium access"""
        return self.role == "premium" or any(subscription.is_active() for subscription in self.subscriptions)
    
    def has_active_subscription(self):
        """Check if user has an active subscription"""
        return any(subscription.is_active() for subscription in self.subscriptions)
    
    def get_active_subscription(self):
        """Get the active subscription or None"""
        return next((sub for sub in self.subscriptions if sub.is_active()), None)
    
    def get_subscription_status(self):
        """Get subscription status details"""
        active_subscription = self.get_active_subscription()
        if not active_subscription:
            return {
                "status": "none",
                "plan": None,
                "end_date": None,
                "days_remaining": 0,
                "auto_renew": False
            }
        
        return {
            "status": active_subscription.status,
            "plan": {
                "name": active_subscription.plan.name if active_subscription.plan else None,
                "price": active_subscription.plan.price if active_subscription.plan else None,
                "id": active_subscription.plan_id
            },
            "end_date": active_subscription.end_date.isoformat(),
            "days_remaining": active_subscription.days_remaining(),
            "auto_renew": active_subscription.auto_renew
        }
    
    def to_dict(self):
        subscription_status = self.get_subscription_status()
        active_subscription = self.get_active_subscription()
            
        return {
            "id": self.id,
            "uuid": self.uuid,
            "email": self.email,
            "username": self.username,
            "full_name": self.full_name,
            "profile_image": self.profile_image,
            "bio": self.bio,
            "registration_date": self.registration_date.isoformat(),
            "last_login": self.last_login.isoformat() if self.last_login else None,
            "status": self.status,
            "role": self.role,
            "email_verified": self.email_verified,
            "favorite_sports": self.favorite_sports or [],
            "favorite_teams": self.favorite_teams or [],
            "favorite_players": self.favorite_players or [],
            "subscription": subscription_status,
            "has_active_subscription": bool(active_subscription),
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat()
        }

class LeagueModel(db.Model):
    __tablename__ = 'leagues'
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(120), nullable=False)
    category: Mapped[str] = mapped_column(String(50), nullable=False)  # baseball, football, basketball, etc.
    country: Mapped[str] = mapped_column(String(50), nullable=False)
    logo_url: Mapped[str] = mapped_column(String(255), nullable=False)
    popularity: Mapped[int] = mapped_column(Integer, nullable=False)
    founded_date: Mapped[datetime] = mapped_column(DateTime, nullable=True)
    headquarters: Mapped[str] = mapped_column(String(120), nullable=True)
    commissioner: Mapped[str] = mapped_column(String(120), nullable=True)
    divisions: Mapped[List[str]] = mapped_column(ARRAY(String), nullable=True)
    num_teams: Mapped[int] = mapped_column(Integer, default=0)
    enabled: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now, onupdate=datetime.now)
    
    teams = relationship("TeamModel", back_populates="league", cascade="all, delete-orphan")
    players = relationship("PlayerModel", back_populates="league", cascade="all, delete-orphan")
    
    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "category": self.category,
            "country": self.country,
            "logo_url": self.logo_url,
            "popularity": self.popularity,
            "founded_date": self.founded_date.isoformat() if self.founded_date else None,
            "headquarters": self.headquarters,
            "commissioner": self.commissioner,
            "divisions": self.divisions,
            "num_teams": self.num_teams,
            "enabled": self.enabled,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat()
        }

class TeamModel(db.Model):
    __tablename__ = 'teams'
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(120), nullable=False)
    league_id: Mapped[int] = mapped_column(Integer, ForeignKey('leagues.id'), nullable=False)
    logo_url: Mapped[str] = mapped_column(String(255), nullable=False)
    popularity: Mapped[int] = mapped_column(Integer, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now, onupdate=datetime.now)
    
    league = relationship("LeagueModel", back_populates="teams")
    players = relationship("PlayerModel", back_populates="team", cascade="all, delete-orphan")
    
    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "league_id": self.league_id,
            "logo_url": self.logo_url,
            "popularity": self.popularity,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat()
        }

class PlayerModel(db.Model):
    __tablename__ = 'players'
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(120), nullable=False)
    team_id: Mapped[int] = mapped_column(Integer, ForeignKey('teams.id'), nullable=False)
    league_id: Mapped[int] = mapped_column(Integer, ForeignKey('leagues.id'), nullable=False)
    position: Mapped[str] = mapped_column(String(50), nullable=False)
    jersey_number: Mapped[str] = mapped_column(String(10), nullable=False)
    profile_image: Mapped[str] = mapped_column(String(255), nullable=False)
    dob: Mapped[datetime] = mapped_column(DateTime, nullable=True)
    college: Mapped[str] = mapped_column(String(120), nullable=True)
    height_weight: Mapped[str] = mapped_column(String(50), nullable=True)
    bat_throw: Mapped[str] = mapped_column(String(20), nullable=True)
    experience: Mapped[str] = mapped_column(String(50), nullable=True)
    birthplace: Mapped[str] = mapped_column(String(120), nullable=True)
    status: Mapped[str] = mapped_column(String(20), default="Active")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now, onupdate=datetime.now)
    
    team = relationship("TeamModel", back_populates="players")
    league = relationship("LeagueModel", back_populates="players")
    reels = relationship("ReelModel", back_populates="player", cascade="all, delete-orphan")
    
    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "team_id": self.team_id,
            "league_id": self.league_id,
            "position": self.position,
            "jersey_number": self.jersey_number,
            "profile_image": self.profile_image,
            "dob": self.dob.isoformat() if self.dob else None,
            "college": self.college,
            "height_weight": self.height_weight,
            "bat_throw": self.bat_throw,
            "experience": self.experience,
            "birthplace": self.birthplace,
            "status": self.status,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat()
        }

class ReelModel(db.Model):
    __tablename__ = 'reels'
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    player_id: Mapped[int] = mapped_column(Integer, ForeignKey('players.id'), nullable=False)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    thumbnail_url: Mapped[str] = mapped_column(String(255), nullable=False)
    video_url: Mapped[str] = mapped_column(String(255), nullable=False)
    duration: Mapped[float] = mapped_column(Float, nullable=False)
    view_count: Mapped[int] = mapped_column(Integer, default=0)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now, onupdate=datetime.now)
    
    player = relationship("PlayerModel", back_populates="reels")
    
    def to_dict(self):
        return {
            "id": self.id,
            "player_id": self.player_id,
            "title": self.title,
            "thumbnail_url": self.thumbnail_url,
            "video_url": self.video_url,
            "duration": self.duration,
            "view_count": self.view_count,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat()
        }

class UserActivityModel(db.Model):
    __tablename__ = 'user_activity'
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    date: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    active_users: Mapped[int] = mapped_column(Integer, nullable=False)
    new_users: Mapped[int] = mapped_column(Integer, nullable=False)
    
    def to_dict(self):
        return {
            "id": self.id,
            "date": self.date.isoformat(),
            "active_users": self.active_users,
            "new_users": self.new_users
        }

class SubscriberStatsModel(db.Model):
    __tablename__ = 'subscriber_stats'
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    date: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    monthly: Mapped[int] = mapped_column(Integer, nullable=False)
    yearly: Mapped[int] = mapped_column(Integer, nullable=False)
    
    def to_dict(self):
        return {
            "id": self.id,
            "date": self.date.isoformat(),
            "monthly": self.monthly,
            "yearly": self.yearly
        }

class NotificationModel(db.Model):
    __tablename__ = 'notifications'
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    message: Mapped[str] = mapped_column(Text, nullable=False)
    destination_url: Mapped[str] = mapped_column(String(255), nullable=False)
    image_url: Mapped[str] = mapped_column(String(255), nullable=True)
    icon_url: Mapped[str] = mapped_column(String(255), nullable=True)
    target_type: Mapped[str] = mapped_column(String(20), default="all")  # "all" or "user"
    target_user_id: Mapped[int] = mapped_column(Integer, nullable=True)  # Only used if target_type is "user"
    sent: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now, onupdate=datetime.now)
    
    def to_dict(self):
        return {
            "id": self.id,
            "title": self.title,
            "message": self.message,
            "destination_url": self.destination_url,
            "image_url": self.image_url,
            "icon_url": self.icon_url,
            "target_type": self.target_type,
            "target_user_id": self.target_user_id,
            "sent": self.sent,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat()
        }

# New model for sports odds data
class OddsModel(db.Model):
    __tablename__ = 'odds'
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    sport_key: Mapped[str] = mapped_column(String(64), nullable=False)
    sport_title: Mapped[str] = mapped_column(String(128), nullable=False)
    event_id: Mapped[str] = mapped_column(String(128), nullable=False)
    event_time: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    home_team: Mapped[str] = mapped_column(String(128), nullable=False)
    away_team: Mapped[str] = mapped_column(String(128), nullable=False)
    bookmakers: Mapped[dict] = mapped_column(JSONB, nullable=False)
    last_update: Mapped[datetime] = mapped_column(DateTime, default=datetime.now, onupdate=datetime.now)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now, onupdate=datetime.now)
    
    def to_dict(self):
        return {
            "id": self.id,
            "sport_key": self.sport_key,
            "sport_title": self.sport_title,
            "event_id": self.event_id,
            "event_time": self.event_time.isoformat(),
            "home_team": self.home_team,
            "away_team": self.away_team,
            "bookmakers": self.bookmakers,
            "last_update": self.last_update.isoformat(),
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat()
        }

# Record structures
class Plan:
    @staticmethod
    def create_record(id: int, name: str, price: float, duration_days: int, description: str = "", is_active: bool = True) -> Dict[str, Any]:
        return {
            "id": id,
            "name": name,
            "description": description,
            "price": price,
            "duration_days": duration_days,
            "is_active": is_active,
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat()
        }

class Subscriber:
    @staticmethod
    def create_record(id: int, user_id: int, plan_id: int, 
                      start_date: datetime, end_date: datetime, 
                      status: str, payment_method: str = "", 
                      auto_renew: bool = True) -> Dict[str, Any]:
        return {
            "id": id,
            "user_id": user_id,
            "plan_id": plan_id,
            "start_date": start_date.isoformat(),
            "end_date": end_date.isoformat(),
            "status": status,  # active, expired, cancelled
            "payment_method": payment_method,
            "auto_renew": auto_renew,
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat()
        }

class User:
    @staticmethod
    def create_record(id: int, email: str, username: str, 
                      registration_date: datetime, last_login: datetime, 
                      status: str, profile_image: str = "", 
                      full_name: str = "", uuid: str = "",
                      bio: str = "", favorite_sports: List[str] = None,
                      favorite_teams: List[int] = None,
                      favorite_players: List[int] = None) -> Dict[str, Any]:
        return {
            "id": id,
            "uuid": uuid or f"user-{id}-uuid",  # In a real system, this would be a proper UUID
            "email": email,
            "username": username,
            "full_name": full_name or username,  # Use full name if provided, otherwise username
            "profile_image": profile_image or f"https://ui-avatars.com/api/?name={username}&background=random",
            "bio": bio or "Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua.",
            "registration_date": registration_date.isoformat(),
            "last_login": last_login.isoformat(),
            "status": status,  # active, inactive, suspended
            "favorite_sports": favorite_sports or [],
            "favorite_teams": favorite_teams or [],
            "favorite_players": favorite_players or [],
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat()
        }

class League:
    @staticmethod
    def create_record(id: int, name: str, category: str, 
                      country: str, logo_url: str, popularity: int,
                      founded_date: datetime = datetime(1900, 1, 1), 
                      headquarters: str = "", commissioner: str = "",
                      divisions: List[str] = [], num_teams: int = 0, 
                      enabled: bool = True) -> Dict[str, Any]:
        return {
            "id": id,
            "name": name,
            "category": category,  # baseball, football, basketball, etc.
            "country": country,
            "logo_url": logo_url,
            "popularity": popularity,  # view count or rating
            "founded_date": founded_date.isoformat() if founded_date else datetime(1900, 1, 1).isoformat(),
            "headquarters": headquarters or "",
            "commissioner": commissioner or "",
            "divisions": divisions or [],
            "num_teams": num_teams,
            "enabled": enabled,
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat()
        }

class Team:
    @staticmethod
    def create_record(id: int, name: str, league_id: int, 
                      logo_url: str, popularity: int) -> Dict[str, Any]:
        return {
            "id": id,
            "name": name,
            "league_id": league_id,
            "logo_url": logo_url,
            "popularity": popularity,  # view count or rating
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat()
        }

class UserActivity:
    @staticmethod
    def create_record(date: datetime, active_users: int, new_users: int) -> Dict[str, Any]:
        return {
            "date": date.isoformat(),
            "active_users": active_users,
            "new_users": new_users
        }

class SubscriberStats:
    @staticmethod
    def create_record(date: datetime, monthly: int, yearly: int) -> Dict[str, Any]:
        return {
            "date": date.isoformat(),
            "monthly": monthly,
            "yearly": yearly
        }

class Player:
    @staticmethod
    def create_record(id: int, name: str, team_id: int, league_id: int, 
                      position: str, jersey_number: str, profile_image: str,
                      dob: Optional[datetime] = None, college: str = "", 
                      height_weight: str = "", bat_throw: str = "",
                      experience: str = "", birthplace: str = "", 
                      status: str = "Active") -> Dict[str, Any]:
        return {
            "id": id,
            "name": name,
            "team_id": team_id,
            "league_id": league_id,
            "position": position,
            "jersey_number": jersey_number,
            "profile_image": profile_image,
            "dob": dob.isoformat() if dob else "",
            "college": college,
            "height_weight": height_weight,
            "bat_throw": bat_throw,
            "experience": experience,
            "birthplace": birthplace,
            "status": status,
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat()
        }

class Reel:
    @staticmethod
    def create_record(id: int, player_id: int, title: str, 
                      thumbnail_url: str, video_url: str, 
                      duration: float, view_count: int = 0,
                      created_at: Optional[datetime] = None) -> Dict[str, Any]:
        now = datetime.now()
        return {
            "id": id,
            "player_id": player_id,
            "title": title,
            "thumbnail_url": thumbnail_url,
            "video_url": video_url,
            "duration": duration,  # in seconds
            "view_count": view_count,
            "created_at": created_at.isoformat() if created_at else now.isoformat(),
            "updated_at": now.isoformat()
        }

class Notification:
    @staticmethod
    def create_record(id: int, title: str, message: str, 
                      destination_url: str, image_url: str = "", 
                      icon_url: str = "", target_type: str = "all", 
                      target_user_id: Optional[int] = None,
                      created_at: Optional[datetime] = None,
                      sent: bool = False) -> Dict[str, Any]:
        now = datetime.now()
        return {
            "id": id,
            "title": title,
            "message": message,
            "destination_url": destination_url,
            "image_url": image_url,
            "icon_url": icon_url,
            "target_type": target_type,  # "all" or "user"
            "target_user_id": target_user_id,  # Only used if target_type is "user"
            "sent": sent,  # Whether the notification has been sent
            "created_at": created_at.isoformat() if created_at else now.isoformat(),
            "updated_at": now.isoformat()
        }

# Odds data helper class
class Odds:
    @staticmethod
    def create_record(id: int, sport_key: str, sport_title: str, event_id: str, 
                      event_time: datetime, home_team: str, away_team: str, 
                      bookmakers: dict) -> Dict[str, Any]:
        now = datetime.now()
        return {
            "id": id,
            "sport_key": sport_key,
            "sport_title": sport_title,
            "event_id": event_id,
            "event_time": event_time.isoformat(),
            "home_team": home_team,
            "away_team": away_team,
            "bookmakers": bookmakers,
            "last_update": now.isoformat(),
            "created_at": now.isoformat(),
            "updated_at": now.isoformat()
        }

# Content Management Models
class FAQModel(db.Model):
    __tablename__ = 'faqs'
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    question: Mapped[str] = mapped_column(Text, nullable=False)
    answer: Mapped[str] = mapped_column(Text, nullable=False)
    order: Mapped[int] = mapped_column(Integer, default=0)  # For controlling display order
    is_published: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now, onupdate=datetime.now)
    
    def to_dict(self):
        return {
            "id": self.id,
            "question": self.question,
            "answer": self.answer,
            "order": self.order,
            "is_published": self.is_published,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat()
        }

class ContentPageModel(db.Model):
    __tablename__ = 'content_pages'
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    page_type: Mapped[str] = mapped_column(String(50), nullable=False)  # privacy_policy, terms_conditions
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    is_published: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now, onupdate=datetime.now)
    
    def to_dict(self):
        return {
            "id": self.id,
            "page_type": self.page_type,
            "title": self.title,
            "content": self.content,
            "is_published": self.is_published,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat()
        }

# In-memory data for content management
faqs_data: List[Dict[str, Any]] = []
content_pages_data: List[Dict[str, Any]] = []

class FAQ:
    @staticmethod
    def create_record(id: int, question: str, answer: str, order: int = 0, 
                     is_published: bool = True) -> Dict[str, Any]:
        return {
            "id": id,
            "question": question,
            "answer": answer,
            "order": order,
            "is_published": is_published,
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat()
        }

class ContentPage:
    @staticmethod
    def create_record(id: int, page_type: str, title: str, content: str,
                     is_published: bool = True) -> Dict[str, Any]:
        return {
            "id": id,
            "page_type": page_type,  # privacy_policy, terms_conditions
            "title": title,
            "content": content,
            "is_published": is_published,
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat()
        }
