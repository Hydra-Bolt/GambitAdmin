"""
Test script for user authentication endpoints.
Run this script to verify that signup, login, and profile endpoints are working correctly.
"""

import requests
import json
import sys
from datetime import datetime

# Configuration
BASE_URL = "http://localhost:5000"  # Change if your app runs on a different port
API_PREFIX = "/api/user-auth"
TEST_USER = {
    "username": f"testuser_{int(datetime.now().timestamp())}",  # Unique username
    "email": f"test_{int(datetime.now().timestamp())}@example.com",  # Unique email
    "password": "TestPassword123!",
    "full_name": "Test User"
}

# Colors for terminal output
class Colors:
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    BLUE = '\033[94m'
    ENDC = '\033[0m'

def print_header(text):
    print(f"\n{Colors.BLUE}=== {text} ==={Colors.ENDC}\n")

def print_success(text):
    print(f"{Colors.GREEN}✓ {text}{Colors.ENDC}")

def print_error(text):
    print(f"{Colors.RED}✗ {text}{Colors.ENDC}")

def print_info(text):
    print(f"{Colors.YELLOW}ℹ {text}{Colors.ENDC}")

def test_signup():
    """Test user signup endpoint"""
    print_header("Testing User Signup")
    
    url = f"{BASE_URL}{API_PREFIX}/signup"
    
    try:
        response = requests.post(url, json=TEST_USER)
        data = response.json()
        
        print(f"Status Code: {response.status_code}")
        print(f"Response: {json.dumps(data, indent=2)}")
        
        if response.status_code == 200 and data.get('success'):
            print_success("Signup successful!")
            return data.get('data', {}).get('access_token'), data.get('data', {}).get('refresh_token')
        else:
            print_error("Signup failed!")
            return None, None
            
    except Exception as e:
        print_error(f"Error: {str(e)}")
        return None, None

def test_login():
    """Test user login endpoint"""
    print_header("Testing User Login")
    
    url = f"{BASE_URL}{API_PREFIX}/login"
    login_data = {
        "username": TEST_USER["username"],
        "password": TEST_USER["password"]
    }
    
    try:
        response = requests.post(url, json=login_data)
        data = response.json()
        
        print(f"Status Code: {response.status_code}")
        print(f"Response: {json.dumps(data, indent=2)}")
        
        if response.status_code == 200 and data.get('success'):
            print_success("Login successful!")
            return data.get('data', {}).get('access_token'), data.get('data', {}).get('refresh_token')
        else:
            print_error("Login failed!")
            return None, None
            
    except Exception as e:
        print_error(f"Error: {str(e)}")
        return None, None

def test_get_profile(access_token):
    """Test get user profile endpoint"""
    print_header("Testing Get Profile")
    
    url = f"{BASE_URL}{API_PREFIX}/me"
    headers = {'Authorization': f'Bearer {access_token}'}
    
    try:
        response = requests.get(url, headers=headers)
        data = response.json()
        
        print(f"Status Code: {response.status_code}")
        print(f"Response: {json.dumps(data, indent=2)}")
        
        if response.status_code == 200 and data.get('success'):
            print_success("Get profile successful!")
            return True
        else:
            print_error("Get profile failed!")
            return False
            
    except Exception as e:
        print_error(f"Error: {str(e)}")
        return False

def test_update_profile(access_token):
    """Test update user profile endpoint"""
    print_header("Testing Update Profile")
    
    url = f"{BASE_URL}{API_PREFIX}/me"
    headers = {'Authorization': f'Bearer {access_token}'}
    profile_data = {
        "full_name": "Updated Test User",
        "bio": "This is a test bio for the test user."
    }
    
    try:
        response = requests.put(url, json=profile_data, headers=headers)
        data = response.json()
        
        print(f"Status Code: {response.status_code}")
        print(f"Response: {json.dumps(data, indent=2)}")
        
        if response.status_code == 200 and data.get('success'):
            print_success("Update profile successful!")
            return True
        else:
            print_error("Update profile failed!")
            return False
            
    except Exception as e:
        print_error(f"Error: {str(e)}")
        return False

def test_refresh_token(refresh_token):
    """Test refresh token endpoint"""
    print_header("Testing Token Refresh")
    
    url = f"{BASE_URL}{API_PREFIX}/refresh"
    headers = {'Authorization': f'Bearer {refresh_token}'}
    
    try:
        response = requests.post(url, headers=headers)
        data = response.json()
        
        print(f"Status Code: {response.status_code}")
        print(f"Response: {json.dumps(data, indent=2)}")
        
        if response.status_code == 200 and data.get('success'):
            print_success("Token refresh successful!")
            return data.get('data', {}).get('access_token')
        else:
            print_error("Token refresh failed!")
            return None
            
    except Exception as e:
        print_error(f"Error: {str(e)}")
        return None

def test_change_password(access_token):
    """Test change password endpoint"""
    print_header("Testing Change Password")
    
    url = f"{BASE_URL}{API_PREFIX}/change-password"
    headers = {'Authorization': f'Bearer {access_token}'}
    new_password = "NewPassword123!"
    password_data = {
        "current_password": TEST_USER["password"],
        "new_password": new_password
    }
    
    try:
        response = requests.post(url, json=password_data, headers=headers)
        data = response.json()
        
        print(f"Status Code: {response.status_code}")
        print(f"Response: {json.dumps(data, indent=2)}")
        
        if response.status_code == 200 and data.get('success'):
            print_success("Password change successful!")
            # Update test user password
            TEST_USER["password"] = new_password
            return True
        else:
            print_error("Password change failed!")
            return False
            
    except Exception as e:
        print_error(f"Error: {str(e)}")
        return False

def run_tests():
    """Run all tests in sequence"""
    print_info("Starting user authentication tests...")
    
    # Test signup
    access_token, refresh_token = test_signup()
    
    if not access_token:
        # If signup fails, try logging in (in case user already exists)
        print_info("Signup failed. Trying login instead...")
        access_token, refresh_token = test_login()
    
    if not access_token:
        print_error("Authentication failed. Cannot continue tests.")
        return False
    
    # Test get profile
    profile_ok = test_get_profile(access_token)
    
    # Test update profile
    update_ok = test_update_profile(access_token)
    
    # Test refresh token
    new_access_token = test_refresh_token(refresh_token)
    refresh_ok = new_access_token is not None
    
    if refresh_ok:
        # Use the new access token for changing password
        access_token = new_access_token
    
    # Test change password
    password_ok = test_change_password(access_token)
    
    # Summary
    print_header("Test Summary")
    print(f"Profile Retrieval: {'✓' if profile_ok else '✗'}")
    print(f"Profile Update: {'✓' if update_ok else '✗'}")
    print(f"Token Refresh: {'✓' if refresh_ok else '✗'}")
    print(f"Password Change: {'✓' if password_ok else '✗'}")
    
    if profile_ok and update_ok and refresh_ok and password_ok:
        print_success("All tests passed successfully!")
        return True
    else:
        print_error("Some tests failed.")
        return False

if __name__ == "__main__":
    # Check if the server is running
    try:
        response = requests.get(f"{BASE_URL}/")
        print_info(f"Server detected at {BASE_URL}")
    except requests.exceptions.ConnectionError:
        print_error(f"No server detected at {BASE_URL}. Make sure your Flask app is running.")
        sys.exit(1)
    
    # Run the tests
    success = run_tests()
    
    # Exit with appropriate code
    sys.exit(0 if success else 1)