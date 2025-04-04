import json
import pytest
from tests.conftest import auth_header, assert_successful_response, assert_error_response
from models import AdminModel

def test_auth_test_route(client):
    """Test the auth test route."""
    response = client.get('/api/auth/test')
    assert_successful_response(response)
    assert json.loads(response.data)['data']['message'] == "Auth API is working"

def test_login_success(client, setup_admins):
    """Test successful login with valid credentials."""
    response = client.post('/api/auth/login', json={
        'username': 'superadmin',
        'password': 'superadmin123'
    })
    data = assert_successful_response(response)
    assert 'token' in data['data']
    assert 'admin' in data['data']
    assert data['data']['admin']['username'] == 'superadmin'

def test_login_invalid_credentials(client, setup_admins):
    """Test login with invalid credentials."""
    # Invalid password
    response = client.post('/api/auth/login', json={
        'username': 'superadmin',
        'password': 'wrongpassword'
    })
    assert_error_response(response, 401, "Invalid username or password")
    
    # Invalid username
    response = client.post('/api/auth/login', json={
        'username': 'nonexistentuser',
        'password': 'superadmin123'
    })
    assert_error_response(response, 401, "Invalid username or password")

def test_login_inactive_account(client, setup_admins):
    """Test login with inactive account."""
    response = client.post('/api/auth/login', json={
        'username': 'inactiveadmin',
        'password': 'inactive123'
    })
    assert_error_response(response, 403, "Your account has been deactivated")

def test_login_missing_fields(client):
    """Test login with missing fields."""
    # Missing username
    response = client.post('/api/auth/login', json={
        'password': 'superadmin123'
    })
    assert_error_response(response, 400, "Missing username or password")
    
    # Missing password
    response = client.post('/api/auth/login', json={
        'username': 'superadmin'
    })
    assert_error_response(response, 400, "Missing username or password")
    
    # Empty request
    response = client.post('/api/auth/login', json={})
    assert_error_response(response, 400, "Missing username or password")

def test_get_current_user(client, auth_tokens, setup_admins):
    """Test getting current user profile."""
    # Successful request
    response = client.get('/api/auth/me', headers=auth_header(auth_tokens['super_admin']))
    data = assert_successful_response(response)
    assert data['data']['username'] == 'superadmin'
    
    # Test with content admin
    response = client.get('/api/auth/me', headers=auth_header(auth_tokens['content_admin']))
    data = assert_successful_response(response)
    assert data['data']['username'] == 'contentadmin'

def test_get_current_user_no_auth(client):
    """Test getting current user without authentication."""
    response = client.get('/api/auth/me')
    assert response.status_code in (401, 422)  # 401 Unauthorized or 422 Unprocessable Entity (missing token)

def test_change_password(client, auth_tokens, setup_admins):
    """Test changing password."""
    # Successful password change
    response = client.post('/api/auth/change-password', json={
        'current_password': 'superadmin123',
        'new_password': 'newpassword123'
    }, headers=auth_header(auth_tokens['super_admin']))
    assert_successful_response(response, "Password changed successfully")
    
    # Verify old password no longer works
    admin = AdminModel.query.get(setup_admins['super_admin'].id)
    assert not admin.check_password('superadmin123')
    
    # Verify new password works
    assert admin.check_password('newpassword123')

def test_change_password_invalid_current(client, auth_tokens):
    """Test changing password with invalid current password."""
    response = client.post('/api/auth/change-password', json={
        'current_password': 'wrongpassword',
        'new_password': 'newpassword123'
    }, headers=auth_header(auth_tokens['super_admin']))
    assert_error_response(response, 400, "Current password is incorrect")

def test_change_password_missing_fields(client, auth_tokens):
    """Test changing password with missing fields."""
    # Missing current password
    response = client.post('/api/auth/change-password', json={
        'new_password': 'newpassword123'
    }, headers=auth_header(auth_tokens['super_admin']))
    assert_error_response(response, 400, "Missing")
    
    # Missing new password
    response = client.post('/api/auth/change-password', json={
        'current_password': 'superadmin123'
    }, headers=auth_header(auth_tokens['super_admin']))
    assert_error_response(response, 400, "Missing")
    
    # Empty request
    response = client.post('/api/auth/change-password', json={}, headers=auth_header(auth_tokens['super_admin']))
    assert_error_response(response, 400, "Missing")

def test_test_jwt(client, auth_tokens):
    """Test the JWT test endpoint."""
    response = client.get('/api/auth/test-jwt', headers=auth_header(auth_tokens['super_admin']))
    data = assert_successful_response(response)
    assert data['data']['message'] == "JWT verification successful"
    
    # Test with no token
    response = client.get('/api/auth/test-jwt')
    data = json.loads(response.data)
    assert "No valid Bearer token found" in data['data']['message']