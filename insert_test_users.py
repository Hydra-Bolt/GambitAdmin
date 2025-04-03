import sys
import datetime
from app import app, db
from models import UserModel

def insert_test_users():
    with app.app_context():
        # Check if users already exist
        user_count = UserModel.query.count()
        if user_count > 0:
            print(f"Database already has {user_count} users. Skipping insertion.")
            return
        
        # Create test users
        test_users = [
            {
                "uuid": "user-1-johndoe-uuid",
                "email": "john.doe@example.com",
                "username": "johndoe",
                "full_name": "John Doe",
                "profile_image": "https://ui-avatars.com/api/?name=johndoe&background=random",
                "registration_date": datetime.datetime(2024, 1, 15),
                "last_login": datetime.datetime(2025, 3, 28),
                "status": "active"
            },
            {
                "uuid": "user-2-janedoe-uuid",
                "email": "jane.doe@example.com",
                "username": "janedoe",
                "full_name": "Jane Doe",
                "profile_image": "https://ui-avatars.com/api/?name=janedoe&background=random",
                "registration_date": datetime.datetime(2024, 2, 10),
                "last_login": datetime.datetime(2025, 3, 30),
                "status": "active"
            },
            {
                "uuid": "user-3-bobsmith-uuid",
                "email": "bob.smith@example.com",
                "username": "bobsmith",
                "full_name": "Bob Smith",
                "profile_image": "https://ui-avatars.com/api/?name=bobsmith&background=random",
                "registration_date": datetime.datetime(2024, 3, 5),
                "last_login": datetime.datetime(2025, 2, 15),
                "status": "inactive"
            },
            {
                "uuid": "user-premium-uuid",
                "email": "premium.user@example.com",
                "username": "premiumuser",
                "full_name": "Premium User",
                "profile_image": "https://ui-avatars.com/api/?name=premiumuser&background=random",
                "registration_date": datetime.datetime(2023, 12, 1),
                "last_login": datetime.datetime(2025, 4, 1),
                "status": "active"
            },
            {
                "uuid": "user-5-susanjones-uuid",
                "email": "susan.jones@example.com",
                "username": "susanjones",
                "full_name": "Susan Jones",
                "profile_image": "https://ui-avatars.com/api/?name=susanjones&background=random",
                "registration_date": datetime.datetime(2024, 5, 20),
                "last_login": datetime.datetime(2025, 1, 10),
                "status": "suspended"
            }
        ]
        
        # Insert users into database
        for user_data in test_users:
            user = UserModel(**user_data)
            db.session.add(user)
        
        db.session.commit()
        print(f"Successfully inserted {len(test_users)} test users into the database.")

if __name__ == "__main__":
    insert_test_users()