# API Documentation

> **Surgify Platform REST API** - Comprehensive endpoint documentation

## 📚 API Overview

The Surgify Platform provides a RESTful API for managing medical cases, user authentication, analytics, and system configuration. All endpoints follow REST conventions and return JSON responses.

### Base Information
- **Base URL**: `https://api.surgify-platform.com/v1`
- **Authentication**: JWT Bearer tokens
- **Content Type**: `application/json`
- **Rate Limiting**: 1000 requests/hour per API key
- **API Version**: v1.0.0

## 🚀 Quick Start

### Authentication

```bash
# Login to get access token
curl -X POST "https://api.surgify-platform.com/v1/auth/login" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "doctor@hospital.com",
    "password": "your-password"
  }'

# Response
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "expires_in": 3600,
  "user": {
    "id": 123,
    "email": "doctor@hospital.com",
    "role": "physician"
  }
}
```

### Making Authenticated Requests

```bash
# Use token in Authorization header
curl -X GET "https://api.surgify-platform.com/v1/cases" \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
```

## 📋 Endpoint Categories

### 🔐 Authentication Endpoints
| Endpoint | Method | Description | Auth Required |
|----------|--------|-------------|---------------|
| `/auth/login` | POST | User login | ❌ |
| `/auth/logout` | POST | User logout | ✅ |
| `/auth/refresh` | POST | Refresh access token | ✅ |
| `/auth/register` | POST | User registration | ❌ |
| `/auth/forgot-password` | POST | Password reset request | ❌ |

[📖 Authentication Details →](./authentication.md)

### 🏥 Cases Management
| Endpoint | Method | Description | Auth Required |
|----------|--------|-------------|---------------|
| `/cases` | GET | List all cases | ✅ |
| `/cases` | POST | Create new case | ✅ |
| `/cases/{id}` | GET | Get case details | ✅ |
| `/cases/{id}` | PUT | Update case | ✅ |
| `/cases/{id}` | DELETE | Delete case | ✅ |
| `/cases/{id}/notes` | GET | Get case notes | ✅ |
| `/cases/{id}/notes` | POST | Add case note | ✅ |

[📖 Cases API Details →](./cases.md)

### 👥 User Management
| Endpoint | Method | Description | Auth Required |
|----------|--------|-------------|---------------|
| `/users/profile` | GET | Get user profile | ✅ |
| `/users/profile` | PUT | Update profile | ✅ |
| `/users` | GET | List users (admin) | ✅ |
| `/users/{id}` | GET | Get user details | ✅ |
| `/users/{id}/permissions` | PUT | Update permissions | ✅ |

[📖 Users API Details →](./users.md)

### 📊 Analytics & Reporting
| Endpoint | Method | Description | Auth Required |
|----------|--------|-------------|---------------|
| `/analytics/dashboard` | GET | Dashboard metrics | ✅ |
| `/analytics/cases` | GET | Case analytics | ✅ |
| `/analytics/performance` | GET | System performance | ✅ |
| `/analytics/reports/{type}` | GET | Generate reports | ✅ |

[📖 Analytics API Details →](./analytics.md)

### 🔧 System Configuration
| Endpoint | Method | Description | Auth Required |
|----------|--------|-------------|---------------|
| `/config/domains` | GET | Get medical domains | ✅ |
| `/config/settings` | GET | System settings | ✅ |
| `/config/settings` | PUT | Update settings | ✅ |
| `/health` | GET | System health check | ❌ |

## 📡 Response Format

### Successful Response

```json
{
  "success": true,
  "data": {
    // Response data
  },
  "message": "Operation completed successfully",
  "timestamp": "2025-08-05T10:30:00Z",
  "meta": {
    "version": "1.0.0",
    "request_id": "req_123456789"
  }
}
```

### Error Response

```json
{
  "success": false,
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Invalid input data",
    "details": [
      {
        "field": "email",
        "message": "Invalid email format"
      }
    ]
  },
  "timestamp": "2025-08-05T10:30:00Z",
  "meta": {
    "version": "1.0.0",
    "request_id": "req_123456789"
  }
}
```

### Pagination Response

```json
{
  "success": true,
  "data": [
    // Array of items
  ],
  "pagination": {
    "page": 1,
    "per_page": 20,
    "total": 150,
    "total_pages": 8,
    "has_next": true,
    "has_prev": false
  }
}
```

## 🔒 Authentication & Security

### JWT Token Structure

```json
{
  "header": {
    "alg": "HS256",
    "typ": "JWT"
  },
  "payload": {
    "user_id": 123,
    "email": "doctor@hospital.com",
    "role": "physician",
    "permissions": ["read:cases", "write:cases"],
    "exp": 1691234567,
    "iat": 1691230967
  }
}
```

### Permission Levels

| Role | Permissions | Description |
|------|-------------|-------------|
| **admin** | All permissions | Full system access |
| **physician** | read:cases, write:cases, read:analytics | Clinical user access |
| **nurse** | read:cases, write:notes | Limited clinical access |
| **researcher** | read:cases, read:analytics | Research data access |
| **viewer** | read:cases | Read-only access |

### Security Headers

```http
Authorization: Bearer <jwt_token>
X-API-Key: <api_key>
X-Request-ID: <unique_request_id>
Content-Type: application/json
```

## 📊 Status Codes

### Success Codes
- **200 OK** - Request successful
- **201 Created** - Resource created successfully
- **204 No Content** - Successful request with no response body

### Client Error Codes
- **400 Bad Request** - Invalid request data
- **401 Unauthorized** - Authentication required
- **403 Forbidden** - Insufficient permissions
- **404 Not Found** - Resource not found
- **422 Unprocessable Entity** - Validation errors

### Server Error Codes
- **500 Internal Server Error** - Server error
- **502 Bad Gateway** - Upstream server error
- **503 Service Unavailable** - Service temporarily unavailable

## 🔄 Rate Limiting

### Limits by Plan

| Plan | Requests/Hour | Requests/Day | Burst Limit |
|------|---------------|--------------|-------------|
| **Free** | 100 | 1,000 | 10/minute |
| **Professional** | 1,000 | 10,000 | 50/minute |
| **Enterprise** | 10,000 | 100,000 | 200/minute |

### Rate Limit Headers

```http
X-RateLimit-Limit: 1000
X-RateLimit-Remaining: 999
X-RateLimit-Reset: 1691234567
X-RateLimit-Retry-After: 3600
```

### Rate Limit Response

```json
{
  "success": false,
  "error": {
    "code": "RATE_LIMIT_EXCEEDED",
    "message": "Rate limit exceeded. Try again in 3600 seconds."
  },
  "retry_after": 3600
}
```

## 🌐 Environment Endpoints

### Development
- **Base URL**: `https://dev-api.surgify-platform.com/v1`
- **Documentation**: `https://dev-api.surgify-platform.com/docs`
- **Rate Limits**: Relaxed for testing

### Staging
- **Base URL**: `https://staging-api.surgify-platform.com/v1`
- **Documentation**: `https://staging-api.surgify-platform.com/docs`
- **Rate Limits**: Production-like

### Production
- **Base URL**: `https://api.surgify-platform.com/v1`
- **Documentation**: `https://api.surgify-platform.com/docs`
- **Rate Limits**: Full enforcement

## 📝 Common Patterns

### Filtering & Searching

```bash
# Filter cases by status
GET /cases?status=active&department=oncology

# Search cases
GET /cases?search=gastric&sort=created_at&order=desc

# Pagination
GET /cases?page=2&per_page=50
```

### Batch Operations

```bash
# Bulk update cases
PUT /cases/bulk
{
  "ids": [1, 2, 3],
  "updates": {
    "status": "completed"
  }
}

# Bulk delete
DELETE /cases/bulk
{
  "ids": [1, 2, 3]
}
```

### Partial Updates

```bash
# PATCH for partial updates
PATCH /cases/123
{
  "status": "in_progress",
  "notes": "Updated treatment plan"
}
```

## 🧪 Testing & Development

### API Testing Tools

#### cURL Examples
```bash
# Test authentication
curl -X POST "$API_BASE/auth/login" \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"test123"}'

# Test case creation
curl -X POST "$API_BASE/cases" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d @case_data.json
```

#### Postman Collection
Download our Postman collection: [Surgify API Collection](./postman/surgify-api.json)

#### JavaScript SDK
```javascript
import SurgifyAPI from '@surgify/api-client';

const api = new SurgifyAPI({
  baseURL: 'https://api.surgify-platform.com/v1',
  apiKey: 'your-api-key'
});

// Authenticate
await api.auth.login('doctor@hospital.com', 'password');

// Fetch cases
const cases = await api.cases.list({ status: 'active' });

// Create case
const newCase = await api.cases.create({
  title: 'New Gastric Case',
  patient_id: 123,
  status: 'active'
});
```

### Mock API Server

For development and testing:

```bash
# Install mock server
npm install -g @surgify/mock-api

# Start mock server
surgify-mock-api --port 3001 --data ./mock-data.json

# Mock server runs at http://localhost:3001
```

## 📚 Code Examples

### Python Client

```python
import requests
from surgify_client import SurgifyAPI

# Initialize client
api = SurgifyAPI(
    base_url='https://api.surgify-platform.com/v1',
    api_key='your-api-key'
)

# Authenticate
token = api.auth.login('doctor@hospital.com', 'password')

# Fetch cases
cases = api.cases.list(status='active', limit=50)

# Create case
new_case = api.cases.create({
    'title': 'Gastric Adenocarcinoma Case',
    'patient_id': 123,
    'department': 'oncology',
    'status': 'active'
})

print(f"Created case: {new_case['id']}")
```

### Node.js Client

```javascript
const { SurgifyAPI } = require('@surgify/api-client');

const api = new SurgifyAPI({
  baseURL: 'https://api.surgify-platform.com/v1',
  apiKey: process.env.SURGIFY_API_KEY
});

async function main() {
  try {
    // Authenticate
    await api.auth.login(
      process.env.SURGIFY_EMAIL,
      process.env.SURGIFY_PASSWORD
    );
    
    // Fetch dashboard data
    const dashboard = await api.analytics.dashboard();
    console.log('Dashboard data:', dashboard);
    
    // Create case
    const caseData = {
      title: 'New Case',
      patient_id: 123,
      status: 'active'
    };
    
    const newCase = await api.cases.create(caseData);
    console.log('Created case:', newCase.id);
    
  } catch (error) {
    console.error('API Error:', error.message);
  }
}

main();
```

## 🔍 Debugging & Troubleshooting

### Common Issues

#### Authentication Errors
```json
{
  "error": {
    "code": "INVALID_TOKEN",
    "message": "JWT token is invalid or expired"
  }
}
```

**Solution**: Refresh your token or re-authenticate.

#### Validation Errors
```json
{
  "error": {
    "code": "VALIDATION_ERROR",
    "details": [
      {
        "field": "email",
        "message": "Email is required"
      }
    ]
  }
}
```

**Solution**: Check required fields and data types.

#### Rate Limiting
```json
{
  "error": {
    "code": "RATE_LIMIT_EXCEEDED",
    "message": "Too many requests"
  }
}
```

**Solution**: Implement exponential backoff or upgrade plan.

### Debug Mode

Enable debug logging by adding header:

```bash
curl -X GET "$API_BASE/cases" \
  -H "Authorization: Bearer $TOKEN" \
  -H "X-Debug: true"
```

### API Status Page

Monitor API status: [https://status.surgify-platform.com](https://status.surgify-platform.com)

## 📊 Monitoring & Analytics

### Request Logging

All API requests are logged with:
- Request ID
- User ID
- Endpoint
- Response time
- Status code
- IP address

### Performance Metrics

- **Average Response Time**: < 200ms
- **99th Percentile**: < 500ms
- **Uptime**: 99.9%
- **Error Rate**: < 0.1%

## 🚀 Changelog

### v1.0.0 (Current)
- Initial API release
- Authentication system
- Cases management
- User management
- Analytics endpoints

### Upcoming Features
- **v1.1.0**: WebSocket support for real-time updates
- **v1.2.0**: GraphQL endpoint
- **v1.3.0**: Advanced search capabilities
- **v2.0.0**: API versioning and backwards compatibility

---

## 📞 Support

- **API Issues**: [GitHub Issues](https://github.com/surgify/api/issues)
- **Feature Requests**: [Feature Portal](https://surgify.canny.io)
- **Email Support**: api-support@surgify-platform.com
- **Documentation**: [Interactive API Explorer](https://api.surgify-platform.com/docs)

**Next**: Explore specific endpoint documentation:
- [Authentication →](./authentication.md)
- [Cases API →](./cases.md)
- [Users API →](./users.md)
- [Analytics API →](./analytics.md)
