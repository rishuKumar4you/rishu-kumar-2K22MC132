# JWT Authentication Guide

## Overview

The Boostly API uses JWT (JSON Web Token) based authentication for secure, stateless user authentication. This guide explains how to use the authentication system.

## Architecture

### Components

1. **auth.py** - Core authentication module with JWT functions
2. **models.py** - User model with password_hash field
3. **schemas.py** - Request/response models for auth endpoints
4. **main.py** - API endpoints with JWT protection

### JWT Token Structure

The JWT token contains the following claims:

```json
{
  "sub": "1",           // Subject (user_id as string)
  "role": "admin",      // User role: "admin" or "user"
  "email": "user@example.com",
  "name": "John Doe",
  "exp": 1763092641,    // Expiration timestamp
  "iat": 1763006241     // Issued at timestamp
}
```

## Security Features

### 1. **Password Hashing**
- Passwords are hashed using bcrypt with automatic salt generation
- Plain text passwords are never stored in the database
- Hash verification is constant-time to prevent timing attacks

### 2. **JWT Token Security**
- Tokens are signed with HS256 algorithm
- Secret key used for signing (configured in auth.py)
- Tokens include expiration time (24 hours by default)
- Token signature is verified on every request

### 3. **Token Verification**
- Validates signature integrity
- Checks expiration time
- Verifies token structure
- Extracts and validates user claims

### 4. **Authorization Levels**
- **User**: Normal authenticated user
- **Admin**: User with ID=1, has access to admin endpoints

## API Endpoints

### 1. Register User

**POST** `/register`

Create a new user account with email and password.

**Request:**
```json
{
  "name": "Alice Smith",
  "email": "alice@example.com",
  "password": "SecurePassword123"
}
```

**Response:**
```json
{
  "id": 1,
  "name": "Alice Smith",
  "email": "alice@example.com",
  "grant_balance": 100,
  "sent_this_month": 0,
  "redeemable_balance": 0,
  "total_received": 0
}
```

**Validation:**
- Name: 1-100 characters, no whitespace-only
- Email: Valid email format
- Password: Minimum 8 characters

### 2. Login

**POST** `/login`

Authenticate and receive JWT access token.

**Request:**
```json
{
  "email": "alice@example.com",
  "password": "SecurePassword123"
}
```

**Response:**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "user_id": 1,
  "name": "Alice Smith",
  "email": "alice@example.com",
  "role": "user"
}
```

**Error Response (401):**
```json
{
  "detail": "Incorrect email or password"
}
```

### 3. Protected Endpoints

All other endpoints require JWT authentication via Bearer token in the Authorization header.

## Usage Examples

### Using curl

```bash
# 1. Register a new user
curl -X POST "http://127.0.0.1:8000/register" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Alice Smith",
    "email": "alice@example.com",
    "password": "SecurePassword123"
  }'

# 2. Login and get JWT token
TOKEN=$(curl -X POST "http://127.0.0.1:8000/login" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "alice@example.com",
    "password": "SecurePassword123"
  }' | jq -r '.access_token')

# 3. Use token for authenticated requests
curl -X POST "http://127.0.0.1:8000/recognize" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{
    "receiver_id": 2,
    "credits": 20,
    "note": "Great work!"
  }'

# 4. Check leaderboard (no auth required)
curl -X GET "http://127.0.0.1:8000/leaderboard?limit=10"

# 5. Admin endpoint (requires admin role)
curl -X GET "http://127.0.0.1:8000/admin/audit-logs?limit=20" \
  -H "Authorization: Bearer $TOKEN"
```

### Using Python requests

```python
import requests

BASE_URL = "http://127.0.0.1:8000"

# 1. Register
response = requests.post(f"{BASE_URL}/register", json={
    "name": "Alice Smith",
    "email": "alice@example.com",
    "password": "SecurePassword123"
})
user = response.json()

# 2. Login
response = requests.post(f"{BASE_URL}/login", json={
    "email": "alice@example.com",
    "password": "SecurePassword123"
})
token_data = response.json()
token = token_data["access_token"]

# 3. Authenticated request
headers = {"Authorization": f"Bearer {token}"}
response = requests.post(
    f"{BASE_URL}/recognize",
    headers=headers,
    json={
        "receiver_id": 2,
        "credits": 20,
        "note": "Great work!"
    }
)
```

### Using JavaScript (fetch)

```javascript
const BASE_URL = "http://127.0.0.1:8000";

// 1. Register
const registerResponse = await fetch(`${BASE_URL}/register`, {
  method: "POST",
  headers: { "Content-Type": "application/json" },
  body: JSON.stringify({
    name: "Alice Smith",
    email: "alice@example.com",
    password: "SecurePassword123"
  })
});
const user = await registerResponse.json();

// 2. Login
const loginResponse = await fetch(`${BASE_URL}/login`, {
  method: "POST",
  headers: { "Content-Type": "application/json" },
  body: JSON.stringify({
    email: "alice@example.com",
    password: "SecurePassword123"
  })
});
const tokenData = await loginResponse.json();
const token = tokenData.access_token;

// 3. Authenticated request
const recognizeResponse = await fetch(`${BASE_URL}/recognize`, {
  method: "POST",
  headers: {
    "Content-Type": "application/json",
    "Authorization": `Bearer ${token}`
  },
  body: JSON.stringify({
    receiver_id: 2,
    credits: 20,
    note: "Great work!"
  })
});
```

## Audit Logging

All authentication events are logged in the audit system:

### Logged Events

1. **create_user** - New user registration
2. **login_success** - Successful authentication
3. **login_failed** - Failed authentication attempt (with reason)

### Login Audit Details

Success:
```json
{
  "email": "alice@example.com",
  "role": "user"
}
```

Failure:
```json
{
  "email": "alice@example.com",
  "reason": "invalid_credentials"
}
```

## Error Handling

### 401 Unauthorized

Returned when:
- Invalid JWT token
- Expired JWT token
- Tampered JWT token
- Missing Authorization header
- Invalid credentials (login)
- User not found

### 403 Forbidden

Returned when:
- Non-admin user tries to access admin endpoints

### 422 Unprocessable Entity

Returned when:
- Invalid request data
- Password too short (< 8 characters)
- Invalid email format
- Missing required fields

## Best Practices

### For Developers

1. **Store tokens securely**
   - Use httpOnly cookies for web apps
   - Never expose tokens in URLs
   - Store in secure storage on mobile apps

2. **Handle token expiration**
   - Tokens expire after 24 hours
   - Implement automatic refresh or re-login
   - Show clear error messages

3. **Secret key management**
   - Use environment variables for SECRET_KEY
   - Never commit secrets to version control
   - Use strong, random keys (32+ characters)

4. **Password requirements**
   - Minimum 8 characters (enforced)
   - Consider requiring complexity
   - Implement rate limiting for login attempts

### For Users

1. **Choose strong passwords**
   - At least 8 characters
   - Mix of letters, numbers, symbols
   - Don't reuse passwords

2. **Protect your token**
   - Don't share your JWT token
   - Logout when done
   - Clear tokens on logout

## Security Configuration

### Secret Key

**Production:** Set via environment variable

```bash
export JWT_SECRET_KEY="your-long-random-secret-key-here"
```

Update `auth.py`:
```python
import os
SECRET_KEY = os.getenv("JWT_SECRET_KEY", "fallback-key-for-dev")
```

### Token Expiration

Change expiration time in `auth.py`:

```python
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24  # 24 hours (current)
ACCESS_TOKEN_EXPIRE_MINUTES = 60       # 1 hour
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24 * 7  # 1 week
```

### Password Requirements

Update validator in `schemas.py`:

```python
@validator('password')
def password_must_be_strong(cls, v):
    if len(v) < 12:  # Increase minimum length
        raise ValueError('Password must be at least 12 characters')
    if not any(c.isupper() for c in v):
        raise ValueError('Password must contain uppercase letter')
    if not any(c.isdigit() for c in v):
        raise ValueError('Password must contain digit')
    return v
```

## Troubleshooting

### Token Verification Fails

**Error:** "Could not validate credentials"

**Solutions:**
1. Check token hasn't expired
2. Verify SECRET_KEY matches on server
3. Ensure token wasn't modified
4. Check Authorization header format: `Bearer <token>`

### User Not Found

**Error:** "User not found"

**Solutions:**
1. User may have been deleted
2. Database may have been reset
3. Token may be from old system

### Invalid Credentials

**Error:** "Incorrect email or password"

**Solutions:**
1. Verify email is correct
2. Check password (case-sensitive)
3. Ensure user is registered
4. Check for typos

## Migration from Old System

If migrating from the old `x-api-user` header system:

1. All existing users need to set passwords
2. Update client code to use `/login` endpoint
3. Store and use JWT tokens
4. Update Authorization header format

## Summary

The JWT authentication system provides:
- ✅ Secure password storage with bcrypt
- ✅ Stateless authentication with JWT
- ✅ Role-based access control
- ✅ Token expiration
- ✅ Comprehensive audit logging
- ✅ Industry-standard security practices

For questions or issues, check the API documentation at `http://127.0.0.1:8000/docs` when the server is running.

