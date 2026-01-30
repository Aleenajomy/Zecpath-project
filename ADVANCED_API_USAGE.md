# Advanced API Features Usage Examples

## 1. Pagination Examples

### Offset-based Pagination (Standard)
```bash
# Get jobs with pagination
GET /api/v2/jobs/?page=1&page_size=10

# Response includes pagination metadata
{
  "count": 150,
  "next": "http://localhost:8000/api/v2/jobs/?page=2&page_size=10",
  "previous": null,
  "page_size": 10,
  "total_pages": 15,
  "current_page": 1,
  "results": [...]
}
```

### Cursor-based Pagination (for Jobs and Applications)
```bash
# Get jobs with cursor pagination (better for real-time data)
GET /api/v2/jobs/?cursor=cD0yMDI0LTEyLTE5KzEwJTNBMDA%3D

# Response
{
  "next": "http://localhost:8000/api/v2/jobs/?cursor=next_cursor_value",
  "previous": "http://localhost:8000/api/v2/jobs/?cursor=prev_cursor_value",
  "results": [...]
}
```

## 2. Filtering Examples

### Filter Jobs
```bash
# Filter by status and date
GET /api/v2/jobs/?status=published&created_after=2024-01-01&created_before=2024-12-31

# Filter by location and company
GET /api/v2/jobs/?location=New York&company=Google

# Filter by multiple criteria
GET /api/v2/jobs/?status=published&location__icontains=remote&title__icontains=python
```

### Filter Users (Admin only)
```bash
# Filter by role and verification status
GET /api/v2/users/?role=candidate&is_verified=true

# Filter by creation date
GET /api/v2/users/?created_after=2024-01-01&role=employer
```

### Filter Applications
```bash
# Filter by status and date
GET /api/v2/applications/?status=pending&applied_after=2024-01-01

# Filter by job title or candidate email
GET /api/v2/applications/?job_title__icontains=developer&candidate_email__icontains=john
```

### Filter Candidates
```bash
# Filter by experience and salary range
GET /api/v2/candidates/?experience_years_min=2&experience_years_max=5&expected_salary_min=50000

# Filter candidates with resume
GET /api/v2/candidates/?has_resume=true
```

### Filter Employers
```bash
# Filter verified employers
GET /api/v2/employers/?verification=true

# Filter by company size and domain
GET /api/v2/employers/?company_size__icontains=startup&domain__icontains=tech
```

## 3. Search Examples

### Search Jobs
```bash
# Keyword search across title, description, location, company
GET /api/v2/jobs/?search=python developer

# Search with filters
GET /api/v2/jobs/?search=remote&status=published&location__icontains=USA
```

### Search Users
```bash
# Search by name or email
GET /api/v2/users/?search=john.doe@example.com

# Search with role filter
GET /api/v2/users/?search=john&role=candidate
```

### Search Candidates
```bash
# Search by name, email, education, or experience
GET /api/v2/candidates/?search=computer science

# Search with experience filter
GET /api/v2/candidates/?search=python&experience_years_min=3
```

## 4. Ordering Examples

```bash
# Order jobs by creation date (newest first)
GET /api/v2/jobs/?ordering=-created_at

# Order by title alphabetically
GET /api/v2/jobs/?ordering=title

# Multiple ordering criteria
GET /api/v2/jobs/?ordering=-status,created_at

# Order candidates by experience and salary
GET /api/v2/candidates/?ordering=-experience_years,expected_salary
```

## 5. Combined Advanced Queries

### Complex Job Search
```bash
# Search for Python jobs in remote locations, published in last 30 days, ordered by relevance
GET /api/v2/jobs/?search=python&location__icontains=remote&status=published&created_after=2024-11-19&ordering=-created_at&page_size=20
```

### Advanced Candidate Filtering
```bash
# Find experienced candidates with resume, sorted by experience
GET /api/v2/candidates/?experience_years_min=5&has_resume=true&search=senior&ordering=-experience_years&page_size=15
```

### Application Analytics
```bash
# Get pending applications from last week
GET /api/v2/applications/?status=pending&applied_after=2024-12-12&ordering=-applied_at
```

## 6. Custom Actions

### Job-specific Actions
```bash
# Get only published jobs
GET /api/v2/jobs/published/

# Get applications for a specific job
GET /api/v2/jobs/123/applications/

# Update application status (employer/admin)
PATCH /api/v2/applications/456/update_status/
{
  "status": "accepted"
}
```

### User Statistics
```bash
# Get user statistics by role (admin only)
GET /api/v2/users/stats/

# Response:
[
  {"role": "candidate", "count": 150},
  {"role": "employer", "count": 45},
  {"role": "admin", "count": 3}
]
```

### Specialized Endpoints
```bash
# Get candidates with resume
GET /api/v2/candidates/with_resume/

# Get verified employers
GET /api/v2/employers/verified/

# Get pending applications
GET /api/v2/applications/pending/
```

## 7. Performance Optimizations

### Optimized Queries (Automatic)
- All ViewSets use `select_related()` and `prefetch_related()` to prevent N+1 queries
- Database indexes on frequently queried fields
- Composite indexes for common filter combinations

### Query Examples with Optimizations
```bash
# This query automatically includes related employer and user data
GET /api/v2/jobs/123/

# Applications include candidate, job, and employer data in single query
GET /api/v2/applications/?job_title__icontains=developer

# Candidates include user data and application counts
GET /api/v2/candidates/?experience_years_min=3
```

## 8. Error Handling

### Validation Errors
```bash
# Invalid filter value
GET /api/v2/jobs/?status=invalid_status

# Response:
{
  "error": "Select a valid choice. invalid_status is not one of the available choices."
}
```

### Permission Errors
```bash
# Unauthorized access to admin endpoints
GET /api/v2/users/

# Response:
{
  "detail": "You do not have permission to perform this action."
}
```

## 9. Response Format Examples

### Paginated Response
```json
{
  "count": 150,
  "next": "http://localhost:8000/api/v2/jobs/?page=2",
  "previous": null,
  "page_size": 10,
  "total_pages": 15,
  "current_page": 1,
  "results": [
    {
      "id": 1,
      "title": "Senior Python Developer",
      "description": "...",
      "location": "Remote",
      "status": "published",
      "created_at": "2024-12-19T10:00:00Z",
      "company_name": "TechCorp",
      "publisher_name": "John Smith",
      "application_count": 25
    }
  ]
}
```

### Optimized Job Response (includes related data)
```json
{
  "id": 1,
  "title": "Senior Python Developer",
  "description": "We are looking for...",
  "location": "Remote",
  "status": "published",
  "created_at": "2024-12-19T10:00:00Z",
  "company_name": "TechCorp",
  "publisher_name": "John Smith",
  "application_count": 25
}
```