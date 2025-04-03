from flask import jsonify

def format_response(data, status_code=200):
    """Format API response in a consistent structure"""
    response = {
        "success": True,
        "data": data
    }
    return jsonify(response), status_code

def format_error(message, details=None, status_code=400):
    """Format API error response in a consistent structure"""
    response = {
        "success": False,
        "error": {
            "message": message,
            "details": details
        }
    }
    return jsonify(response), status_code
