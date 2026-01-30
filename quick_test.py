import requests

BASE_URL = "http://localhost:8000"

# 1. Test public endpoints
print("1. Testing public access...")
response = requests.get(f"{BASE_URL}/api/jobs/")
print(f"Jobs list: {response.status_code}")

# 2. Test unauthorized access
print("\n2. Testing unauthorized access...")
response = requests.get(f"{BASE_URL}/api/admin/dashboard/")
print(f"Admin dashboard (no auth): {response.status_code} - Should be 401")

response = requests.post(f"{BASE_URL}/api/jobs/create/", json={"title": "Test"})
print(f"Job creation (no auth): {response.status_code} - Should be 401")

# 3. Create test users and get tokens
print("\n3. Creating test users...")
users = {
    'admin': {'email': 'admin@test.com', 'role': 'admin'},
    'employer': {'email': 'employer@test.com', 'role': 'employer'},
    'candidate': {'email': 'candidate@test.com', 'role': 'candidate'}
}

tokens = {}
for role, data in users.items():
    # Signup
    signup_data = {**data, 'password': 'test123', 'confirm_password': 'test123', 'first_name': role, 'last_name': 'user'}
    requests.post(f"{BASE_URL}/auth/signup/", json=signup_data)
    
    # Login
    login_data = {'email': data['email'], 'password': 'test123'}
    response = requests.post(f"{BASE_URL}/auth/login/", json=login_data)
    if response.status_code == 200:
        tokens[role] = response.json()['access']
        print(f"{role} token obtained")

# 4. Test role-based access
print("\n4. Testing role-based access...")

# Admin endpoints
if 'admin' in tokens:
    headers = {'Authorization': f'Bearer {tokens["admin"]}'}
    response = requests.get(f"{BASE_URL}/api/admin/dashboard/", headers=headers)
    print(f"Admin dashboard: {response.status_code} - Should be 200")

# Employer endpoints  
if 'employer' in tokens:
    headers = {'Authorization': f'Bearer {tokens["employer"]}'}
    response = requests.post(f"{BASE_URL}/api/jobs/create/", 
                           json={"title": "Test Job", "description": "Test", "location": "Remote"},
                           headers=headers)
    print(f"Employer job creation: {response.status_code} - Should be 201")

# Cross-role access (should fail)
if 'candidate' in tokens:
    headers = {'Authorization': f'Bearer {tokens["candidate"]}'}
    response = requests.post(f"{BASE_URL}/api/jobs/create/", 
                           json={"title": "Unauthorized", "description": "Test", "location": "Test"},
                           headers=headers)
    print(f"Candidate job creation: {response.status_code} - Should be 403")

print("\nTest complete!")