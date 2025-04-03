"""
Role management routes for the Gambit Admin API.
Handles creating, updating, and assigning roles.
"""

from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from models import db, AdminModel, RoleModel, PermissionType
from utils.auth import require_permission
from utils.response_formatter import format_response, format_error
from sqlalchemy import desc

roles_bp = Blueprint('roles', __name__)

@roles_bp.route('/', methods=['GET'])
@jwt_required()
@require_permission(PermissionType.ROLES)
def get_roles():
    """Get all roles with optional filtering"""
    try:
        # Get query parameters
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 10, type=int)
        
        # Query roles with pagination
        query = RoleModel.query.order_by(RoleModel.name)
        pagination = query.paginate(page=page, per_page=per_page)
        
        # Format response
        return format_response({
            'roles': [role.to_dict() for role in pagination.items],
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
        return format_error(f"Error retrieving roles: {str(e)}")

@roles_bp.route('/<int:role_id>', methods=['GET'])
@jwt_required()
@require_permission(PermissionType.ROLES)
def get_role(role_id):
    """Get a specific role by ID"""
    try:
        role = RoleModel.query.get(role_id)
        
        if not role:
            return format_error(f"Role with ID {role_id} not found", status_code=404)
        
        return format_response(role.to_dict())
    
    except Exception as e:
        return format_error(f"Error retrieving role: {str(e)}")

@roles_bp.route('/', methods=['POST'])
@jwt_required()
@require_permission(PermissionType.ROLES)
def create_role():
    """Create a new role"""
    try:
        data = request.get_json()
        
        if not data or not data.get('name'):
            return format_error("Role name is required", status_code=400)
        
        # Check if role with same name already exists
        existing_role = RoleModel.query.filter_by(name=data['name']).first()
        if existing_role:
            return format_error(f"Role with name '{data['name']}' already exists", status_code=400)
        
        # Create new role
        new_role = RoleModel(
            name=data['name'],
            description=data.get('description', ''),
            permissions=data.get('permissions', [])
        )
        
        db.session.add(new_role)
        db.session.commit()
        
        return format_response(new_role.to_dict())
    
    except Exception as e:
        db.session.rollback()
        return format_error(f"Error creating role: {str(e)}")

@roles_bp.route('/<int:role_id>', methods=['PUT'])
@jwt_required()
@require_permission(PermissionType.ROLES)
def update_role(role_id):
    """Update an existing role"""
    try:
        role = RoleModel.query.get(role_id)
        
        if not role:
            return format_error(f"Role with ID {role_id} not found", status_code=404)
        
        data = request.get_json()
        
        if not data:
            return format_error("No data provided", status_code=400)
        
        # Update role fields
        if 'name' in data:
            # Check for duplicate name
            existing_role = RoleModel.query.filter_by(name=data['name']).first()
            if existing_role and existing_role.id != role_id:
                return format_error(f"Role with name '{data['name']}' already exists", status_code=400)
            role.name = data['name']
        
        if 'description' in data:
            role.description = data['description']
        
        if 'permissions' in data:
            role.permissions = data['permissions']
        
        db.session.commit()
        
        return format_response(role.to_dict())
    
    except Exception as e:
        db.session.rollback()
        return format_error(f"Error updating role: {str(e)}")

@roles_bp.route('/<int:role_id>', methods=['DELETE'])
@jwt_required()
@require_permission(PermissionType.ROLES)
def delete_role(role_id):
    """Delete a role"""
    try:
        role = RoleModel.query.get(role_id)
        
        if not role:
            return format_error(f"Role with ID {role_id} not found", status_code=404)
        
        # Check if role is assigned to any admin
        if role.admins:
            return format_error("Cannot delete role that is assigned to administrators", status_code=400)
        
        db.session.delete(role)
        db.session.commit()
        
        return format_response({"message": f"Role '{role.name}' deleted successfully"})
    
    except Exception as e:
        db.session.rollback()
        return format_error(f"Error deleting role: {str(e)}")

@roles_bp.route('/permissions', methods=['GET'])
@jwt_required()
@require_permission(PermissionType.ROLES)
def get_permissions():
    """Get all available permissions"""
    try:
        permissions = [
            {"id": PermissionType.CONTENT, "name": "Content Management"},
            {"id": PermissionType.NOTIFICATION, "name": "Notification Management"},
            {"id": PermissionType.LEAGUES, "name": "Leagues Management"},
            {"id": PermissionType.REELS, "name": "Reels Management"},
            {"id": PermissionType.USERS, "name": "Users Management"},
            {"id": PermissionType.SUBSCRIBERS, "name": "Subscribers Management"},
            {"id": PermissionType.ROLES, "name": "Roles Management"},
            {"id": PermissionType.ALL, "name": "All Permissions (Super Admin)"}
        ]
        
        return format_response(permissions)
    
    except Exception as e:
        return format_error(f"Error retrieving permissions: {str(e)}")

@roles_bp.route('/admin-assignments', methods=['GET'])
@jwt_required()
@require_permission(PermissionType.ROLES)
def get_admin_role_assignments():
    """Get all admin-role assignments"""
    try:
        # Get query parameters
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 10, type=int)
        
        # Query admins with pagination
        query = AdminModel.query.order_by(AdminModel.name)
        pagination = query.paginate(page=page, per_page=per_page)
        
        # Format response with admin and their roles
        assignments = []
        for admin in pagination.items:
            admin_data = admin.to_dict()
            admin_data['roles'] = [role.to_dict() for role in admin.roles]
            assignments.append(admin_data)
        
        return format_response({
            'assignments': assignments,
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
        return format_error(f"Error retrieving admin role assignments: {str(e)}")

@roles_bp.route('/assign', methods=['POST'])
@jwt_required()
@require_permission(PermissionType.ROLES)
def assign_role():
    """Assign a role to an admin"""
    try:
        data = request.get_json()
        
        if not data or not data.get('admin_id') or not data.get('role_id'):
            return format_error("Admin ID and role ID are required", status_code=400)
        
        admin = AdminModel.query.get(data['admin_id'])
        if not admin:
            return format_error(f"Admin with ID {data['admin_id']} not found", status_code=404)
        
        role = RoleModel.query.get(data['role_id'])
        if not role:
            return format_error(f"Role with ID {data['role_id']} not found", status_code=404)
        
        # Check if admin already has this role
        if role in admin.roles:
            return format_error(f"Admin already has the role '{role.name}'", status_code=400)
        
        # Assign role to admin
        admin.roles.append(role)
        db.session.commit()
        
        return format_response({
            "message": f"Role '{role.name}' assigned to admin '{admin.name}' successfully",
            "admin": admin.to_dict()
        })
    
    except Exception as e:
        db.session.rollback()
        return format_error(f"Error assigning role: {str(e)}")

@roles_bp.route('/unassign', methods=['POST'])
@jwt_required()
@require_permission(PermissionType.ROLES)
def unassign_role():
    """Remove a role from an admin"""
    try:
        data = request.get_json()
        
        if not data or not data.get('admin_id') or not data.get('role_id'):
            return format_error("Admin ID and role ID are required", status_code=400)
        
        admin = AdminModel.query.get(data['admin_id'])
        if not admin:
            return format_error(f"Admin with ID {data['admin_id']} not found", status_code=404)
        
        role = RoleModel.query.get(data['role_id'])
        if not role:
            return format_error(f"Role with ID {data['role_id']} not found", status_code=404)
        
        # Check if admin has this role
        if role not in admin.roles:
            return format_error(f"Admin does not have the role '{role.name}'", status_code=400)
        
        # Remove role from admin
        admin.roles.remove(role)
        db.session.commit()
        
        return format_response({
            "message": f"Role '{role.name}' removed from admin '{admin.name}' successfully",
            "admin": admin.to_dict()
        })
    
    except Exception as e:
        db.session.rollback()
        return format_error(f"Error removing role: {str(e)}")