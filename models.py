# In-memory data storage for MVP
# This file defines the data structures and provides access to the mock database

from datetime import datetime
from typing import Dict, List, Any, Optional

# Global variables to store data
subscribers_data: List[Dict[str, Any]] = []
users_data: List[Dict[str, Any]] = []
leagues_data: List[Dict[str, Any]] = []
teams_data: List[Dict[str, Any]] = []
players_data: List[Dict[str, Any]] = []
reels_data: List[Dict[str, Any]] = []
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
                      status: str, profile_image: str = "", 
                      full_name: str = "", uuid: str = "") -> Dict[str, Any]:
        return {
            "id": id,
            "uuid": uuid or f"user-{id}-uuid",  # In a real system, this would be a proper UUID
            "email": email,
            "username": username,
            "full_name": full_name or username,  # Use full name if provided, otherwise username
            "profile_image": profile_image or f"https://ui-avatars.com/api/?name={username}&background=random",
            "registration_date": registration_date.isoformat(),
            "last_login": last_login.isoformat(),
            "status": status,  # active, inactive, suspended
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat()
        }

class League:
    @staticmethod
    def create_record(id: int, name: str, category: str, 
                      country: str, logo_url: str, popularity: int,
                      founded_date: datetime = datetime(1900, 1, 1), 
                      headquarters: str = "", commissioner: str = "",
                      divisions: List[str] = [], num_teams: int = 0, 
                      enabled: bool = True) -> Dict[str, Any]:
        return {
            "id": id,
            "name": name,
            "category": category,  # baseball, football, basketball, etc.
            "country": country,
            "logo_url": logo_url,
            "popularity": popularity,  # view count or rating
            "founded_date": founded_date.isoformat() if founded_date else datetime(1900, 1, 1).isoformat(),
            "headquarters": headquarters or "",
            "commissioner": commissioner or "",
            "divisions": divisions or [],
            "num_teams": num_teams,
            "enabled": enabled,
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

class Player:
    @staticmethod
    def create_record(id: int, name: str, team_id: int, league_id: int, 
                      position: str, jersey_number: str, profile_image: str,
                      dob: Optional[datetime] = None, college: str = "", 
                      height_weight: str = "", bat_throw: str = "",
                      experience: str = "", birthplace: str = "", 
                      status: str = "Active") -> Dict[str, Any]:
        return {
            "id": id,
            "name": name,
            "team_id": team_id,
            "league_id": league_id,
            "position": position,
            "jersey_number": jersey_number,
            "profile_image": profile_image,
            "dob": dob.isoformat() if dob else "",
            "college": college,
            "height_weight": height_weight,
            "bat_throw": bat_throw,
            "experience": experience,
            "birthplace": birthplace,
            "status": status,
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat()
        }

class Reel:
    @staticmethod
    def create_record(id: int, player_id: int, title: str, 
                      thumbnail_url: str, video_url: str, 
                      duration: float, view_count: int = 0,
                      created_at: Optional[datetime] = None) -> Dict[str, Any]:
        now = datetime.now()
        return {
            "id": id,
            "player_id": player_id,
            "title": title,
            "thumbnail_url": thumbnail_url,
            "video_url": video_url,
            "duration": duration,  # in seconds
            "view_count": view_count,
            "created_at": created_at.isoformat() if created_at else now.isoformat(),
            "updated_at": now.isoformat()
        }
