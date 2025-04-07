"""
Sidebar management utility for Gambit Admin

This module provides functions and data structures for managing the admin sidebar.
It allows for centralized configuration and easier maintenance of sidebar items.
"""
from flask import request

# Define sidebar items with all necessary properties
ADMIN_SIDEBAR = [
    {
        "id": "dashboard",
        "title": "Dashboard", 
        "url": "/dashboard",
        "icon": "chart-pie",
        "implemented": True,
        "permission": None  # No special permission required
    },
    {
        "id": "leagues",
        "title": "Manage Leagues", 
        "url": "/leagues",
        "icon": "trophy",
        "implemented": True,
        "permission": "manage_leagues"
    },
    {
        "id": "users",
        "title": "Manage Users", 
        "url": "/users",
        "icon": "users",
        "implemented": True,
        "permission": "manage_users"
    },
    {
        "id": "subscribers",
        "title": "View Subscription", 
        "url": "/subscribers",
        "icon": "credit-card",
        "implemented": True,
        "permission": "view_subscriptions"
    },
    {
        "id": "odds",
        "title": "Sports Odds", 
        "url": "/odds",
        "icon": "percentage",
        "implemented": True,
        "permission": "odds"
    },
    {
        "id": "reels",
        "title": "Manage Reels", 
        "url": "/reels",
        "icon": "video",
        "implemented": False,
        "permission": "manage_content"
    },
    {
        "id": "notifications",
        "title": "Manage Notification", 
        "url": "/notifications",
        "icon": "bell",
        "implemented": False,
        "permission": "manage_notifications"
    },
    {
        "id": "content",
        "title": "Manage Content", 
        "url": "/content",
        "icon": "file-text",
        "implemented": False,
        "permission": "manage_content"
    },
    {
        "id": "roles",
        "title": "Manage Roles", 
        "url": "/roles",
        "icon": "shield",
        "implemented": False,
        "permission": "manage_roles"
    },
    {
        "id": "admins",
        "title": "Manage Admins", 
        "url": "/admins",
        "icon": "users-cog",
        "implemented": False,
        "permission": "manage_admins"
    }
]

def get_sidebar_items(user=None):
    """
    Get sidebar items filtered based on user permissions.
    
    Args:
        user: The current user (optional). If provided, only show sidebar items 
             the user has permission to access.
             
    Returns:
        list: A list of sidebar items the user can access
    """
    # If no user is provided, return all sidebar items
    if user is None:
        return ADMIN_SIDEBAR
    
    # Filter sidebar items based on user permissions
    filtered_items = []
    for item in ADMIN_SIDEBAR:
        # If no permission is required or user has the permission, include the item
        if item['permission'] is None or user.has_permission(item['permission']):
            filtered_items.append(item)
    
    return filtered_items

def get_active_sidebar_item():
    """
    Determine the active sidebar item based on current URL path.
    
    Returns:
        str: ID of the active sidebar item, or None if no match
    """
    path = request.path
    
    # Strip trailing slash if present
    if path.endswith('/'):
        path = path[:-1]
    
    # Find matching sidebar item based on URL
    for item in ADMIN_SIDEBAR:
        if item['url'] == path:
            return item['id']
    
    # Default to dashboard if on root path
    if path == '':
        return 'dashboard'
    
    return None