# ZecPath API Documentation

## Overview
ZecPath is a job portal API built with Django REST Framework featuring role-based authentication and comprehensive error handling.

## Base URL
```
http://localhost:8000
```

## Authentication
The API uses JWT (JSON Web Token) authentication. Include the token in the Authorization header:
```
Authorization: Bearer <your_access_token>
```

## Standard Response Format
All API responses follow this standardized format:

### Success Response
```json
{
    "success": true,
    "message": "Operation successful",
    "data": { ... },
    "errors": {}
}
```

### Error Response
```json
{
    "success": false,
    "message": "Error description",
    "data": null,
    "errors": { ... }
}
```

## HTTP Status Codes

| Code | Status | Description |
|------|--------|-------------|
| 200 | OK | Request successful |
| 201 | Created | Resource created successfully |
| 400 | Bad Request | Invalid request data |
| 401 | Unauthorized | Authentication required |
| 403 | Forbidden | Permission denied |
| 404 | Not Found | Resource not found |
| 500 | Server Error | Internal server error |

## User Roles

- **Admin**: Full system access
- **Employer**: Can create/manage jobs, view applications
- **Candidate**: Can apply to jobs, manage profile

## API Endpoints

### Authentication

#### POST /auth/signup/
Register a new user.

**Request Body:**
```json
{
    "email": "user@example.com",
    "password": "password123",
    "role": "candidate|employer|admin",
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
            "email": "user@example.com",
            "role": "candidate",
            "first_name": "John",
            "last_name": "Doe"
        },
        "access": "jwt_access_token",
        "refresh": "jwt_refresh_token"
    }
}
```

#### POST /auth/login/
Authenticate user and get tokens.

**Request Body:**
```json
{
    "email": "user@example.com",
    "password": "password123"
}
```

**Response (200):**
```json
{
    "success": true,
    "message": "Login successful",
    "data": {
        "user": { ... },
        "access": "jwt_access_token",
        "refresh": "jwt_refresh_token"
    }
}
```

#### POST /auth/logout/
Logout user and blacklist refresh token.

**Request Body:**
```json
{
    "refresh": "jwt_refresh_token"
}
```

### Jobs

#### GET /api/jobs/
Get all published jobs (Public access).

**Response (200):**
```json
{
    "success": true,
    "message": "Success",
    "data": [
        {
            "id": 1,
            "title": "Software Developer",
            "description": "Job description",
            "location": "New York",
            "status": "published",
            "created_at": "2024-01-01T00:00:00Z"
        }
    ]
}
```

#### POST /api/jobs/create/
Create a new job (Employer only).

**Request Body:**
```json
{
    "title": "Software Developer",
    "description": "Looking for a skilled developer",
    "location": "New York",
    "status": "published"
}
```

#### PUT /api/jobs/{id}/update/
Update a job (Employer only - own jobs).

### Security Testing

#### Unauthorized Access (401)
```bash
curl -X GET http://localhost:8000/api/profile/
# Expected: 401 Unauthorized
```

#### Role Violation (403)
```bash
# Candidate trying to access admin endpoint
curl -X GET http://localhost:8000/api/admin/dashboard/ \
  -H "Authorization: Bearer <candidate_token>"
# Expected: 403 Forbidden
```

#### Invalid Token (401)
```bash
curl -X GET http://localhost:8000/api/profile/ \
  -H "Authorization: Bearer invalid_token"
# Expected: 401 Unauthorized
```

#### Not Found (404)
```bash
curl -X GET http://localhost:8000/api/nonexistent/
# Expected: 404 Not Found
```

#### Bad Request (400)
```bash
curl -X POST http://localhost:8000/auth/signup/ \
  -H "Content-Type: application/json" \
  -d '{}'
# Expected: 400 Bad Request
```

## Error Handling

### Validation Errors (400)
```json
{
    "success": false,
    "message": "Validation failed",
    "data": null,
    "errors": {
        "email": ["This field is required."],
        "password": ["This field is required."]
    }
}
```

### Authentication Errors (401)
```json
{
    "success": false,
    "message": "Authentication required",
    "data": null,
    "errors": {}
}
```

### Permission Errors (403)
```json
{
    "success": false,
    "message": "Permission denied",
    "data": null,
    "errors": {}
}
```

### Not Found Errors (404)
```json
{
    "success": false,
    "message": "Resource not found",
    "data": null,
    "errors": {}
}
```

## Postman Testing

1. Import the collection: `postman/ZecPath_API_Collection.json`
2. Import the environment: `postman/ZecPath_Environment.json`
3. Run the security tests folder to validate:
   - Unauthorized access attempts
   - Role-based access violations
   - Invalid token handling
   - Proper status code responses

## Security Features

- JWT token authentication
- Role-based access control
- Token blacklisting on logout
- Request rate limiting
- File upload validation
- Custom exception handling
- Standardized error responses

## Testing Commands

Run security tests:
```bash
python security_tests.py
```

Start development server:
```bash
python manage.py runserver
```