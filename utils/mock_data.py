import random
import logging
from datetime import datetime, timedelta
from models import (
    subscribers_data, users_data, leagues_data, teams_data, user_activity_data,
    Subscriber, User, League, Team, UserActivity, SubscriberStats
)

# Configure logger
logger = logging.getLogger(__name__)

def initialize_mock_data():
    """Generate mock data for all models"""
    logger.info("Initializing mock data...")
    
    # Clear existing data
    subscribers_data.clear()
    users_data.clear()
    leagues_data.clear()
    teams_data.clear()
    user_activity_data.clear()
    
    # Generate leagues
    generate_leagues()
    
    # Generate teams
    generate_teams()
    
    # Generate users
    generate_users()
    
    # Generate subscribers
    generate_subscribers()
    
    # Generate user activity
    generate_user_activity()
    
    logger.info("Mock data initialization complete.")

def generate_leagues():
    """Generate mock league data"""
    leagues = [
        {
            "id": 1,
            "name": "Major League Baseball",
            "category": "Baseball",
            "country": "USA",
            "logo_url": "https://www.mlbstatic.com/mlb-logos/league-on-dark/logo-primary-on-dark.svg",
            "popularity": 5000,
            "founded_date": datetime(1876, 2, 2),
            "headquarters": "New York City, USA",
            "commissioner": "Rob Manfred (as of 2025)",
            "divisions": ["American League", "National League"],
            "num_teams": 12,
            "enabled": True
        },
        {
            "id": 2,
            "name": "National Basketball Association",
            "category": "Basketball",
            "country": "USA",
            "logo_url": "https://cdn.nba.com/logos/leagues/logo-nba.svg",
            "popularity": 4800,
            "founded_date": datetime(1949, 8, 3),
            "headquarters": "New York City, USA",
            "commissioner": "Adam Silver (as of 2025)",
            "divisions": ["Eastern Conference", "Western Conference"],
            "num_teams": 12,
            "enabled": True
        },
        {
            "id": 3,
            "name": "National Football League",
            "category": "Football",
            "country": "USA",
            "logo_url": "https://static.www.nfl.com/image/upload/v1554321393/league/nvfr7ogywskqrfaiu38m.svg",
            "popularity": 4500,
            "founded_date": datetime(1920, 8, 20),
            "headquarters": "345 Park Avenue, New York City, NY, USA",
            "commissioner": "Roger Goodell (as of 2025)",
            "divisions": ["NORTH", "SOUTH", "EAST", "WEST"],
            "num_teams": 12,
            "enabled": True
        },
        {
            "id": 4,
            "name": "UEFA Champions League",
            "category": "Soccer",
            "country": "Europe",
            "logo_url": "https://upload.wikimedia.org/wikipedia/en/thumb/9/9a/UEFA_Champions_League_logo.svg/120px-UEFA_Champions_League_logo.svg.png",
            "popularity": 4200,
            "founded_date": datetime(1955, 1, 1),
            "headquarters": "Nyon, Switzerland",
            "commissioner": "Aleksander Čeferin",
            "divisions": ["Europe"],
            "num_teams": 12,
            "enabled": True
        },
        {
            "id": 5,
            "name": "2025 Australian Open",
            "category": "Tennis",
            "country": "Australia",
            "logo_url": "https://en.wikipedia.org/wiki/File:Australian_Open_logo.svg",
            "popularity": 3900,
            "founded_date": datetime(2025, 1, 6),
            "headquarters": "Melbourne, Victoria, Australia",
            "commissioner": "Grand Slam",
            "divisions": ["Melbourne Park"],
            "num_teams": 12,
            "enabled": True
        }
    ]
    
    for league_data in leagues:
        league = League.create_record(
            id=league_data["id"],
            name=league_data["name"],
            category=league_data["category"],
            country=league_data["country"],
            logo_url=league_data["logo_url"],
            popularity=league_data["popularity"],
            founded_date=league_data["founded_date"],
            headquarters=league_data["headquarters"],
            commissioner=league_data["commissioner"],
            divisions=league_data["divisions"],
            num_teams=league_data["num_teams"],
            enabled=league_data["enabled"]
        )
        leagues_data.append(league)
    
    logger.info(f"Generated {len(leagues_data)} leagues")

def generate_teams():
    """Generate mock team data"""
    teams = [
        {
            "id": 1,
            "name": "Baltimore Orioles",
            "league_id": 2,
            "logo_url": "https://www.mlbstatic.com/team-logos/110.svg",
            "popularity": 4800
        },
        {
            "id": 2,
            "name": "New York Yankees",
            "league_id": 2,
            "logo_url": "https://www.mlbstatic.com/team-logos/147.svg",
            "popularity": 4700
        },
        {
            "id": 3,
            "name": "Los Angeles Lakers",
            "league_id": 3,
            "logo_url": "https://cdn.nba.com/logos/nba/1610612747/primary/L/logo.svg",
            "popularity": 4500
        },
        {
            "id": 4,
            "name": "Kansas City Chiefs",
            "league_id": 4,
            "logo_url": "https://static.www.nfl.com/image/private/f_auto/league/ujshjqvdb3jlpqym8pky",
            "popularity": 4300
        },
        {
            "id": 5,
            "name": "Manchester United",
            "league_id": 5,
            "logo_url": "https://resources.premierleague.com/premierleague/badges/t1.svg",
            "popularity": 4000
        }
    ]
    
    for team_data in teams:
        team = Team.create_record(
            id=team_data["id"],
            name=team_data["name"],
            league_id=team_data["league_id"],
            logo_url=team_data["logo_url"],
            popularity=team_data["popularity"]
        )
        teams_data.append(team)
    
    logger.info(f"Generated {len(teams_data)} teams")

def generate_users():
    """Generate mock user data"""
    # List of realistic names for our sample users
    first_names = ["Theresa", "Savannah", "Darlene", "Jackson", "Michelle", "Kenzi", "Robert", "James", "Emma", "Olivia"]
    last_names = ["Webb", "Nguyen", "Robertson", "Graham", "Rivera", "Lawson", "Smith", "Johnson", "Williams", "Brown"]
    
    # Generate ~40 named users first with more detailed data
    named_users = []
    for i in range(1, 41):
        status = random.choice(["active", "inactive", "suspended"])
        registration_date = datetime.now() - timedelta(days=random.randint(1, 500))
        last_login = registration_date + timedelta(days=random.randint(0, (datetime.now() - registration_date).days))
        
        first_name = random.choice(first_names)
        last_name = random.choice(last_names)
        full_name = f"{first_name} {last_name}"
        user_name = first_name.lower() + last_name.lower()
        email = f"{first_name.lower()}.{last_name.lower()}@example.com"
        
        user = User.create_record(
            id=i,
            email=email,
            username=user_name,
            full_name=full_name,
            registration_date=registration_date,
            last_login=last_login,
            status=status,
            uuid=f"user-{i}-{user_name}-uuid"
        )
        named_users.append(user)
    
    # Then generate the rest up to 2500 total
    for i in range(41, 2501):
        status = random.choice(["active", "inactive", "suspended"])
        registration_date = datetime.now() - timedelta(days=random.randint(1, 500))
        last_login = registration_date + timedelta(days=random.randint(0, (datetime.now() - registration_date).days))
        
        user = User.create_record(
            id=i,
            email=f"user{i}@example.com",
            username=f"user{i}",
            registration_date=registration_date,
            last_login=last_login,
            status=status
        )
        named_users.append(user)
    
    # Update the global users_data list
    users_data.extend(named_users)
    
    logger.info(f"Generated {len(users_data)} users")

def generate_subscribers():
    """Generate mock subscriber data"""
    # Generate ~10000 subscribers
    for i in range(1, 10001):
        subscription_type = random.choice(["monthly", "yearly"])
        status = random.choice(["active", "expired", "cancelled"])
        start_date = datetime.now() - timedelta(days=random.randint(1, 500))
        
        # End date logic depends on subscription type and status
        if subscription_type == "monthly":
            if status == "active":
                end_date = start_date + timedelta(days=30 + random.randint(0, 30))
            else:
                end_date = start_date + timedelta(days=random.randint(1, 30))
        else:  # yearly
            if status == "active":
                end_date = start_date + timedelta(days=365 + random.randint(0, 30))
            else:
                end_date = start_date + timedelta(days=random.randint(1, 365))
        
        subscriber = Subscriber.create_record(
            id=i,
            email=f"subscriber{i}@example.com",
            name=f"Subscriber {i}",
            subscription_type=subscription_type,
            start_date=start_date,
            end_date=end_date,
            status=status
        )
        subscribers_data.append(subscriber)
    
    logger.info(f"Generated {len(subscribers_data)} subscribers")

def generate_user_activity():
    """Generate mock user activity data for charting"""
    # Generate data for the last 31 days (January 2024)
    today = datetime(2024, 1, 31)
    
    for i in range(31):
        date = today - timedelta(days=i)
        
        # Generate realistic-looking data with some randomness
        if i < 7:  # Last week - higher values
            active_users = random.randint(1800, 2500)
            new_users = random.randint(150, 300)
        elif i < 14:  # Week before - slightly lower
            active_users = random.randint(1600, 2300)
            new_users = random.randint(120, 250)
        else:  # Earlier weeks - lower values
            active_users = random.randint(1400, 2100)
            new_users = random.randint(100, 200)
        
        # Add some day-of-week patterns
        day_of_week = date.weekday()
        if day_of_week == 5 or day_of_week == 6:  # Weekend
            active_users = int(active_users * 1.2)  # 20% more activity on weekends
        
        activity = UserActivity.create_record(
            date=date,
            active_users=active_users,
            new_users=new_users
        )
        user_activity_data.append(activity)
    
    # Sort by date (ascending)
    user_activity_data.sort(key=lambda x: x['date'])
    
    logger.info(f"Generated {len(user_activity_data)} days of user activity data")
