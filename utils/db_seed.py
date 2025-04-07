"""
Database seeding utilities for the Gambit Admin API
"""

import logging
import random
from datetime import datetime, timedelta
from app import db
from models import (
    NotificationModel, subscribers_data, users_data, leagues_data, 
    teams_data, players_data, reels_data, user_activity_data, 
    notifications_data, faqs_data, content_pages_data,
    SubscriberModel, UserModel, LeagueModel, TeamModel, PlayerModel, 
    ReelModel, UserActivityModel, SubscriberStatsModel, FAQModel, ContentPageModel,
    PlanModel
)

# Configure logger
logger = logging.getLogger(__name__)

def seed_database():
    """Seed the database with mock data from the in-memory data structures"""
    try:
        seed_plans()
        seed_leagues()
        seed_teams()
        seed_players()
        seed_reels()
        seed_users()
        seed_subscribers()
        seed_user_activity()
        seed_notifications()
        seed_faqs()
        seed_content_pages()
        logger.info("Database seeded successfully")
    except Exception as e:
        logger.error(f"Error seeding database: {str(e)}")
        db.session.rollback()

def seed_plans():
    """Seed subscription plans into the database"""
    # Check if we have plans in the database already
    if db.session.query(PlanModel).count() > 0:
        logger.info("Plans table already has data, skipping seeding")
        return
    
    logger.info("Seeding plans table...")
    
    # Create the two subscription plans
    monthly_plan = PlanModel(
        id=1,
        name="Monthly",
        description="Access to all premium features on a monthly billing cycle",
        price=50.99,
        duration_days=30,
        is_active=True,
        created_at=datetime.now(),
        updated_at=datetime.now()
    )
    
    yearly_plan = PlanModel(
        id=2,
        name="Yearly",
        description="Access to all premium features on an annual billing cycle at a discounted rate",
        price=150.99,
        duration_days=365,
        is_active=True,
        created_at=datetime.now(),
        updated_at=datetime.now()
    )
    
    db.session.add(monthly_plan)
    db.session.add(yearly_plan)
    db.session.commit()
    logger.info("Seeded 2 subscription plans")

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
            
            # Generate a secure password hash for the user
            user = UserModel(
                id=user_data["id"],
                uuid=user_data["uuid"],
                email=user_data["email"],
                username=user_data["username"],
                full_name=user_data["full_name"],
                password_hash="",  # Will be set below
                profile_image=user_data.get("profile_image", ""),
                bio=user_data.get("bio", ""),
                registration_date=registration_date,
                last_login=last_login,
                status=user_data["status"],
                role=user_data.get("role", "user"),
                favorite_sports=user_data.get("favorite_sports", []),
                favorite_teams=user_data.get("favorite_teams", []),
                favorite_players=user_data.get("favorite_players", []),
                created_at=created_at,
                updated_at=updated_at
            )
            
            # Set a default password - in a real app this would be more secure
            user.set_password("password123")
            
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
    
    # Get all plans and users
    plans = db.session.query(PlanModel).all()
    users = db.session.query(UserModel).all()
    
    if not plans or not users:
        logger.error("Cannot seed subscribers: plans or users not found")
        return
    
    # Create a subscription for approximately 60% of users
    users_to_subscribe = random.sample(users, k=int(len(users) * 0.6))
    
    for i, user in enumerate(users_to_subscribe):
        try:
            # Randomly choose a plan
            plan = random.choice(plans)
            
            # Determine start date (between 1-180 days ago)
            days_ago = random.randint(1, 180)
            start_date = datetime.now() - timedelta(days=days_ago)
            
            # Set end date based on plan duration
            end_date = start_date + timedelta(days=plan.duration_days)
            
            # Determine status based on end date
            if end_date > datetime.now():
                status = "active"
            else:
                status = "expired"
            
            # Randomly determine if auto-renew is enabled (70% chance)
            auto_renew = random.random() < 0.7
            
            # Randomly pick a payment method
            payment_methods = ["credit_card", "paypal", "apple_pay", "google_pay"]
            payment_method = random.choice(payment_methods)
            
            # Create a simple payment details object
            payment_details = {
                "last_four": f"{random.randint(1000, 9999)}",
                "expiry": f"{random.randint(1, 12)}/24"
            }
            
            subscriber = SubscriberModel(
                id=i + 1,
                user_id=user.id,
                plan_id=plan.id,
                start_date=start_date,
                end_date=end_date,
                status=status,
                payment_method=payment_method,
                payment_details=payment_details,
                auto_renew=auto_renew,
                created_at=start_date,
                updated_at=start_date
            )
            db.session.add(subscriber)
            
        except Exception as e:
            logger.error(f"Error adding subscription for user {user.id}: {str(e)}")
    
    db.session.commit()
    logger.info(f"Seeded {len(users_to_subscribe)} subscriptions")

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

def seed_faqs():
    """Seed FAQ data into the database"""
    # Check if we have FAQs in the database already
    if db.session.query(FAQModel).count() > 0:
        logger.info("FAQs table already has data, skipping seeding")
        return
    
    logger.info("Seeding FAQs table...")
    
    # Convert in-memory FAQs to database models
    for faq_data in faqs_data:
        try:
            # Parse ISO format dates
            created_at = datetime.fromisoformat(faq_data["created_at"])
            updated_at = datetime.fromisoformat(faq_data["updated_at"])
            
            faq = FAQModel(
                question=faq_data["question"],
                answer=faq_data["answer"],
                order=faq_data["order"],
                is_published=faq_data["is_published"],
                created_at=created_at,
                updated_at=updated_at
            )
            db.session.add(faq)
        except Exception as e:
            logger.error(f"Error adding FAQ: {str(e)}")
    
    db.session.commit()
    logger.info(f"Seeded {len(faqs_data)} FAQs")

def seed_content_pages():
    """Seed content pages data into the database"""
    # Check if we have content pages in the database already
    if db.session.query(ContentPageModel).count() > 0:
        logger.info("Content pages table already has data, skipping seeding")
        return
    
    logger.info("Seeding content pages table...")
    
    # Convert in-memory content pages to database models
    for page_data in content_pages_data:
        try:
            # Parse ISO format dates
            created_at = datetime.fromisoformat(page_data["created_at"])
            updated_at = datetime.fromisoformat(page_data["updated_at"])
            
            page = ContentPageModel(
                page_type=page_data["page_type"],
                title=page_data["title"],
                content=page_data["content"],
                is_published=page_data["is_published"],
                created_at=created_at,
                updated_at=updated_at
            )
            db.session.add(page)
        except Exception as e:
            logger.error(f"Error adding content page: {str(e)}")
    
    db.session.commit()
    logger.info(f"Seeded {len(content_pages_data)} content pages")