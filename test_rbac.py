#!/usr/bin/env python
"""
RBAC Security Test Script
Tests role-based access control and unauthorized access scenarios
"""
import requests
import json

BASE_URL = "http://localhost:8000"

def test_unauthorized_access():
    """Test unauthorized access attempts"""
    print("=== Testing Unauthorized Access ===")
    
    # Test admin endpoint without auth
    response = requests.get(f"{BASE_URL}/api/admin/dashboard/")
    print(f"Admin dashboard (no auth): {response.status_code}")
    
    # Test job creation without auth
    response = requests.post(f"{BASE_URL}/api/jobs/create/", json={"title": "Test Job"})
    print(f"Job creation (no auth): {response.status_code}")

def test_role_enforcement():
    """Test role-based access enforcement"""
    print("\n=== Testing Role Enforcement ===")
    
    # Create test users
    users = {
        'admin': {'email': 'admin@test.com', 'password': 'testpass123', 'role': 'admin'},
        'employer': {'email': 'employer@test.com', 'password': 'testpass123', 'role': 'employer'},
        'candidate': {'email': 'candidate@test.com', 'password': 'testpass123', 'role': 'candidate'}
    }
    
    tokens = {}
    
    # Register and login users
    for role, user_data in users.items():
        # Register
        signup_data = {**user_data, 'confirm_password': user_data['password'], 'first_name': role.title(), 'last_name': 'User'}
        response = requests.post(f"{BASE_URL}/auth/signup/", json=signup_data)
        print(f"{role} signup: {response.status_code}")
        
        # Login
        login_data = {'email': user_data['email'], 'password': user_data['password']}
        response = requests.post(f"{BASE_URL}/auth/login/", json=login_data)
        if response.status_code == 200:
            tokens[role] = response.json()['access']
            print(f"{role} login: Success")
        else:
            print(f"{role} login: Failed - {response.status_code}")
    
    # Test cross-role access attempts
    print("\n--- Cross-Role Access Tests ---")
    
    # Candidate trying to create job (should fail)
    if 'candidate' in tokens:
        headers = {'Authorization': f'Bearer {tokens["candidate"]}'}
        response = requests.post(f"{BASE_URL}/api/jobs/create/", 
                               json={"title": "Unauthorized Job", "description": "Test", "location": "Test"},
                               headers=headers)
        print(f"Candidate creating job: {response.status_code} (should be 403)")
    
    # Employer trying to access admin dashboard (should fail)
    if 'employer' in tokens:
        headers = {'Authorization': f'Bearer {tokens["employer"]}'}
        response = requests.get(f"{BASE_URL}/api/admin/dashboard/", headers=headers)
        print(f"Employer accessing admin: {response.status_code} (should be 403)")
    
    # Admin accessing everything (should succeed)
    if 'admin' in tokens:
        headers = {'Authorization': f'Bearer {tokens["admin"]}'}
        response = requests.get(f"{BASE_URL}/api/admin/dashboard/", headers=headers)
        print(f"Admin accessing dashboard: {response.status_code} (should be 200)")

if __name__ == "__main__":
    print("Starting RBAC Security Tests...")
    print("Make sure Django server is running on localhost:8000")
    
    try:
        test_unauthorized_access()
        test_role_enforcement()
        print("\n=== Tests Complete ===")
    except requests.exceptions.ConnectionError:
        print("Error: Cannot connect to Django server. Make sure it's running on localhost:8000")