"""
Database Migration Script for Gambit Admin

This script updates the PostgreSQL database schema to add the email_verified column to the users table.
"""

import os
import sys
import logging
import psycopg2
from psycopg2 import sql

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s:%(name)s:%(message)s')
logger = logging.getLogger(__name__)

def get_database_url():
    """Get database URL from environment variable or .env file"""
    # Try to get from environment variable
    db_url = os.environ.get('DATABASE_URL')
    
    # If not in environment, try to read from .env file
    if not db_url:
        try:
            with open('.env', 'r') as f:
                for line in f:
                    if line.startswith('DATABASE_URL='):
                        db_url = line.strip().split('=', 1)[1]
                        break
        except FileNotFoundError:
            logger.error("No .env file found and DATABASE_URL not set in environment")
            sys.exit(1)
    
    if not db_url:
        logger.error("DATABASE_URL not found in environment or .env file")
        sys.exit(1)
        
    return db_url

def parse_database_url(db_url):
    """Parse database URL into connection parameters"""
    # Expected format: postgresql://username:password@host:port/dbname
    if not db_url.startswith('postgresql://'):
        logger.error(f"Unsupported database URL format: {db_url}")
        sys.exit(1)
        
    # Remove the protocol part
    db_url = db_url[len('postgresql://'):]
    
    # Split user:password@host:port/dbname
    auth_host_db = db_url.split('@', 1)
    if len(auth_host_db) != 2:
        logger.error(f"Invalid database URL format: {db_url}")
        sys.exit(1)
        
    auth, host_db = auth_host_db
    
    # Split username:password
    auth_parts = auth.split(':', 1)
    username = auth_parts[0]
    password = auth_parts[1] if len(auth_parts) > 1 else ''
    
    # Split host:port/dbname
    host_db_parts = host_db.split('/', 1)
    if len(host_db_parts) != 2:
        logger.error(f"Invalid database URL format: {db_url}")
        sys.exit(1)
        
    host_port, dbname = host_db_parts
    
    # Split host:port
    host_port_parts = host_port.split(':', 1)
    host = host_port_parts[0]
    port = host_port_parts[1] if len(host_port_parts) > 1 else '5432'
    
    return {
        'dbname': dbname,
        'user': username,
        'password': password,
        'host': host,
        'port': port
    }

def add_email_verified_column():
    """Add email_verified column to users table"""
    db_url = get_database_url()
    db_params = parse_database_url(db_url)
    
    try:
        logger.info(f"Connecting to database {db_params['dbname']} on {db_params['host']}")
        conn = psycopg2.connect(**db_params)
        conn.autocommit = True
        cursor = conn.cursor()
        
        # Check if the column already exists
        cursor.execute("""
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_name = 'users' AND column_name = 'email_verified';
        """)
        
        if cursor.fetchone():
            logger.info("Column 'email_verified' already exists in users table. No changes needed.")
            return True
        
        # Add the column to the table
        logger.info("Adding email_verified column to users table")
        cursor.execute("""
            ALTER TABLE users
            ADD COLUMN email_verified BOOLEAN NOT NULL DEFAULT FALSE;
        """)
        
        logger.info("Successfully added email_verified column to users table")
        return True
        
    except Exception as e:
        logger.error(f"Error updating database schema: {str(e)}")
        return False
        
    finally:
        if 'conn' in locals():
            cursor.close()
            conn.close()

def main():
    print("Gambit Admin Database Migration")
    print("==============================")
    
    success = add_email_verified_column()
    
    if success:
        print("\nMigration completed successfully!")
        print("You can now run your application.")
    else:
        print("\nMigration failed. Please check the error messages.")
        sys.exit(1)

if __name__ == "__main__":
    main()