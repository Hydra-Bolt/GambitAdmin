"""
Response formatter utilities for the Gambit Admin API.
Provides consistent response formatting across all endpoints.
"""

from flask import jsonify

def format_response(data, message=None):
    """Format a successful API response"""
    response = {
        "success": True,
        "data": data
    }
    
    if message:
        response["message"] = message
    
    return jsonify(response)

def format_error(message, status_code=500, error_code=None):
    """Format an error API response"""
    response = {
        "success": False,
        "message": message
    }
    
    if error_code:
        response["error_code"] = error_code
    
    return jsonify(response), status_code