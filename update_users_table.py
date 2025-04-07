"""
Script to update the users table schema by adding the password_hash and role columns.

Run this script to fix the 'column users.password_hash does not exist' error.
"""

import os
import logging
import sys
from sqlalchemy import text
from app import app, db

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def update_users_table():
    """Update users table to add password_hash and role columns"""
    try:
        with app.app_context():
            # Check if password_hash column exists
            with db.engine.connect() as connection:
                # First check if the column exists
                result = connection.execute(text(
                    """
                    SELECT column_name 
                    FROM information_schema.columns 
                    WHERE table_name='users' AND column_name='password_hash'
                    """
                ))
                
                # If column doesn't exist, add it
                if result.rowcount == 0:
                    logger.info("Adding password_hash column to users table")
                    connection.execute(text(
                        """
                        ALTER TABLE users 
                        ADD COLUMN password_hash VARCHAR(256) DEFAULT NULL
                        """
                    ))
                    connection.commit()
                    logger.info("Added password_hash column successfully")
                else:
                    logger.info("password_hash column already exists")
                
                # Check if role column exists
                result = connection.execute(text(
                    """
                    SELECT column_name 
                    FROM information_schema.columns 
                    WHERE table_name='users' AND column_name='role'
                    """
                ))
                
                # If column doesn't exist, add it
                if result.rowcount == 0:
                    logger.info("Adding role column to users table")
                    connection.execute(text(
                        """
                        ALTER TABLE users 
                        ADD COLUMN role VARCHAR(20) DEFAULT 'user'
                        """
                    ))
                    connection.commit()
                    logger.info("Added role column successfully")
                else:
                    logger.info("role column already exists")
                
                # Update registration_date and last_login to use DEFAULT now() if they're not nullable
                logger.info("Ensuring registration_date and last_login have proper defaults")
                connection.execute(text(
                    """
                    ALTER TABLE users 
                    ALTER COLUMN registration_date SET DEFAULT CURRENT_TIMESTAMP;
                    """
                ))
                connection.execute(text(
                    """
                    ALTER TABLE users 
                    ALTER COLUMN last_login DROP NOT NULL;
                    """
                ))
                connection.commit()
            
            logger.info("Users table schema update completed successfully")
            return True
    
    except Exception as e:
        logger.error(f"Error updating users table: {e}")
        return False

if __name__ == "__main__":
    success = update_users_table()
    if success:
        print("✅ Users table updated successfully!")
        sys.exit(0)
    else:
        print("❌ Failed to update users table. Check logs for details.")
        sys.exit(1)