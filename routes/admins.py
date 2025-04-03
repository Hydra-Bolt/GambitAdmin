"""
Admin management routes for the Gambit Admin API.
Handles creating, updating, and managing admin users.
"""

from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from models import db, AdminModel, RoleModel, PermissionType
from utils.auth import require_permission
from utils.response_formatter import format_response, format_error
from sqlalchemy import desc

admins_bp = Blueprint('admins', __name__)

@admins_bp.route('/', methods=['GET'])
@jwt_required()
@require_permission(PermissionType.ROLES)
def get_admins():
    """Get all admin users with optional filtering"""
    try:
        # Get query parameters
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 10, type=int)
        
        # Query admins with pagination
        query = AdminModel.query.order_by(AdminModel.name)
        pagination = query.paginate(page=page, per_page=per_page)
        
        # Format response
        return format_response({
            'admins': [admin.to_dict() for admin in pagination.items],
            'pagination': {
                'total': pagination.total,
                'pages': pagination.pages,
                'page': page,
                'per_page': per_page,
                'has_next': pagination.has_next,
                'has_prev': pagination.has_prev
            }
        })
    
    except Exception as e:
        return format_error(f"Error retrieving admins: {str(e)}")

@admins_bp.route('/<int:admin_id>', methods=['GET'])
@jwt_required()
@require_permission(PermissionType.ROLES)
def get_admin(admin_id):
    """Get a specific admin by ID"""
    try:
        admin = AdminModel.query.get(admin_id)
        
        if not admin:
            return format_error(f"Admin with ID {admin_id} not found", status_code=404)
        
        return format_response(admin.to_dict())
    
    except Exception as e:
        return format_error(f"Error retrieving admin: {str(e)}")

@admins_bp.route('/', methods=['POST'])
@jwt_required()
@require_permission(PermissionType.ROLES)
def create_admin():
    """Create a new admin user"""
    try:
        data = request.get_json()
        
        if not data or not data.get('username') or not data.get('email') or not data.get('name') or not data.get('password'):
            return format_error("Username, email, name, and password are required", status_code=400)
        
        # Check if admin with same username or email already exists
        existing_admin = AdminModel.query.filter_by(username=data['username']).first()
        if existing_admin:
            return format_error(f"Admin with username '{data['username']}' already exists", status_code=400)
        
        existing_admin = AdminModel.query.filter_by(email=data['email']).first()
        if existing_admin:
            return format_error(f"Admin with email '{data['email']}' already exists", status_code=400)
        
        # Create new admin
        new_admin = AdminModel(
            username=data['username'],
            email=data['email'],
            name=data['name'],
            is_active=data.get('is_active', True)
        )
        
        # Set password
        new_admin.set_password(data['password'])
        
        # Assign roles if provided
        if data.get('role_ids'):
            for role_id in data['role_ids']:
                role = RoleModel.query.get(role_id)
                if role:
                    new_admin.roles.append(role)
        
        db.session.add(new_admin)
        db.session.commit()
        
        return format_response(new_admin.to_dict())
    
    except Exception as e:
        db.session.rollback()
        return format_error(f"Error creating admin: {str(e)}")

@admins_bp.route('/<int:admin_id>', methods=['PUT'])
@jwt_required()
@require_permission(PermissionType.ROLES)
def update_admin(admin_id):
    """Update an existing admin user"""
    try:
        admin = AdminModel.query.get(admin_id)
        
        if not admin:
            return format_error(f"Admin with ID {admin_id} not found", status_code=404)
        
        # Prevent self-deactivation
        current_admin_id = get_jwt_identity()
        if int(current_admin_id) == admin_id and request.get_json().get('is_active') is False:
            return format_error("You cannot deactivate your own account", status_code=400)
        
        data = request.get_json()
        
        if not data:
            return format_error("No data provided", status_code=400)
        
        # Update admin fields
        if 'username' in data:
            # Check for duplicate username
            existing_admin = AdminModel.query.filter_by(username=data['username']).first()
            if existing_admin and existing_admin.id != admin_id:
                return format_error(f"Admin with username '{data['username']}' already exists", status_code=400)
            admin.username = data['username']
        
        if 'email' in data:
            # Check for duplicate email
            existing_admin = AdminModel.query.filter_by(email=data['email']).first()
            if existing_admin and existing_admin.id != admin_id:
                return format_error(f"Admin with email '{data['email']}' already exists", status_code=400)
            admin.email = data['email']
        
        if 'name' in data:
            admin.name = data['name']
        
        if 'is_active' in data:
            admin.is_active = data['is_active']
        
        # Update password if provided
        if 'password' in data:
            admin.set_password(data['password'])
        
        # Update roles if provided
        if 'role_ids' in data:
            # Clear existing roles
            admin.roles = []
            
            # Add new roles
            for role_id in data['role_ids']:
                role = RoleModel.query.get(role_id)
                if role:
                    admin.roles.append(role)
        
        db.session.commit()
        
        return format_response(admin.to_dict())
    
    except Exception as e:
        db.session.rollback()
        return format_error(f"Error updating admin: {str(e)}")

@admins_bp.route('/<int:admin_id>', methods=['DELETE'])
@jwt_required()
@require_permission(PermissionType.ROLES)
def delete_admin(admin_id):
    """Delete an admin user"""
    try:
        admin = AdminModel.query.get(admin_id)
        
        if not admin:
            return format_error(f"Admin with ID {admin_id} not found", status_code=404)
        
        # Prevent self-deletion
        current_admin_id = get_jwt_identity()
        if int(current_admin_id) == admin_id:
            return format_error("You cannot delete your own account", status_code=400)
        
        db.session.delete(admin)
        db.session.commit()
        
        return format_response({"message": f"Admin '{admin.name}' deleted successfully"})
    
    except Exception as e:
        db.session.rollback()
        return format_error(f"Error deleting admin: {str(e)}")

@admins_bp.route('/<int:admin_id>/toggle-status', methods=['PATCH'])
@jwt_required()
@require_permission(PermissionType.ROLES)
def toggle_admin_status(admin_id):
    """Toggle admin active status"""
    try:
        admin = AdminModel.query.get(admin_id)
        
        if not admin:
            return format_error(f"Admin with ID {admin_id} not found", status_code=404)
        
        # Prevent self-deactivation
        current_admin_id = get_jwt_identity()
        if int(current_admin_id) == admin_id:
            return format_error("You cannot change the status of your own account", status_code=400)
        
        # Toggle status
        admin.is_active = not admin.is_active
        db.session.commit()
        
        status = "activated" if admin.is_active else "deactivated"
        return format_response({
            "message": f"Admin '{admin.name}' {status} successfully",
            "admin": admin.to_dict()
        })
    
    except Exception as e:
        db.session.rollback()
        return format_error(f"Error toggling admin status: {str(e)}")