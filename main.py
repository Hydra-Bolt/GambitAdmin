import logging
from app import app, db, logger

# Configure app context for database operations
with app.app_context():
    # Import models
    from models import (
        SubscriberModel, UserModel, LeagueModel, TeamModel, 
        PlayerModel, ReelModel, UserActivityModel, 
        SubscriberStatsModel, NotificationModel
    )
    
    # Create tables
    db.create_all()
    logger.info("Database tables created")
    
    # Initialize mock data
    from utils.mock_data import initialize_mock_data
    initialize_mock_data()
    
    try:
        # Seed the database with mock data if tables are empty
        from utils.db_seed import seed_database
        seed_database()
        logger.info("Database seeded successfully")
        
        # Seed admin users and roles
        from utils.admin_seed import seed_admin_users
        admin_seeded = seed_admin_users()
        if admin_seeded:
            logger.info("Admin users and roles seeded successfully")
        else:
            logger.info("Admin users and roles already exist")
    except Exception as e:
        logger.error(f"Error seeding database: {str(e)}")

logger.info("Gambit Admin API initialized")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
