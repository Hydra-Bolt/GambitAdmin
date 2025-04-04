"""
Content routes for the Gambit Admin API.
Manages FAQs, Privacy Policy, and Terms & Conditions content.
"""

import logging
from datetime import datetime
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from sqlalchemy import desc, asc
from models import db, FAQModel, ContentPageModel, faqs_data, content_pages_data, PermissionType
from utils.response_formatter import format_response, format_error
from utils.auth import require_permission

# Configure logger
logger = logging.getLogger(__name__)

# Create blueprint
content_bp = Blueprint('content', __name__)

# FAQ Routes
@content_bp.route('/faqs', methods=['GET'])
@jwt_required()
@require_permission(PermissionType.CONTENT)
def get_faqs():
    """Get all FAQs with optional filtering"""
    try:
        # Parse query parameters
        is_published = request.args.get('is_published')
        
        # Build query
        query = db.session.query(FAQModel)
        
        # Apply filters if provided
        if is_published is not None:
            is_published = is_published.lower() == 'true'
            query = query.filter(FAQModel.is_published == is_published)
        
        # Order by specified order field
        query = query.order_by(asc(FAQModel.order))
        
        # Execute query
        faqs = query.all()
        
        # Convert to dictionary
        faqs_list = [faq.to_dict() for faq in faqs]
        
        return format_response(faqs_list)
    except Exception as e:
        logger.error(f"Error getting FAQs: {str(e)}")
        return format_error(str(e)), 500

@content_bp.route('/faqs/<int:faq_id>', methods=['GET'])
@jwt_required()
@require_permission(PermissionType.CONTENT)
def get_faq(faq_id):
    """Get a specific FAQ by ID"""
    try:
        faq = db.session.get(FAQModel, faq_id)
        if not faq:
            return format_error(f"FAQ with ID {faq_id} not found"), 404
        
        return format_response(faq.to_dict())
    except Exception as e:
        logger.error(f"Error getting FAQ {faq_id}: {str(e)}")
        return format_error(str(e)), 500

@content_bp.route('/faqs', methods=['POST'])
@jwt_required()
@require_permission(PermissionType.CONTENT)
def create_faq():
    """Create a new FAQ"""
    try:
        data = request.json
        if not data:
            return format_error("Invalid request data"), 400
            
        # Validate required fields
        required_fields = ['question', 'answer']
        for field in required_fields:
            if field not in data:
                return format_error(f"Missing required field: {field}"), 400
        
        # Create new FAQ
        new_faq = FAQModel(
            question=data['question'],
            answer=data['answer'],
            order=data.get('order', 0),
            is_published=data.get('is_published', True)
        )
        
        # Add to database
        db.session.add(new_faq)
        db.session.commit()
        
        # Return formatted response
        return jsonify({
            "success": True,
            "data": new_faq.to_dict()
        }), 201
    except Exception as e:
        logger.error(f"Error creating FAQ: {str(e)}")
        db.session.rollback()
        return format_error(str(e)), 500

@content_bp.route('/faqs/<int:faq_id>', methods=['PUT'])
@jwt_required()
@require_permission(PermissionType.CONTENT)
def update_faq(faq_id):
    """Update an existing FAQ"""
    try:
        data = request.json
        if not data:
            return format_error("Invalid request data"), 400
        
        # Find FAQ
        faq = db.session.get(FAQModel, faq_id)
        if not faq:
            return format_error(f"FAQ with ID {faq_id} not found"), 404
        
        # Update fields if provided
        if 'question' in data:
            faq.question = data['question']
        if 'answer' in data:
            faq.answer = data['answer']
        if 'order' in data:
            faq.order = data['order']
        if 'is_published' in data:
            faq.is_published = data['is_published']
        
        # Update the updated_at timestamp
        faq.updated_at = datetime.now()
        
        # Commit changes
        db.session.commit()
        
        return format_response(faq.to_dict())
    except Exception as e:
        logger.error(f"Error updating FAQ {faq_id}: {str(e)}")
        db.session.rollback()
        return format_error(str(e)), 500

@content_bp.route('/faqs/<int:faq_id>', methods=['PATCH'])
@jwt_required()
@require_permission(PermissionType.CONTENT)
def patch_faq(faq_id):
    """Partially update an existing FAQ"""
    try:
        data = request.json
        if not data:
            return format_error("Invalid request data"), 400
        
        # Find FAQ
        faq = db.session.get(FAQModel, faq_id)
        if not faq:
            return format_error(f"FAQ with ID {faq_id} not found"), 404
        
        # Update fields if provided
        if 'question' in data:
            faq.question = data['question']
        if 'answer' in data:
            faq.answer = data['answer']
        if 'order' in data:
            faq.order = data['order']
        if 'is_published' in data:
            faq.is_published = data['is_published']
        
        # Update the updated_at timestamp
        faq.updated_at = datetime.now()
        
        # Commit changes
        db.session.commit()
        
        return format_response(faq.to_dict())
    except Exception as e:
        logger.error(f"Error patching FAQ {faq_id}: {str(e)}")
        db.session.rollback()
        return format_error(str(e)), 500

@content_bp.route('/faqs/<int:faq_id>', methods=['DELETE'])
@jwt_required()
@require_permission(PermissionType.CONTENT)
def delete_faq(faq_id):
    """Delete a FAQ"""
    try:
        # Find FAQ
        faq = db.session.get(FAQModel, faq_id)
        if not faq:
            return format_error(f"FAQ with ID {faq_id} not found"), 404
        
        # Delete from database
        db.session.delete(faq)
        db.session.commit()
        
        return format_response({"message": f"FAQ with ID {faq_id} deleted successfully"})
    except Exception as e:
        logger.error(f"Error deleting FAQ {faq_id}: {str(e)}")
        db.session.rollback()
        return format_error(str(e)), 500

# Content Pages Routes
@content_bp.route('/pages', methods=['GET'])
@jwt_required()
@require_permission(PermissionType.CONTENT)
def get_content_pages():
    """Get all content pages with optional filtering"""
    try:
        # Parse query parameters
        page_type = request.args.get('page_type')
        is_published = request.args.get('is_published')
        
        # Build query
        query = db.session.query(ContentPageModel)
        
        # Apply filters if provided
        if page_type:
            query = query.filter(ContentPageModel.page_type == page_type)
        if is_published is not None:
            is_published = is_published.lower() == 'true'
            query = query.filter(ContentPageModel.is_published == is_published)
        
        # Execute query
        pages = query.all()
        
        # Convert to dictionary
        pages_list = [page.to_dict() for page in pages]
        
        return format_response(pages_list)
    except Exception as e:
        logger.error(f"Error getting content pages: {str(e)}")
        return format_error(str(e)), 500

@content_bp.route('/pages/<int:page_id>', methods=['GET'])
@jwt_required()
@require_permission(PermissionType.CONTENT)
def get_content_page(page_id):
    """Get a specific content page by ID"""
    try:
        page = db.session.get(ContentPageModel, page_id)
        if not page:
            return format_error(f"Content page with ID {page_id} not found"), 404
        
        return format_response(page.to_dict())
    except Exception as e:
        logger.error(f"Error getting content page {page_id}: {str(e)}")
        return format_error(str(e)), 500

@content_bp.route('/pages/type/<page_type>', methods=['GET'])
def get_content_page_by_type(page_type):
    """Get a specific content page by type (privacy_policy, terms_conditions)"""
    try:
        page = db.session.query(ContentPageModel).filter(
            ContentPageModel.page_type == page_type,
            ContentPageModel.is_published == True
        ).first()
        
        if not page:
            return format_error(f"Content page with type {page_type} not found"), 404
        
        return format_response(page.to_dict())
    except Exception as e:
        logger.error(f"Error getting content page by type {page_type}: {str(e)}")
        return format_error(str(e)), 500

@content_bp.route('/pages', methods=['POST'])
@jwt_required()
@require_permission(PermissionType.CONTENT)
def create_content_page():
    """Create a new content page"""
    try:
        data = request.json
        if not data:
            return format_error("Invalid request data"), 400
            
        # Validate required fields
        required_fields = ['page_type', 'title', 'content']
        for field in required_fields:
            if field not in data:
                return format_error(f"Missing required field: {field}"), 400
        
        # Check if a page with this type already exists
        existing_page = db.session.query(ContentPageModel).filter(
            ContentPageModel.page_type == data['page_type']
        ).first()
        
        if existing_page:
            return format_error(f"A content page with type {data['page_type']} already exists"), 400
        
        # Create new content page
        new_page = ContentPageModel(
            page_type=data['page_type'],
            title=data['title'],
            content=data['content'],
            is_published=data.get('is_published', True)
        )
        
        # Add to database
        db.session.add(new_page)
        db.session.commit()
        
        # Return formatted response
        return jsonify({
            "success": True,
            "data": new_page.to_dict()
        }), 201
    except Exception as e:
        logger.error(f"Error creating content page: {str(e)}")
        db.session.rollback()
        return format_error(str(e)), 500

@content_bp.route('/pages/<int:page_id>', methods=['PUT'])
@jwt_required()
@require_permission(PermissionType.CONTENT)
def update_content_page(page_id):
    """Update an existing content page"""
    try:
        data = request.json
        if not data:
            return format_error("Invalid request data"), 400
        
        # Find content page
        page = db.session.get(ContentPageModel, page_id)
        if not page:
            return format_error(f"Content page with ID {page_id} not found"), 404
        
        # Update fields if provided
        if 'title' in data:
            page.title = data['title']
        if 'content' in data:
            page.content = data['content']
        if 'is_published' in data:
            page.is_published = data['is_published']
        
        # Update the updated_at timestamp
        page.updated_at = datetime.now()
        
        # Commit changes
        db.session.commit()
        
        return format_response(page.to_dict())
    except Exception as e:
        logger.error(f"Error updating content page {page_id}: {str(e)}")
        db.session.rollback()
        return format_error(str(e)), 500

@content_bp.route('/pages/<int:page_id>', methods=['PATCH'])
@jwt_required()
@require_permission(PermissionType.CONTENT)
def patch_content_page(page_id):
    """Partially update an existing content page"""
    try:
        data = request.json
        if not data:
            return format_error("Invalid request data"), 400
        
        # Find content page
        page = db.session.get(ContentPageModel, page_id)
        if not page:
            return format_error(f"Content page with ID {page_id} not found"), 404
        
        # Update fields if provided
        if 'title' in data:
            page.title = data['title']
        if 'content' in data:
            page.content = data['content']
        if 'is_published' in data:
            page.is_published = data['is_published']
        
        # Update the updated_at timestamp
        page.updated_at = datetime.now()
        
        # Commit changes
        db.session.commit()
        
        return format_response(page.to_dict())
    except Exception as e:
        logger.error(f"Error patching content page {page_id}: {str(e)}")
        db.session.rollback()
        return format_error(str(e)), 500

@content_bp.route('/pages/<int:page_id>', methods=['DELETE'])
@jwt_required()
@require_permission(PermissionType.CONTENT)
def delete_content_page(page_id):
    """Delete a content page"""
    try:
        # Find content page
        page = db.session.get(ContentPageModel, page_id)
        if not page:
            return format_error(f"Content page with ID {page_id} not found"), 404
        
        # Delete from database
        db.session.delete(page)
        db.session.commit()
        
        return format_response({"message": f"Content page with ID {page_id} deleted successfully"})
    except Exception as e:
        logger.error(f"Error deleting content page {page_id}: {str(e)}")
        db.session.rollback()
        return format_error(str(e)), 500