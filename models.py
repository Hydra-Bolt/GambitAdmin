# In-memory data storage for MVP
# This file defines the data structures and provides access to the mock database

from datetime import datetime
from typing import Dict, List, Any

# Global variables to store data
subscribers_data: List[Dict[str, Any]] = []
users_data: List[Dict[str, Any]] = []
leagues_data: List[Dict[str, Any]] = []
teams_data: List[Dict[str, Any]] = []
user_activity_data: List[Dict[str, Any]] = []

# Record structures
class Subscriber:
    @staticmethod
    def create_record(id: int, email: str, name: str, subscription_type: str, 
                      start_date: datetime, end_date: datetime, status: str) -> Dict[str, Any]:
        return {
            "id": id,
            "email": email,
            "name": name,
            "subscription_type": subscription_type,  # monthly, yearly
            "start_date": start_date.isoformat(),
            "end_date": end_date.isoformat(),
            "status": status,  # active, expired, cancelled
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat()
        }

class User:
    @staticmethod
    def create_record(id: int, email: str, username: str, 
                      registration_date: datetime, last_login: datetime, 
                      status: str) -> Dict[str, Any]:
        return {
            "id": id,
            "email": email,
            "username": username,
            "registration_date": registration_date.isoformat(),
            "last_login": last_login.isoformat(),
            "status": status,  # active, inactive, suspended
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat()
        }

class League:
    @staticmethod
    def create_record(id: int, name: str, category: str, 
                      country: str, logo_url: str, popularity: int) -> Dict[str, Any]:
        return {
            "id": id,
            "name": name,
            "category": category,  # baseball, football, basketball, etc.
            "country": country,
            "logo_url": logo_url,
            "popularity": popularity,  # view count or rating
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
