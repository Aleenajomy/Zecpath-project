import requests
import json
from datetime import datetime

class SecurityTester:
    def __init__(self, base_url="http://localhost:8000"):
        self.base_url = base_url
        self.results = []
    
    def log_test(self, test_name, expected_status, actual_status, passed, details=""):
        result = {
            "test_name": test_name,
            "expected_status": expected_status,
            "actual_status": actual_status,
            "passed": passed,
            "details": details,
            "timestamp": datetime.now().isoformat()
        }
        self.results.append(result)
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{status} - {test_name}: Expected {expected_status}, Got {actual_status}")
    
    def test_unauthorized_access(self):
        """Test accessing protected endpoints without authentication"""
        protected_endpoints = [
            "/api/profile/",
            "/api/admin/dashboard/",
            "/api/jobs/create/",
            "/api/candidate/profile/",
            "/api/employer/profile/"
        ]
        
        for endpoint in protected_endpoints:
            try:
                response = requests.get(f"{self.base_url}{endpoint}")
                passed = response.status_code == 401
                self.log_test(
                    f"Unauthorized access to {endpoint}",
                    401,
                    response.status_code,
                    passed,
                    f"Response: {response.json() if response.headers.get('content-type') == 'application/json' else response.text}"
                )
            except Exception as e:
                self.log_test(f"Unauthorized access to {endpoint}", 401, "ERROR", False, str(e))
    
    def test_invalid_token(self):
        """Test with invalid/expired tokens"""
        headers = {"Authorization": "Bearer invalid_token_here"}
        
        try:
            response = requests.get(f"{self.base_url}/api/profile/", headers=headers)
            passed = response.status_code == 401
            self.log_test(
                "Invalid token access",
                401,
                response.status_code,
                passed,
                f"Response: {response.json() if response.headers.get('content-type') == 'application/json' else response.text}"
            )
        except Exception as e:
            self.log_test("Invalid token access", 401, "ERROR", False, str(e))
    
    def test_role_violations(self):
        """Test role-based access violations"""
        # First, create test users and get tokens
        test_users = [
            {"email": "candidate_test@example.com", "role": "candidate"},
            {"email": "employer_test@example.com", "role": "employer"}
        ]
        
        tokens = {}
        
        # Create users and get tokens
        for user in test_users:
            signup_data = {
                "email": user["email"],
                "password": "testpass123",
                "role": user["role"],
                "first_name": "Test",
                "last_name": "User"
            }
            
            try:
                # Signup
                response = requests.post(f"{self.base_url}/auth/signup/", json=signup_data)
                if response.status_code in [200, 201]:
                    data = response.json()
                    if data.get("success") and data.get("data"):
                        tokens[user["role"]] = data["data"]["access"]
                    else:
                        # Try login if user already exists
                        login_response = requests.post(f"{self.base_url}/auth/login/", json={
                            "email": user["email"],
                            "password": "testpass123"
                        })
                        if login_response.status_code == 200:
                            login_data = login_response.json()
                            if login_data.get("success") and login_data.get("data"):
                                tokens[user["role"]] = login_data["data"]["access"]
            except Exception as e:
                print(f"Error creating user {user['email']}: {e}")
        
        # Test role violations
        role_tests = [
            {
                "role": "candidate",
                "forbidden_endpoints": [
                    "/api/admin/dashboard/",
                    "/api/jobs/create/"
                ]
            },
            {
                "role": "employer", 
                "forbidden_endpoints": [
                    "/api/admin/dashboard/",
                    "/api/jobs/1/apply/"
                ]
            }
        ]
        
        for test in role_tests:
            if test["role"] in tokens:
                headers = {"Authorization": f"Bearer {tokens[test['role']]}"}
                
                for endpoint in test["forbidden_endpoints"]:
                    try:
                        response = requests.get(f"{self.base_url}{endpoint}", headers=headers)
                        passed = response.status_code == 403
                        self.log_test(
                            f"{test['role'].title()} accessing {endpoint}",
                            403,
                            response.status_code,
                            passed,
                            f"Response: {response.json() if response.headers.get('content-type') == 'application/json' else response.text}"
                        )
                    except Exception as e:
                        self.log_test(f"{test['role'].title()} accessing {endpoint}", 403, "ERROR", False, str(e))
    
    def test_status_codes(self):
        """Test various HTTP status codes"""
        # Test 404 - Not Found
        try:
            response = requests.get(f"{self.base_url}/api/nonexistent/")
            passed = response.status_code == 404
            self.log_test("404 Not Found test", 404, response.status_code, passed)
        except Exception as e:
            self.log_test("404 Not Found test", 404, "ERROR", False, str(e))
        
        # Test 400 - Bad Request (invalid signup data)
        try:
            response = requests.post(f"{self.base_url}/auth/signup/", json={})
            passed = response.status_code == 400
            self.log_test("400 Bad Request test", 400, response.status_code, passed)
        except Exception as e:
            self.log_test("400 Bad Request test", 400, "ERROR", False, str(e))
    
    def run_all_tests(self):
        """Run all security tests"""
        print("🔒 Starting Security Tests for ZecPath API")
        print("=" * 50)
        
        self.test_unauthorized_access()
        self.test_invalid_token()
        self.test_role_violations()
        self.test_status_codes()
        
        # Summary
        total_tests = len(self.results)
        passed_tests = sum(1 for r in self.results if r["passed"])
        failed_tests = total_tests - passed_tests
        
        print("\n" + "=" * 50)
        print(f"📊 Test Summary:")
        print(f"Total Tests: {total_tests}")
        print(f"Passed: {passed_tests} ✅")
        print(f"Failed: {failed_tests} ❌")
        print(f"Success Rate: {(passed_tests/total_tests)*100:.1f}%")
        
        # Save results to file
        with open("security_test_results.json", "w") as f:
            json.dump(self.results, f, indent=2)
        
        print(f"\n📄 Detailed results saved to: security_test_results.json")
        
        return self.results

if __name__ == "__main__":
    tester = SecurityTester()
    tester.run_all_tests()