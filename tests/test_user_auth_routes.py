"""
Unit tests for user authentication routes
"""

import pytest
import json
import uuid
from datetime import datetime
from flask import url_for

from models import UserModel, db

class TestUserAuth:

    def test_signup_success(self, client):
        """Test successful user signup"""
        # Create a unique test user
        unique_id = str(uuid.uuid4())[:8]
        test_user = {
            "username": f"testuser_{unique_id}",
            "email": f"test_{unique_id}@example.com",
            "password": "TestPassword123!",
            "full_name": "Test User"
        }
        
        # Send request to signup endpoint
        response = client.post(
            '/api/user-auth/signup',
            data=json.dumps(test_user),
            content_type='application/json'
        )
        
        # Check response
        data = json.loads(response.data)
        assert response.status_code == 200
        assert data['success'] is True
        assert 'access_token' in data['data']
        assert 'refresh_token' in data['data']
        assert data['data']['user']['username'] == test_user['username']
        
        # Verify user was created in database
        user = UserModel.query.filter_by(username=test_user['username']).first()
        assert user is not None
        assert user.email == test_user['email']
        assert user.full_name == test_user['full_name']

    def test_signup_duplicate_username(self, client):
        """Test signup with duplicate username"""
        # Create a first user
        unique_id = str(uuid.uuid4())[:8]
        test_user = {
            "username": f"testuser_{unique_id}",
            "email": f"test_{unique_id}@example.com",
            "password": "TestPassword123!",
            "full_name": "Test User"
        }
        
        # First signup should succeed
        response = client.post(
            '/api/user-auth/signup',
            data=json.dumps(test_user),
            content_type='application/json'
        )
        
        # Create a second user with same username but different email
        duplicate_user = {
            "username": test_user['username'],
            "email": f"different_{unique_id}@example.com",
            "password": "TestPassword123!",
            "full_name": "Duplicate User"
        }
        
        # Second signup should fail
        response = client.post(
            '/api/user-auth/signup',
            data=json.dumps(duplicate_user),
            content_type='application/json'
        )
        
        # Check response
        data = json.loads(response.data)
        assert response.status_code == 409
        assert data['success'] is False
        assert 'username already taken' in data['message'].lower()

    def test_login_success(self, client):
        """Test successful user login"""
        # Create a test user
        unique_id = str(uuid.uuid4())[:8]
        test_user = {
            "username": f"testuser_{unique_id}",
            "email": f"test_{unique_id}@example.com",
            "password": "TestPassword123!",
            "full_name": "Test User"
        }
        
        # Create the user
        response = client.post(
            '/api/user-auth/signup',
            data=json.dumps(test_user),
            content_type='application/json'
        )
        
        # Now try to login
        login_data = {
            "username": test_user['username'],
            "password": test_user['password']
        }
        
        response = client.post(
            '/api/user-auth/login',
            data=json.dumps(login_data),
            content_type='application/json'
        )
        
        # Check response
        data = json.loads(response.data)
        assert response.status_code == 200
        assert data['success'] is True
        assert 'access_token' in data['data']
        assert 'refresh_token' in data['data']
        assert data['data']['user']['username'] == test_user['username']

    def test_login_failure(self, client):
        """Test login with wrong password"""
        # Create a test user
        unique_id = str(uuid.uuid4())[:8]
        test_user = {
            "username": f"testuser_{unique_id}",
            "email": f"test_{unique_id}@example.com",
            "password": "TestPassword123!",
            "full_name": "Test User"
        }
        
        # Create the user
        response = client.post(
            '/api/user-auth/signup',
            data=json.dumps(test_user),
            content_type='application/json'
        )
        
        # Try to login with wrong password
        login_data = {
            "username": test_user['username'],
            "password": "WrongPassword123!"
        }
        
        response = client.post(
            '/api/user-auth/login',
            data=json.dumps(login_data),
            content_type='application/json'
        )
        
        # Check response
        data = json.loads(response.data)
        assert response.status_code == 401
        assert data['success'] is False
        assert 'invalid' in data['message'].lower()

    def test_get_profile(self, client):
        """Test getting user profile"""
        # Create a test user
        unique_id = str(uuid.uuid4())[:8]
        test_user = {
            "username": f"testuser_{unique_id}",
            "email": f"test_{unique_id}@example.com",
            "password": "TestPassword123!",
            "full_name": "Test User"
        }
        
        # Create the user and get token
        response = client.post(
            '/api/user-auth/signup',
            data=json.dumps(test_user),
            content_type='application/json'
        )
        
        data = json.loads(response.data)
        access_token = data['data']['access_token']
        
        # Get profile with token
        response = client.get(
            '/api/user-auth/me',
            headers={'Authorization': f'Bearer {access_token}'}
        )
        
        # Check response
        data = json.loads(response.data)
        assert response.status_code == 200
        assert data['success'] is True
        assert data['data']['username'] == test_user['username']
        assert data['data']['email'] == test_user['email']
        assert data['data']['full_name'] == test_user['full_name']

    def test_update_profile(self, client):
        """Test updating user profile"""
        # Create a test user
        unique_id = str(uuid.uuid4())[:8]
        test_user = {
            "username": f"testuser_{unique_id}",
            "email": f"test_{unique_id}@example.com",
            "password": "TestPassword123!",
            "full_name": "Test User"
        }
        
        # Create the user and get token
        response = client.post(
            '/api/user-auth/signup',
            data=json.dumps(test_user),
            content_type='application/json'
        )
        
        data = json.loads(response.data)
        access_token = data['data']['access_token']
        
        # Update profile
        update_data = {
            "full_name": "Updated Name",
            "bio": "This is my updated bio"
        }
        
        response = client.put(
            '/api/user-auth/me',
            data=json.dumps(update_data),
            content_type='application/json',
            headers={'Authorization': f'Bearer {access_token}'}
        )
        
        # Check response
        data = json.loads(response.data)
        assert response.status_code == 200
        assert data['success'] is True
        assert data['data']['user']['full_name'] == update_data['full_name']
        assert data['data']['user']['bio'] == update_data['bio']
        
        # Verify database was updated
        user = UserModel.query.filter_by(username=test_user['username']).first()
        assert user.full_name == update_data['full_name']
        assert user.bio == update_data['bio']

    def test_refresh_token(self, client):
        """Test refreshing access token"""
        # Create a test user
        unique_id = str(uuid.uuid4())[:8]
        test_user = {
            "username": f"testuser_{unique_id}",
            "email": f"test_{unique_id}@example.com",
            "password": "TestPassword123!",
            "full_name": "Test User"
        }
        
        # Create the user and get tokens
        response = client.post(
            '/api/user-auth/signup',
            data=json.dumps(test_user),
            content_type='application/json'
        )
        
        data = json.loads(response.data)
        refresh_token = data['data']['refresh_token']
        
        # Use refresh token to get new access token
        response = client.post(
            '/api/user-auth/refresh',
            headers={'Authorization': f'Bearer {refresh_token}'}
        )
        
        # Check response
        data = json.loads(response.data)
        assert response.status_code == 200
        assert data['success'] is True
        assert 'access_token' in data['data']
        
        # Verify new token works
        new_access_token = data['data']['access_token']
        response = client.get(
            '/api/user-auth/me',
            headers={'Authorization': f'Bearer {new_access_token}'}
        )
        
        assert response.status_code == 200

    def test_change_password(self, client):
        """Test changing user password"""
        # Create a test user
        unique_id = str(uuid.uuid4())[:8]
        test_user = {
            "username": f"testuser_{unique_id}",
            "email": f"test_{unique_id}@example.com",
            "password": "TestPassword123!",
            "full_name": "Test User"
        }
        
        # Create the user and get token
        response = client.post(
            '/api/user-auth/signup',
            data=json.dumps(test_user),
            content_type='application/json'
        )
        
        data = json.loads(response.data)
        access_token = data['data']['access_token']
        
        # Change password
        new_password = "NewPassword456!"
        password_data = {
            "current_password": test_user['password'],
            "new_password": new_password
        }
        
        response = client.post(
            '/api/user-auth/change-password',
            data=json.dumps(password_data),
            content_type='application/json',
            headers={'Authorization': f'Bearer {access_token}'}
        )
        
        # Check response
        data = json.loads(response.data)
        assert response.status_code == 200
        assert data['success'] is True
        
        # Try logging in with new password
        login_data = {
            "username": test_user['username'],
            "password": new_password
        }
        
        response = client.post(
            '/api/user-auth/login',
            data=json.dumps(login_data),
            content_type='application/json'
        )
        
        # Should succeed with new password
        assert response.status_code == 200
        
        # Try logging in with old password (should fail)
        login_data = {
            "username": test_user['username'],
            "password": test_user['password']
        }
        
        response = client.post(
            '/api/user-auth/login',
            data=json.dumps(login_data),
            content_type='application/json'
        )
        
        # Should fail with old password
        assert response.status_code == 401