import pytest
import os
import json
from datetime import datetime, timedelta
from flask_jwt_extended import create_access_token
from app import app, db
from models import (
    AdminModel, RoleModel, UserModel, SubscriberModel, LeagueModel, 
    TeamModel, PlayerModel, ReelModel, NotificationModel, PermissionType
)

@pytest.fixture
def client():
    """Create a test client for the app with app_context."""
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    app.config['JWT_SECRET_KEY'] = 'test-key'
    
    with app.test_client() as client:
        with app.app_context():
            db.create_all()
            yield client
            db.session.remove()
            db.drop_all()

@pytest.fixture
def setup_roles():
    """Set up test roles with different permissions."""
    # Create Admin role with all permissions
    admin_role = RoleModel(name='Admin', description='Administrator', permissions=[PermissionType.ALL])
    
    # Content Manager role
    content_role = RoleModel(name='Content Manager', description='Manages content', 
                           permissions=[PermissionType.CONTENT, PermissionType.REELS])
    
    # User Manager role
    user_role = RoleModel(name='User Manager', description='Manages users', 
                        permissions=[PermissionType.USERS, PermissionType.SUBSCRIBERS])
    
    # League Manager role
    league_role = RoleModel(name='League Manager', description='Manages leagues', 
                          permissions=[PermissionType.LEAGUES])
    
    db.session.add_all([admin_role, content_role, user_role, league_role])
    db.session.commit()
    
    return {
        'admin_role': admin_role,
        'content_role': content_role, 
        'user_role': user_role,
        'league_role': league_role
    }

@pytest.fixture
def setup_admins(setup_roles):
    """Set up test admin users with different roles."""
    # Super admin with all permissions
    super_admin = AdminModel(
        username='superadmin',
        name='Super Admin',
        email='super@gambitadmin.com',
        is_active=True
    )
    super_admin.set_password('superadmin123')
    super_admin.roles.append(setup_roles['admin_role'])
    
    # Content manager
    content_admin = AdminModel(
        username='contentadmin',
        name='Content Admin',
        email='content@gambitadmin.com',
        is_active=True
    )
    content_admin.set_password('content123')
    content_admin.roles.append(setup_roles['content_role'])
    
    # User manager
    user_admin = AdminModel(
        username='useradmin',
        name='User Admin',
        email='user@gambitadmin.com',
        is_active=True
    )
    user_admin.set_password('user123')
    user_admin.roles.append(setup_roles['user_role'])
    
    # League manager
    league_admin = AdminModel(
        username='leagueadmin',
        name='League Admin',
        email='league@gambitadmin.com',
        is_active=True
    )
    league_admin.set_password('league123')
    league_admin.roles.append(setup_roles['league_role'])
    
    # Inactive admin
    inactive_admin = AdminModel(
        username='inactiveadmin',
        name='Inactive Admin',
        email='inactive@gambitadmin.com',
        is_active=False
    )
    inactive_admin.set_password('inactive123')
    inactive_admin.roles.append(setup_roles['admin_role'])
    
    db.session.add_all([super_admin, content_admin, user_admin, league_admin, inactive_admin])
    db.session.commit()
    
    return {
        'super_admin': super_admin,
        'content_admin': content_admin,
        'user_admin': user_admin,
        'league_admin': league_admin,
        'inactive_admin': inactive_admin
    }

@pytest.fixture
def auth_tokens(setup_admins):
    """Create JWT tokens for each admin type."""
    tokens = {}
    for admin_type, admin in setup_admins.items():
        tokens[admin_type] = create_access_token(identity=admin.id)
    return tokens

@pytest.fixture
def setup_users():
    """Set up test users."""
    users = []
    for i in range(1, 6):
        user = UserModel(
            uuid=f"user-{i}-uuid",
            email=f"user{i}@example.com",
            username=f"user{i}",
            full_name=f"Test User {i}",
            profile_image=f"https://ui-avatars.com/api/?name=User{i}",
            bio=f"Bio for test user {i}",
            registration_date=datetime.now() - timedelta(days=i*10),
            last_login=datetime.now() - timedelta(days=i),
            status='active' if i % 3 != 0 else 'inactive' if i % 3 == 0 else 'suspended',
            favorite_sports=[f"sport{j}" for j in range(1, i+1)],
            favorite_teams=[j for j in range(1, i+1)],
            favorite_players=[j for j in range(1, i+1)]
        )
        users.append(user)
    
    db.session.add_all(users)
    db.session.commit()
    
    return users

@pytest.fixture
def setup_subscribers():
    """Set up test subscribers."""
    subscribers = []
    for i in range(1, 6):
        subscriber = SubscriberModel(
            email=f"subscriber{i}@example.com",
            name=f"Subscriber {i}",
            subscription_type="monthly" if i % 2 == 0 else "yearly",
            start_date=datetime.now() - timedelta(days=30),
            end_date=datetime.now() + timedelta(days=30 if i % 2 == 0 else 365),
            status="active" if i < 4 else "expired" if i == 4 else "cancelled"
        )
        subscribers.append(subscriber)
    
    db.session.add_all(subscribers)
    db.session.commit()
    
    return subscribers

@pytest.fixture
def setup_leagues():
    """Set up test leagues."""
    leagues = []
    categories = ["football", "basketball", "baseball", "hockey", "soccer"]
    countries = ["USA", "Canada", "UK", "Spain", "Germany"]
    
    for i in range(1, 6):
        league = LeagueModel(
            name=f"League {i}",
            category=categories[i-1],
            country=countries[i-1],
            logo_url=f"https://example.com/logos/league{i}.png",
            popularity=100 - i*10,
            founded_date=datetime(1900 + i*20, 1, 1),
            headquarters=f"City {i}",
            commissioner=f"Commissioner {i}",
            divisions=[f"Division {j}" for j in range(1, 4)],
            num_teams=10 + i,
            enabled=True if i < 5 else False
        )
        leagues.append(league)
    
    db.session.add_all(leagues)
    db.session.commit()
    
    return leagues

@pytest.fixture
def setup_teams(setup_leagues):
    """Set up test teams."""
    teams = []
    for league_idx, league in enumerate(setup_leagues):
        for i in range(1, 4):  # 3 teams per league
            team = TeamModel(
                name=f"Team {league_idx+1}-{i}",
                league_id=league.id,
                logo_url=f"https://example.com/logos/team{league_idx+1}-{i}.png",
                popularity=90 - (league_idx*10) - i
            )
            teams.append(team)
    
    db.session.add_all(teams)
    db.session.commit()
    
    return teams

@pytest.fixture
def setup_players(setup_teams, setup_leagues):
    """Set up test players."""
    players = []
    positions = ["Forward", "Guard", "Center", "Pitcher", "Catcher"]
    
    for team_idx, team in enumerate(setup_teams):
        for i in range(1, 3):  # 2 players per team
            player = PlayerModel(
                name=f"Player {team_idx+1}-{i}",
                team_id=team.id,
                league_id=team.league_id,
                position=positions[team_idx % len(positions)],
                jersey_number=str(i),
                profile_image=f"https://example.com/players/player{team_idx+1}-{i}.png",
                dob=datetime(1990 - team_idx, 1, i),
                college=f"University {team_idx+1}",
                height_weight=f"{180+i} cm, {80+i} kg",
                bat_throw=f"{'Right' if i % 2 == 0 else 'Left'}",
                experience=f"{team_idx+i} years",
                birthplace=f"City {team_idx+i}",
                status="Active"
            )
            players.append(player)
    
    db.session.add_all(players)
    db.session.commit()
    
    return players

@pytest.fixture
def setup_reels(setup_players):
    """Set up test reels."""
    reels = []
    for player_idx, player in enumerate(setup_players):
        for i in range(1, 3):  # 2 reels per player
            reel = ReelModel(
                player_id=player.id,
                title=f"Amazing Play by {player.name} - {i}",
                thumbnail_url=f"https://example.com/thumbnails/reel{player_idx+1}-{i}.jpg",
                video_url=f"https://example.com/videos/reel{player_idx+1}-{i}.mp4",
                duration=30.0 + (player_idx * 5),
                view_count=1000 - (player_idx * 100 + i * 10)
            )
            reels.append(reel)
    
    db.session.add_all(reels)
    db.session.commit()
    
    return reels

@pytest.fixture
def setup_notifications(setup_users):
    """Set up test notifications."""
    notifications = []
    
    # General notifications for all users
    for i in range(1, 4):
        notification = NotificationModel(
            title=f"General Notification {i}",
            message=f"This is a general notification {i} for all users",
            destination_url=f"https://example.com/notifications/{i}",
            image_url=f"https://example.com/images/notification{i}.jpg",
            icon_url=f"https://example.com/icons/notification{i}.jpg",
            target_type="all",
            sent=i < 3  # First 2 are sent
        )
        notifications.append(notification)
    
    # User-specific notifications
    for i, user in enumerate(setup_users[:2]):  # Only for first 2 users
        notification = NotificationModel(
            title=f"User Notification for {user.username}",
            message=f"This is a personal notification for {user.username}",
            destination_url=f"https://example.com/users/{user.id}/notifications",
            image_url=f"https://example.com/images/user-notification{i}.jpg",
            icon_url=f"https://example.com/icons/user-notification{i}.jpg",
            target_type="user",
            target_user_id=user.id,
            sent=i == 0  # Only first one is sent
        )
        notifications.append(notification)
    
    db.session.add_all(notifications)
    db.session.commit()
    
    return notifications

def auth_header(token):
    """Helper function to create authorization header with JWT token."""
    return {'Authorization': f'Bearer {token}'}

def assert_successful_response(response, message=None):
    """Helper function to assert that a response is successful."""
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data['success'] is True
    if message:
        assert message in data.get('message', '')
    return data

def assert_error_response(response, status_code, message=None):
    """Helper function to assert that a response is an error."""
    assert response.status_code == status_code
    data = json.loads(response.data)
    assert data['success'] is False
    if message:
        assert message in data.get('error', '') or message in data.get('message', '')
    return data