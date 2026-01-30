# Role-Based Access Control (RBAC) Implementation

## Overview
This RBAC system enforces strict access control for the Zecpath job platform with three distinct roles:
- **Admin**: Full system control
- **Employer**: Can post and manage jobs
- **Candidate**: Can apply to jobs

## Permission Classes

### Custom Permissions (`apps/core/permissions.py`)
- `IsAdmin`: Admin-only access
- `IsEmployer`: Employer-only access  
- `IsCandidate`: Candidate-only access
- `IsOwnerOrAdmin`: Resource owner or admin access

## Protected Endpoints

### Admin Only
- `GET /api/admin/dashboard/` - System statistics
- `GET /api/profile/` - View all users

### Employer Only
- `POST /api/jobs/create/` - Create job postings
- `GET /api/employer/jobs/` - View own job postings

### Candidate Only
- `POST /api/jobs/<id>/apply/` - Apply to jobs

### Public Access
- `POST /auth/signup/` - User registration
- `POST /auth/login/` - User authentication
- `GET /api/jobs/` - View job listings

## Security Features

### Middleware Protection
- Logs suspicious access attempts
- Monitors role mismatches
- Tracks admin access attempts

### API Abuse Prevention
- Rate limiting: 100/hour for anonymous, 1000/hour for authenticated
- JWT token blacklisting on logout
- Proper error handling for token validation

## Testing Unauthorized Access

Run the security test script:
```bash
python test_rbac.py
```

This tests:
- Unauthorized endpoint access
- Cross-role access attempts
- Proper permission enforcement

## Attack Scenarios Handled

1. **Privilege Escalation**: Users cannot access higher-privilege endpoints
2. **Cross-Role Access**: Employers cannot access candidate functions and vice versa
3. **Token Abuse**: Blacklisted tokens are rejected
4. **Rate Limiting**: Prevents DoS attacks
5. **Data Leakage**: Users can only access their own resources

## Usage Examples

### Creating a Job (Employer Only)
```python
headers = {'Authorization': f'Bearer {employer_token}'}
data = {
    'title': 'Software Engineer',
    'description': 'Python developer needed',
    'location': 'Remote'
}
response = requests.post('/api/jobs/create/', json=data, headers=headers)
```

### Applying to Job (Candidate Only)
```python
headers = {'Authorization': f'Bearer {candidate_token}'}
response = requests.post('/api/jobs/1/apply/', headers=headers)
```

### Admin Dashboard (Admin Only)
```python
headers = {'Authorization': f'Bearer {admin_token}'}
response = requests.get('/api/admin/dashboard/', headers=headers)
```