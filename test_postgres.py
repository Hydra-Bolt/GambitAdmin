"""
Test PostgreSQL Connection for Gambit Admin

This script tests if the PostgreSQL database connection works properly.
Run this after setting up your database with setup_postgres.py.
"""

import os
import sys
import time
from dotenv import load_dotenv
import sqlalchemy
from sqlalchemy import text

def test_connection():
    """Test the connection to PostgreSQL database"""
    print("\n=== Testing PostgreSQL Connection ===\n")
    
    # Try to load from .env file first
    load_dotenv()
    
    # Get DATABASE_URL
    database_url = os.environ.get("DATABASE_URL")
    if not database_url:
        print("❌ DATABASE_URL environment variable is not set.")
        print("Make sure you've run set_env.bat (Windows) or source set_env.sh (Unix/Mac).")
        sys.exit(1)
    
    # Print redacted database URL for verification
    # Redact password for security
    redacted_url = database_url
    if "@" in database_url and ":" in database_url:
        parts = database_url.split("@")
        credentials = parts[0].split("://")[1].split(":")
        redacted_url = f"{parts[0].split('://')[0]}://{credentials[0]}:****@{parts[1]}"
    
    print(f"Database URL: {redacted_url}")
    print("Attempting to connect to PostgreSQL...")
    
    # Try to connect to the database
    try:
        engine = sqlalchemy.create_engine(database_url)
        connection = engine.connect()
        
        # Execute a simple query to test the connection
        result = connection.execute(text("SELECT version();"))
        version = result.fetchone()[0]
        
        print(f"\n✅ Connection successful!")
        print(f"PostgreSQL version: {version}")
        
        # Test if we can create a table
        print("\nTesting table creation...")
        try:
            connection.execute(text("""
                CREATE TABLE IF NOT EXISTS connection_test (
                    id SERIAL PRIMARY KEY,
                    test_data TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
            """))
            
            # Insert a test row
            connection.execute(text("""
                INSERT INTO connection_test (test_data) 
                VALUES ('Connection test at ' || NOW());
            """))
            
            # Retrieve the data
            result = connection.execute(text("SELECT * FROM connection_test;"))
            rows = result.fetchall()
            
            print(f"✅ Table creation and data insertion successful!")
            print(f"Rows in test table: {len(rows)}")
            
            # Clean up the test table
            connection.execute(text("DROP TABLE connection_test;"))
            print("Test table cleaned up.")
            
        except Exception as e:
            print(f"❌ Failed to create/use test table: {e}")
            print("You may not have proper permissions on this database.")
            
        connection.close()
        
    except Exception as e:
        print(f"\n❌ Connection failed: {e}")
        print("\nPossible issues:")
        print("1. PostgreSQL service is not running")
        print("2. Database credentials are incorrect")
        print("3. Database does not exist")
        print("4. Network/firewall issues")
        sys.exit(1)
    
    print("\n=== Database Connection Test Complete ===")
    print("Your database setup looks good! You can now run the main application.")
    print("Run 'python main.py' to initialize the database schema and start the app.")

if __name__ == "__main__":
    test_connection()