# ZecPath API Endpoints with Examples

## Base URL: `http://localhost:8000`

---

## 🔐 Authentication Endpoints

### 1. Home API
```http
GET /
```
**Response (200):**
```json
{
  "success": true,
  "message": "API is running",
  "data": {"message": "Hello Zecpath Backend"}
}
```

### 2. User Signup
```http
POST /auth/signup/
Content-Type: application/json

{
  "email": "john@example.com",
  "password": "password123",
  "role": "candidate",
  "first_name": "John",
  "last_name": "Doe"
}
```
**Response (201):**
```json
{
  "success": true,
  "message": "User registered successfully",
  "data": {
    "user": {
      "email": "john@example.com",
      "role": "candidate",
      "first_name": "John",
      "last_name": "Doe"
    },
    "refresh": "eyJ0eXAiOiJKV1QiLCJhbGc...",
    "access": "eyJ0eXAiOiJKV1QiLCJhbGc..."
  }
}
```

### 3. User Login
```http
POST /auth/login/
Content-Type: application/json

{
  "email": "john@example.com",
  "password": "password123"
}
```
**Response (200):**
```json
{
  "success": true,
  "message": "Login successful",
  "data": {
    "user": {
      "email": "john@example.com",
      "role": "candidate",
      "first_name": "John",
      "last_name": "Doe"
    },
    "refresh": "eyJ0eXAiOiJKV1QiLCJhbGc...",
    "access": "eyJ0eXAiOiJKV1QiLCJhbGc..."
  }
}
```

### 4. Logout
```http
POST /auth/logout/
Authorization: Bearer <access_token>
Content-Type: application/json

{
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGc..."
}
```
**Response (200):**
```json
{
  "success": true,
  "message": "Logout successful",
  "data": null
}
```

### 5. Refresh Token
```http
POST /auth/refresh/
Content-Type: application/json

{
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGc..."
}
```
**Response (200):**
```json
{
  "access": "eyJ0eXAiOiJKV1QiLCJhbGc..."
}
```

---

## 💼 Job Endpoints

### 6. Get All Jobs (Public)
```http
GET /api/jobs/
```
**Response (200):**
```json
[
  {
    "id": 1,
    "title": "Software Developer",
    "description": "Looking for a skilled developer",
    "location": "New York",
    "status": "published",
    "created_at": "2024-01-15T10:30:00Z",
    "employer": {
      "company_name": "Tech Corp"
    }
  }
]
```

### 7. Create Job (Employer Only)
```http
POST /api/jobs/create/
Authorization: Bearer <employer_token>
Content-Type: application/json

{
  "title": "Senior Python Developer",
  "description": "We need an experienced Python developer",
  "location": "San Francisco",
  "status": "published"
}
```
**Response (201):**
```json
{
  "id": 2,
  "title": "Senior Python Developer",
  "description": "We need an experienced Python developer",
  "location": "San Francisco",
  "status": "published",
  "created_at": "2024-01-15T11:00:00Z"
}
```

### 8. Update Job (Employer Only)
```http
PUT /api/jobs/1/update/
Authorization: Bearer <employer_token>
Content-Type: application/json

{
  "title": "Senior Software Developer",
  "description": "Updated job description",
  "location": "New York",
  "status": "published"
}
```
**Response (200):**
```json
{
  "id": 1,
  "title": "Senior Software Developer",
  "description": "Updated job description",
  "location": "New York",
  "status": "published"
}
```

### 9. Delete Job (Employer Only)
```http
DELETE /api/jobs/1/update/
Authorization: Bearer <employer_token>
```
**Response (204):**
```json
{
  "success": true,
  "message": "Job deleted successfully"
}
```

### 10. Apply to Job (Candidate Only)
```http
POST /api/jobs/1/apply/
Authorization: Bearer <candidate_token>
```
**Response (201):**
```json
{
  "id": 1,
  "candidate": 1,
  "job": 1,
  "status": "pending",
  "applied_at": "2024-01-15T12:00:00Z"
}
```

---

## 👤 Profile Endpoints

### 11. Get Candidate Profile
```http
GET /api/candidate/profile/
Authorization: Bearer <candidate_token>
```
**Response (200):**
```json
{
  "id": 1,
  "user": {
    "email": "john@example.com",
    "first_name": "John",
    "last_name": "Doe"
  },
  "skills": {"python": "advanced", "django": "intermediate"},
  "education": "Computer Science",
  "experience": "2 years in web development",
  "expected_salary": 75000,
  "experience_years": 2,
  "resume": "http://localhost:8000/media/resumes/john_resume.pdf"
}
```

### 12. Update Candidate Profile
```http
PUT /api/candidate/profile/
Authorization: Bearer <candidate_token>
Content-Type: application/json

{
  "skills": {"python": "expert", "react": "intermediate"},
  "education": "Masters in Computer Science",
  "experience": "3 years full-stack development",
  "expected_salary": 85000,
  "experience_years": 3
}
```
**Response (200):**
```json
{
  "id": 1,
  "skills": {"python": "expert", "react": "intermediate"},
  "education": "Masters in Computer Science",
  "experience": "3 years full-stack development",
  "expected_salary": 85000,
  "experience_years": 3
}
```

### 13. Get Employer Profile
```http
GET /api/employer/profile/
Authorization: Bearer <employer_token>
```
**Response (200):**
```json
{
  "id": 1,
  "user": {
    "email": "hr@techcorp.com",
    "first_name": "Jane",
    "last_name": "Smith"
  },
  "company_name": "Tech Corp",
  "website": "https://techcorp.com",
  "domain": "Technology",
  "company_description": "Leading tech company",
  "company_size": "100-500",
  "verification": true
}
```

### 14. Get Employer Jobs
```http
GET /api/employer/jobs/
Authorization: Bearer <employer_token>
```
**Response (200):**
```json
[
  {
    "id": 1,
    "title": "Software Developer",
    "description": "Looking for a skilled developer",
    "location": "New York",
    "status": "published",
    "created_at": "2024-01-15T10:30:00Z"
  }
]
```

---

## 📄 Resume Endpoints

### 15. Upload Resume (Candidate Only)
```http
POST /api/resume/upload/
Authorization: Bearer <candidate_token>
Content-Type: multipart/form-data

resume: [file.pdf]
```
**Response (200):**
```json
{
  "success": true,
  "message": "Resume uploaded successfully",
  "data": {
    "resume_url": "http://localhost:8000/media/resumes/john_resume.pdf"
  }
}
```

### 16. Download Resume
```http
GET /api/resume/download/
Authorization: Bearer <candidate_token>
```
**Response (200):** File download

### 17. Download Resume by ID (Employer/Admin)
```http
GET /api/resume/download/1/
Authorization: Bearer <employer_token>
```
**Response (200):** File download

### 18. Delete Resume (Candidate Only)
```http
DELETE /api/resume/delete/
Authorization: Bearer <candidate_token>
```
**Response (200):**
```json
{
  "success": true,
  "message": "Resume deleted successfully"
}
```

---

## 🔧 Admin Endpoints

### 19. Admin Dashboard (Admin Only)
```http
GET /api/admin/dashboard/
Authorization: Bearer <admin_token>
```
**Response (200):**
```json
{
  "total_users": 150,
  "total_jobs": 45,
  "total_applications": 230,
  "employers": 25,
  "candidates": 120
}
```

### 20. Get All Users (Admin Only)
```http
GET /api/profile/
Authorization: Bearer <admin_token>
```
**Response (200):**
```json
[
  {
    "id": 1,
    "email": "john@example.com",
    "role": "candidate",
    "first_name": "John",
    "last_name": "Doe",
    "is_verified": false,
    "created_at": "2024-01-15T09:00:00Z"
  }
]
```

---

## ❌ Error Examples

### 401 Unauthorized
```http
GET /api/profile/
```
**Response (401):**
```json
{
  "success": false,
  "message": "Authentication required",
  "data": null,
  "errors": {}
}
```

### 403 Forbidden
```http
GET /api/admin/dashboard/
Authorization: Bearer <candidate_token>
```
**Response (403):**
```json
{
  "success": false,
  "message": "Permission denied",
  "data": null,
  "errors": {}
}
```

### 400 Bad Request
```http
POST /auth/signup/
Content-Type: application/json

{
  "email": "",
  "password": ""
}
```
**Response (400):**
```json
{
  "success": false,
  "message": "Validation failed",
  "data": null,
  "errors": {
    "email": ["This field is required."],
    "password": ["This field is required."],
    "role": ["This field is required."]
  }
}
```

### 404 Not Found
```http
GET /api/jobs/999/update/
Authorization: Bearer <employer_token>
```
**Response (404):**
```json
{
  "success": false,
  "message": "Resource not found",
  "data": null,
  "errors": {}
}
```

---

## 🧪 Test Users

Create these test users for different role testing:

```bash
# Admin
POST /auth/signup/
{
  "email": "admin@zecpath.com",
  "password": "admin123",
  "role": "admin",
  "first_name": "Admin",
  "last_name": "User"
}

# Employer
POST /auth/signup/
{
  "email": "employer@company.com",
  "password": "employer123",
  "role": "employer",
  "first_name": "HR",
  "last_name": "Manager"
}

# Candidate
POST /auth/signup/
{
  "email": "candidate@example.com",
  "password": "candidate123",
  "role": "candidate",
  "first_name": "Job",
  "last_name": "Seeker"
}
```