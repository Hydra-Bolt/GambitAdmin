"""
Database seeding utilities for the Gambit Admin API
"""

import logging
from datetime import datetime, timedelta
from app import db
from models import (
    NotificationModel, subscribers_data, users_data, leagues_data, 
    teams_data, players_data, reels_data, user_activity_data, 
    notifications_data, SubscriberModel, UserModel, LeagueModel, 
    TeamModel, PlayerModel, ReelModel, UserActivityModel, 
    SubscriberStatsModel
)

# Configure logger
logger = logging.getLogger(__name__)

def seed_database():
    """Seed the database with mock data from the in-memory data structures"""
    try:
        seed_leagues()
        seed_teams()
        seed_players()
        seed_reels()
        seed_users()
        seed_subscribers()
        seed_user_activity()
        seed_notifications()
        logger.info("Database seeded successfully")
    except Exception as e:
        logger.error(f"Error seeding database: {str(e)}")
        db.session.rollback()

def seed_notifications():
    """Seed notification data into the database"""
    # Check if we have notifications in the database already
    if db.session.query(NotificationModel).count() > 0:
        logger.info("Notifications table already has data, skipping seeding")
        return
    
    logger.info("Seeding notifications table...")
    
    # Convert in-memory notifications to database models
    for notification_data in notifications_data:
        try:
            # Parse ISO format dates
            created_at = datetime.fromisoformat(notification_data["created_at"])
            updated_at = datetime.fromisoformat(notification_data["updated_at"])
            
            notification = NotificationModel(
                id=notification_data["id"],
                title=notification_data["title"],
                message=notification_data["message"],
                destination_url=notification_data["destination_url"],
                image_url=notification_data.get("image_url", ""),
                icon_url=notification_data.get("icon_url", ""),
                target_type=notification_data.get("target_type", "all"),
                target_user_id=notification_data.get("target_user_id"),
                sent=notification_data.get("sent", False),
                created_at=created_at,
                updated_at=updated_at
            )
            db.session.add(notification)
        except Exception as e:
            logger.error(f"Error adding notification {notification_data['id']}: {str(e)}")
    
    db.session.commit()
    logger.info(f"Seeded {len(notifications_data)} notifications")

def seed_leagues():
    """Seed league data into the database"""
    # Check if we have leagues in the database already
    if db.session.query(LeagueModel).count() > 0:
        logger.info("Leagues table already has data, skipping seeding")
        return
    
    logger.info("Seeding leagues table...")
    
    # Convert in-memory leagues to database models
    for league_data in leagues_data:
        try:
            # Parse ISO format dates
            created_at = datetime.fromisoformat(league_data["created_at"])
            updated_at = datetime.fromisoformat(league_data["updated_at"])
            founded_date = datetime.fromisoformat(league_data["founded_date"]) if league_data.get("founded_date") else None
            
            league = LeagueModel(
                id=league_data["id"],
                name=league_data["name"],
                category=league_data["category"],
                country=league_data["country"],
                logo_url=league_data["logo_url"],
                popularity=league_data["popularity"],
                founded_date=founded_date,
                headquarters=league_data.get("headquarters", ""),
                commissioner=league_data.get("commissioner", ""),
                divisions=league_data.get("divisions", []),
                num_teams=league_data.get("num_teams", 0),
                enabled=league_data.get("enabled", True),
                created_at=created_at,
                updated_at=updated_at
            )
            db.session.add(league)
        except Exception as e:
            logger.error(f"Error adding league {league_data['id']}: {str(e)}")
    
    db.session.commit()
    logger.info(f"Seeded {len(leagues_data)} leagues")

def seed_teams():
    """Seed team data into the database"""
    # Check if we have teams in the database already
    if db.session.query(TeamModel).count() > 0:
        logger.info("Teams table already has data, skipping seeding")
        return
    
    logger.info("Seeding teams table...")
    
    # Convert in-memory teams to database models
    for team_data in teams_data:
        try:
            # Parse ISO format dates
            created_at = datetime.fromisoformat(team_data["created_at"])
            updated_at = datetime.fromisoformat(team_data["updated_at"])
            
            team = TeamModel(
                id=team_data["id"],
                name=team_data["name"],
                league_id=team_data["league_id"],
                logo_url=team_data["logo_url"],
                popularity=team_data["popularity"],
                created_at=created_at,
                updated_at=updated_at
            )
            db.session.add(team)
        except Exception as e:
            logger.error(f"Error adding team {team_data['id']}: {str(e)}")
    
    db.session.commit()
    logger.info(f"Seeded {len(teams_data)} teams")

def seed_players():
    """Seed player data into the database"""
    # Check if we have players in the database already
    if db.session.query(PlayerModel).count() > 0:
        logger.info("Players table already has data, skipping seeding")
        return
    
    logger.info("Seeding players table...")
    
    # Convert in-memory players to database models
    for player_data in players_data:
        try:
            # Parse ISO format dates
            created_at = datetime.fromisoformat(player_data["created_at"])
            updated_at = datetime.fromisoformat(player_data["updated_at"])
            dob = datetime.fromisoformat(player_data["dob"]) if player_data.get("dob") else None
            
            player = PlayerModel(
                id=player_data["id"],
                name=player_data["name"],
                team_id=player_data["team_id"],
                league_id=player_data["league_id"],
                position=player_data["position"],
                jersey_number=player_data["jersey_number"],
                profile_image=player_data["profile_image"],
                dob=dob,
                college=player_data.get("college", ""),
                height_weight=player_data.get("height_weight", ""),
                bat_throw=player_data.get("bat_throw", ""),
                experience=player_data.get("experience", ""),
                birthplace=player_data.get("birthplace", ""),
                status=player_data.get("status", "Active"),
                created_at=created_at,
                updated_at=updated_at
            )
            db.session.add(player)
        except Exception as e:
            logger.error(f"Error adding player {player_data['id']}: {str(e)}")
    
    db.session.commit()
    logger.info(f"Seeded {len(players_data)} players")

def seed_reels():
    """Seed reel data into the database"""
    # Check if we have reels in the database already
    if db.session.query(ReelModel).count() > 0:
        logger.info("Reels table already has data, skipping seeding")
        return
    
    logger.info("Seeding reels table...")
    
    # Convert in-memory reels to database models
    for reel_data in reels_data:
        try:
            # Parse ISO format dates
            created_at = datetime.fromisoformat(reel_data["created_at"])
            updated_at = datetime.fromisoformat(reel_data["updated_at"])
            
            reel = ReelModel(
                id=reel_data["id"],
                player_id=reel_data["player_id"],
                title=reel_data["title"],
                thumbnail_url=reel_data["thumbnail_url"],
                video_url=reel_data["video_url"],
                duration=reel_data["duration"],
                view_count=reel_data.get("view_count", 0),
                created_at=created_at,
                updated_at=updated_at
            )
            db.session.add(reel)
        except Exception as e:
            logger.error(f"Error adding reel {reel_data['id']}: {str(e)}")
    
    db.session.commit()
    logger.info(f"Seeded {len(reels_data)} reels")

def seed_users():
    """Seed user data into the database"""
    # Check if we have users in the database already
    if db.session.query(UserModel).count() > 0:
        logger.info("Users table already has data, skipping seeding")
        return
    
    logger.info("Seeding users table...")
    
    # Only seed first 100 users to avoid overwhelming the database
    users_to_seed = users_data[:100]
    
    # Convert in-memory users to database models
    for user_data in users_to_seed:
        try:
            # Parse ISO format dates
            created_at = datetime.fromisoformat(user_data["created_at"])
            updated_at = datetime.fromisoformat(user_data["updated_at"])
            registration_date = datetime.fromisoformat(user_data["registration_date"])
            last_login = datetime.fromisoformat(user_data["last_login"])
            
            user = UserModel(
                id=user_data["id"],
                uuid=user_data["uuid"],
                email=user_data["email"],
                username=user_data["username"],
                full_name=user_data["full_name"],
                profile_image=user_data.get("profile_image", ""),
                registration_date=registration_date,
                last_login=last_login,
                status=user_data["status"],
                created_at=created_at,
                updated_at=updated_at
            )
            db.session.add(user)
        except Exception as e:
            logger.error(f"Error adding user {user_data['id']}: {str(e)}")
    
    db.session.commit()
    logger.info(f"Seeded {len(users_to_seed)} users")

def seed_subscribers():
    """Seed subscriber data into the database"""
    # Check if we have subscribers in the database already
    if db.session.query(SubscriberModel).count() > 0:
        logger.info("Subscribers table already has data, skipping seeding")
        return
    
    logger.info("Seeding subscribers table...")
    
    # Only seed first 100 subscribers to avoid overwhelming the database
    subscribers_to_seed = subscribers_data[:100]
    
    # Convert in-memory subscribers to database models
    for subscriber_data in subscribers_to_seed:
        try:
            # Parse ISO format dates
            created_at = datetime.fromisoformat(subscriber_data["created_at"])
            updated_at = datetime.fromisoformat(subscriber_data["updated_at"])
            start_date = datetime.fromisoformat(subscriber_data["start_date"])
            end_date = datetime.fromisoformat(subscriber_data["end_date"])
            
            subscriber = SubscriberModel(
                id=subscriber_data["id"],
                email=subscriber_data["email"],
                name=subscriber_data["name"],
                subscription_type=subscriber_data["subscription_type"],
                start_date=start_date,
                end_date=end_date,
                status=subscriber_data["status"],
                created_at=created_at,
                updated_at=updated_at
            )
            db.session.add(subscriber)
        except Exception as e:
            logger.error(f"Error adding subscriber {subscriber_data['id']}: {str(e)}")
    
    db.session.commit()
    logger.info(f"Seeded {len(subscribers_to_seed)} subscribers")

def seed_user_activity():
    """Seed user activity data into the database"""
    # Check if we have user activity in the database already
    if db.session.query(UserActivityModel).count() > 0:
        logger.info("User activity table already has data, skipping seeding")
        return
    
    logger.info("Seeding user activity table...")
    
    # Convert in-memory user activity to database models
    for activity_data in user_activity_data:
        try:
            # Parse ISO format dates
            date = datetime.fromisoformat(activity_data["date"])
            
            activity = UserActivityModel(
                id=activity_data.get("id", None),  # Some might not have ID
                date=date,
                active_users=activity_data["active_users"],
                new_users=activity_data["new_users"]
            )
            db.session.add(activity)
        except Exception as e:
            logger.error(f"Error adding user activity record: {str(e)}")
    
    db.session.commit()
    logger.info(f"Seeded {len(user_activity_data)} user activity records")