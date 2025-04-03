"""
Seed script for admin users and roles.
Creates initial admin user and basic roles.
"""

import logging
from models import db, AdminModel, RoleModel, PermissionType

logger = logging.getLogger(__name__)

def seed_admin_users():
    """Seed admin users and roles if they don't exist"""
    try:
        # Check if any admin exists
        admin_exists = AdminModel.query.first() is not None
        
        if not admin_exists:
            logger.info("No admin users found. Creating default admin user...")
            
            # Create super admin role if it doesn't exist
            super_admin_role = RoleModel.query.filter_by(name="Super Admin").first()
            if not super_admin_role:
                super_admin_role = RoleModel(
                    name="Super Admin",
                    description="Full access to all features",
                    permissions=[PermissionType.ALL]
                )
                db.session.add(super_admin_role)
                logger.info("Created Super Admin role")
            
            # Create content manager role
            content_role = RoleModel.query.filter_by(name="Content Manager").first()
            if not content_role:
                content_role = RoleModel(
                    name="Content Manager",
                    description="Manage content and notifications",
                    permissions=[PermissionType.CONTENT, PermissionType.NOTIFICATION]
                )
                db.session.add(content_role)
                logger.info("Created Content Manager role")
            
            # Create reels manager role
            reels_role = RoleModel.query.filter_by(name="Reels Manager").first()
            if not reels_role:
                reels_role = RoleModel(
                    name="Reels Manager",
                    description="Manage reels, leagues, and content",
                    permissions=[PermissionType.REELS, PermissionType.CONTENT, PermissionType.LEAGUES]
                )
                db.session.add(reels_role)
                logger.info("Created Reels Manager role")
            
            # Create default admin user
            admin = AdminModel(
                username="admin",
                name="Administrator",
                email="admin@gambit.com",
                is_active=True
            )
            admin.set_password("admin123")  # Default password should be changed immediately
            
            # Assign super admin role
            admin.roles.append(super_admin_role)
            
            db.session.add(admin)
            db.session.commit()
            logger.info("Created default admin user: username=admin, password=admin123")
            
            # Create additional sample admin users with different roles
            sample_admins = [
                {
                    "username": "content_admin",
                    "name": "Content Administrator",
                    "email": "content@gambit.com",
                    "password": "content123",
                    "roles": [content_role]
                },
                {
                    "username": "reels_admin",
                    "name": "Reels Administrator",
                    "email": "reels@gambit.com",
                    "password": "reels123",
                    "roles": [reels_role]
                }
            ]
            
            for admin_data in sample_admins:
                admin = AdminModel(
                    username=admin_data["username"],
                    name=admin_data["name"],
                    email=admin_data["email"],
                    is_active=True
                )
                admin.set_password(admin_data["password"])
                
                for role in admin_data["roles"]:
                    admin.roles.append(role)
                
                db.session.add(admin)
            
            db.session.commit()
            logger.info("Created sample admin users")
            
            return True
        else:
            logger.info("Admin users already exist, skipping seeding")
            return False
    
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error seeding admin users: {str(e)}")
        return False