# Boostly - Peer Recognition & Rewards Platform

A FastAPI-based platform that enables college students to recognize their peers, allocate monthly credits, and redeem earned rewards. The system encourages appreciation and engagement across student communities with a simple, transparent credit-based reward system.

## 🌟 Features

- **User Management** - Register and authenticate users with JWT tokens
- **Peer Recognition** - Send credits to peers with notes
- **Monthly Credit System** - 100 credits/month with carry-forward (max 50)
- **Endorsements** - Endorse recognitions from other users
- **Redemption** - Convert credits to vouchers (5 INR per credit)
- **Leaderboard** - Track top contributors
- **Admin Functions** - Month reset and audit log management
- **Audit Logging** - Complete audit trail of all actions
- **Input Validation** - Comprehensive Pydantic validation
- **JWT Authentication** - Secure token-based authentication

## 📋 Table of Contents

- [Prerequisites](#prerequisites)
- [Installation](#installation)
- [Running the Application](#running-the-application)
- [API Documentation](#api-documentation)
- [Testing Guide](#testing-guide)
- [Project Structure](#project-structure)
- [Technology Stack](#technology-stack)

## 🔧 Prerequisites

- Python 3.10 or higher
- pip (Python package manager)
- curl (for testing)
- jq (optional, for pretty JSON output)

## 📥 Installation

### 1. Clone or Navigate to Project Directory

```bash
cd /home/captainpilot/Desktop/nodeflow/rippling-task
```

### 2. Create Virtual Environment

```bash
python3 -m venv venv
```

### 3. Activate Virtual Environment

```bash
source venv/bin/activate
```

### 4. Install Dependencies

```bash
pip install -r requirements.txt
```

### 5. Verify Installation

```bash
python -c "import fastapi, sqlmodel, jose; print('✓ All dependencies installed successfully')"
```

## 🚀 Running the Application

### 1. Navigate to Source Directory

```bash
cd src
```

### 2. Start the Server

```bash
uvicorn main:app --reload
```

Expected output:
```
INFO:     Will watch for changes in these directories: ['/home/captainpilot/Desktop/nodeflow/rippling-task/src']
INFO:     Uvicorn running on http://127.0.0.1:8000 (Press CTRL+C to quit)
INFO:     Started reloader process [XXXXX] using StatReload
INFO:     Started server process [XXXXX]
INFO:     Waiting for application startup.
INFO:     Application startup complete.
```

### 3. Verify Server is Running

Open another terminal and run:

```bash
curl http://127.0.0.1:8000/docs
```

Or open in browser: http://127.0.0.1:8000/docs

## 📚 API Documentation

### Base URL
```
http://127.0.0.1:8000
```

### Interactive Documentation
- **Swagger UI**: http://127.0.0.1:8000/docs
- **ReDoc**: http://127.0.0.1:8000/redoc

## 🧪 Testing Guide

This section provides comprehensive curl commands to test all features of the application.

### Setup for Testing

Open a new terminal (keep the server running in the first terminal):

```bash
cd /home/captainpilot/Desktop/nodeflow/rippling-task
```

### Test 1: User Registration

#### 1.1 Register First User (Alice - will become admin)

```bash
curl -X POST "http://127.0.0.1:8000/register" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Alice Smith",
    "email": "alice@example.com",
    "password": "SecurePass123"
  }'
```

**Expected Response:**
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

✅ Verify: User ID 1, grant_balance = 100

#### 1.2 Register Second User (Bob)

```bash
curl -X POST "http://127.0.0.1:8000/register" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Bob Johnson",
    "email": "bob@example.com",
    "password": "BobPassword456"
  }'
```

✅ Verify: User ID 2, grant_balance = 100

#### 1.3 Register Third User (Charlie)

```bash
curl -X POST "http://127.0.0.1:8000/register" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Charlie Brown",
    "email": "charlie@example.com",
    "password": "Charlie789"
  }'
```

✅ Verify: User ID 3, grant_balance = 100

#### 1.4 Test Email Validation (Should Fail)

```bash
curl -X POST "http://127.0.0.1:8000/register" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Invalid User",
    "email": "not-an-email",
    "password": "password123"
  }'
```

**Expected:** 422 Unprocessable Entity - Invalid email format

✅ Verify: Error message about email validation

#### 1.5 Test Password Too Short (Should Fail)

```bash
curl -X POST "http://127.0.0.1:8000/register" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Test User",
    "email": "test@example.com",
    "password": "short"
  }'
```

**Expected:** 422 Unprocessable Entity - Password too short

✅ Verify: Error about password length

#### 1.6 Test Duplicate Email (Should Fail)

```bash
curl -X POST "http://127.0.0.1:8000/register" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Duplicate",
    "email": "alice@example.com",
    "password": "password123"
  }'
```

**Expected:** 400 Bad Request - "Email already registered"

✅ Verify: Duplicate email rejected

---

### Test 2: Authentication (Login)

#### 2.1 Login as Alice (Get JWT Token)

```bash
ALICE_TOKEN=$(curl -s -X POST "http://127.0.0.1:8000/login" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "alice@example.com",
    "password": "SecurePass123"
  }' | jq -r '.access_token')

echo "Alice Token: $ALICE_TOKEN"
```

**Expected Response:**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "user_id": 1,
  "name": "Alice Smith",
  "email": "alice@example.com",
  "role": "admin"
}
```

✅ Verify: Token received, role = "admin" (user ID 1)

#### 2.2 Login as Bob

```bash
BOB_TOKEN=$(curl -s -X POST "http://127.0.0.1:8000/login" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "bob@example.com",
    "password": "BobPassword456"
  }' | jq -r '.access_token')

echo "Bob Token: $BOB_TOKEN"
```

✅ Verify: Token received, role = "user"

#### 2.3 Login as Charlie

```bash
CHARLIE_TOKEN=$(curl -s -X POST "http://127.0.0.1:8000/login" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "charlie@example.com",
    "password": "Charlie789"
  }' | jq -r '.access_token')

echo "Charlie Token: $CHARLIE_TOKEN"
```

✅ Verify: Token received

#### 2.4 Test Wrong Password (Should Fail)

```bash
curl -X POST "http://127.0.0.1:8000/login" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "alice@example.com",
    "password": "WrongPassword"
  }'
```

**Expected:** 401 Unauthorized - "Incorrect email or password"

✅ Verify: Authentication failed

#### 2.5 Test Non-existent User (Should Fail)

```bash
curl -X POST "http://127.0.0.1:8000/login" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "nobody@example.com",
    "password": "password123"
  }'
```

**Expected:** 401 Unauthorized

✅ Verify: User not found

---

### Test 3: Recognition (Peer-to-Peer Credits)

#### 3.1 Alice Recognizes Bob (20 Credits)

```bash
curl -X POST "http://127.0.0.1:8000/recognize" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $ALICE_TOKEN" \
  -d '{
    "receiver_id": 2,
    "credits": 20,
    "note": "Great work on the project presentation!"
  }'
```

**Expected Response:**
```json
{
  "status": "ok",
  "recognition_id": 1
}
```

✅ Verify:
- Alice: grant_balance = 80, sent_this_month = 20
- Bob: redeemable_balance = 20, total_received = 20

#### 3.2 Bob Recognizes Charlie (15 Credits)

```bash
curl -X POST "http://127.0.0.1:8000/recognize" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $BOB_TOKEN" \
  -d '{
    "receiver_id": 3,
    "credits": 15,
    "note": "Thanks for helping with debugging"
  }'
```

✅ Verify: recognition_id = 2, Bob sent 15 credits

#### 3.3 Charlie Recognizes Alice (25 Credits)

```bash
curl -X POST "http://127.0.0.1:8000/recognize" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $CHARLIE_TOKEN" \
  -d '{
    "receiver_id": 1,
    "credits": 25,
    "note": "Excellent mentorship!"
  }'
```

✅ Verify: recognition_id = 3, Alice receives 25 credits

#### 3.4 Test Self-Recognition (Should Fail)

```bash
curl -X POST "http://127.0.0.1:8000/recognize" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $ALICE_TOKEN" \
  -d '{
    "receiver_id": 1,
    "credits": 10,
    "note": "Testing self"
  }'
```

**Expected:** 400 Bad Request - "Cannot send credits to yourself"

✅ Verify: Self-recognition blocked

#### 3.5 Test Zero Credits (Should Fail)

```bash
curl -X POST "http://127.0.0.1:8000/recognize" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $ALICE_TOKEN" \
  -d '{
    "receiver_id": 2,
    "credits": 0,
    "note": "Testing"
  }'
```

**Expected:** 422 Unprocessable Entity - Credits must be > 0

✅ Verify: Validation error

#### 3.6 Test Credits > 100 (Should Fail)

```bash
curl -X POST "http://127.0.0.1:8000/recognize" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $ALICE_TOKEN" \
  -d '{
    "receiver_id": 2,
    "credits": 101,
    "note": "Too many"
  }'
```

**Expected:** 422 Unprocessable Entity - Credits must be <= 100

✅ Verify: Validation error

#### 3.7 Test Monthly Limit

```bash
# Alice sends 60 more credits (already sent 20, total will be 80)
curl -X POST "http://127.0.0.1:8000/recognize" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $ALICE_TOKEN" \
  -d '{
    "receiver_id": 3,
    "credits": 60,
    "note": "More recognition"
  }'

# Try to send 21 more (should fail - exceeds 100/month)
curl -X POST "http://127.0.0.1:8000/recognize" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $ALICE_TOKEN" \
  -d '{
    "receiver_id": 2,
    "credits": 21,
    "note": "This should fail"
  }'
```

**Expected:** 400 Bad Request - "Monthly sending limit exceeded"

✅ Verify: Monthly limit enforced (100 credits max)

#### 3.8 Test Non-existent Receiver (Should Fail)

```bash
curl -X POST "http://127.0.0.1:8000/recognize" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $BOB_TOKEN" \
  -d '{
    "receiver_id": 999,
    "credits": 10,
    "note": "Ghost user"
  }'
```

**Expected:** 404 Not Found - "Receiver not found"

✅ Verify: Invalid receiver rejected

#### 3.9 Test Without Authentication (Should Fail)

```bash
curl -X POST "http://127.0.0.1:8000/recognize" \
  -H "Content-Type: application/json" \
  -d '{
    "receiver_id": 2,
    "credits": 10,
    "note": "No auth"
  }'
```

**Expected:** 403 Forbidden - Missing authorization

✅ Verify: Authentication required

---

### Test 4: Endorsements

#### 4.1 Charlie Endorses Recognition 1

```bash
curl -X POST "http://127.0.0.1:8000/recognitions/1/endorse" \
  -H "Authorization: Bearer $CHARLIE_TOKEN"
```

**Expected Response:**
```json
{
  "status": "ok"
}
```

✅ Verify: Endorsement successful

#### 4.2 Bob Endorses Recognition 3

```bash
curl -X POST "http://127.0.0.1:8000/recognitions/3/endorse" \
  -H "Authorization: Bearer $BOB_TOKEN"
```

✅ Verify: Endorsement successful

#### 4.3 Test Duplicate Endorsement (Should Fail)

```bash
curl -X POST "http://127.0.0.1:8000/recognitions/1/endorse" \
  -H "Authorization: Bearer $CHARLIE_TOKEN"
```

**Expected:** 400 Bad Request - "Already endorsed"

✅ Verify: Duplicate endorsement blocked

#### 4.4 Test Invalid Recognition ID (Should Fail)

```bash
curl -X POST "http://127.0.0.1:8000/recognitions/999/endorse" \
  -H "Authorization: Bearer $CHARLIE_TOKEN"
```

**Expected:** 404 Not Found - "Recognition not found"

✅ Verify: Invalid recognition rejected

---

### Test 5: Redemption

#### 5.1 Bob Redeems 10 Credits

```bash
curl -X POST "http://127.0.0.1:8000/redeem" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $BOB_TOKEN" \
  -d '{
    "credits": 10
  }'
```

**Expected Response:**
```json
{
  "status": "ok",
  "voucher_inr": 50
}
```

✅ Verify:
- Voucher value: 50 INR (10 × 5)
- Bob's redeemable_balance reduced by 10

#### 5.2 Charlie Redeems 20 Credits

```bash
curl -X POST "http://127.0.0.1:8000/redeem" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $CHARLIE_TOKEN" \
  -d '{
    "credits": 20
  }'
```

**Expected:** voucher_inr = 100 (20 × 5)

✅ Verify: Credits converted correctly

#### 5.3 Test Insufficient Balance (Should Fail)

```bash
curl -X POST "http://127.0.0.1:8000/redeem" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $BOB_TOKEN" \
  -d '{
    "credits": 100
  }'
```

**Expected:** 400 Bad Request - "Insufficient redeemable balance"

✅ Verify: Balance check working

#### 5.4 Test Zero Credits (Should Fail)

```bash
curl -X POST "http://127.0.0.1:8000/redeem" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $BOB_TOKEN" \
  -d '{
    "credits": 0
  }'
```

**Expected:** 422 Unprocessable Entity - Credits must be > 0

✅ Verify: Validation error

---

### Test 6: Leaderboard

#### 6.1 Get Top 10 Users

```bash
curl -X GET "http://127.0.0.1:8000/leaderboard?limit=10"
```

**Expected Response:**
```json
[
  {
    "id": 3,
    "name": "Charlie Brown",
    "total_received": 75,
    "recognition_count": 2,
    "endorsement_total": 0
  },
  {
    "id": 1,
    "name": "Alice Smith",
    "total_received": 25,
    "recognition_count": 1,
    "endorsement_total": 1
  },
  {
    "id": 2,
    "name": "Bob Johnson",
    "total_received": 20,
    "recognition_count": 1,
    "endorsement_total": 1
  }
]
```

✅ Verify:
- Users sorted by total_received (descending)
- Recognition counts correct
- Endorsement totals correct

#### 6.2 Get Top 2 Users

```bash
curl -X GET "http://127.0.0.1:8000/leaderboard?limit=2"
```

✅ Verify: Only 2 users returned

#### 6.3 Test Invalid Limit (Should Fail)

```bash
curl -X GET "http://127.0.0.1:8000/leaderboard?limit=0"
```

**Expected:** 422 Unprocessable Entity - Limit must be > 0

✅ Verify: Validation error

---

### Test 7: Admin Functions - Month Reset

#### 7.1 Reset Month (Admin Only)

```bash
curl -X POST "http://127.0.0.1:8000/admin/reset_month" \
  -H "Authorization: Bearer $ALICE_TOKEN"
```

**Expected Response:**
```json
{
  "status": "ok",
  "users_reset": 3
}
```

✅ Verify:
- All users: grant_balance reset to 100 + carry_forward (max 50)
- All users: sent_this_month = 0
- Alice had 20 remaining → gets 100 + 20 = 120
- Bob had 85 remaining → gets 100 + 50 = 150 (capped at 50)
- Charlie had 15 remaining → gets 100 + 15 = 115

#### 7.2 Test Non-Admin Access (Should Fail)

```bash
curl -X POST "http://127.0.0.1:8000/admin/reset_month" \
  -H "Authorization: Bearer $BOB_TOKEN"
```

**Expected:** 403 Forbidden - "Admin access required"

✅ Verify: Admin check working

#### 7.3 Reset Again (Should Skip Already Reset)

```bash
curl -X POST "http://127.0.0.1:8000/admin/reset_month" \
  -H "Authorization: Bearer $ALICE_TOKEN"
```

**Expected:** users_reset = 0 (already reset this month)

✅ Verify: Duplicate reset prevention

---

### Test 8: Admin Functions - Audit Logs

#### 8.1 Get All Recent Audit Logs

```bash
curl -X GET "http://127.0.0.1:8000/admin/audit-logs?limit=20" \
  -H "Authorization: Bearer $ALICE_TOKEN" | jq
```

**Expected:** Array of audit log entries with timestamps, actions, details

✅ Verify:
- create_user events (3)
- login_success events (3)
- recognize events (4)
- endorse events (2)
- redeem events (2)
- reset_month event (1)

#### 8.2 Filter by Action (Recognize)

```bash
curl -X GET "http://127.0.0.1:8000/admin/audit-logs?action=recognize&limit=50" \
  -H "Authorization: Bearer $ALICE_TOKEN" | jq
```

✅ Verify: Only recognition actions returned

#### 8.3 Filter by User ID

```bash
curl -X GET "http://127.0.0.1:8000/admin/audit-logs?user_id=1&limit=100" \
  -H "Authorization: Bearer $ALICE_TOKEN" | jq
```

✅ Verify: Only Alice's actions returned

#### 8.4 Filter by Entity Type

```bash
curl -X GET "http://127.0.0.1:8000/admin/audit-logs?entity_type=recognition" \
  -H "Authorization: Bearer $ALICE_TOKEN" | jq
```

✅ Verify: Only recognition-related logs

#### 8.5 Multiple Filters

```bash
curl -X GET "http://127.0.0.1:8000/admin/audit-logs?action=recognize&user_id=1" \
  -H "Authorization: Bearer $ALICE_TOKEN" | jq
```

✅ Verify: Only recognitions by Alice

#### 8.6 Test Non-Admin Access (Should Fail)

```bash
curl -X GET "http://127.0.0.1:8000/admin/audit-logs" \
  -H "Authorization: Bearer $BOB_TOKEN"
```

**Expected:** 403 Forbidden - "Admin access required"

✅ Verify: Admin-only access enforced

---

### Test 9: Integration Test - Complete User Journey

#### 9.1 Create New User (Diana)

```bash
curl -X POST "http://127.0.0.1:8000/register" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Diana Prince",
    "email": "diana@example.com",
    "password": "Diana2024Pass"
  }'
```

#### 9.2 Diana Logs In

```bash
DIANA_TOKEN=$(curl -s -X POST "http://127.0.0.1:8000/login" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "diana@example.com",
    "password": "Diana2024Pass"
  }' | jq -r '.access_token')
```

#### 9.3 Bob Recognizes Diana

```bash
curl -X POST "http://127.0.0.1:8000/recognize" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $BOB_TOKEN" \
  -d '{
    "receiver_id": 4,
    "credits": 30,
    "note": "Welcome to the team! Great first contribution."
  }'
```

#### 9.4 Diana Redeems Credits

```bash
curl -X POST "http://127.0.0.1:8000/redeem" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $DIANA_TOKEN" \
  -d '{
    "credits": 20
  }'
```

#### 9.5 Check Updated Leaderboard

```bash
curl -X GET "http://127.0.0.1:8000/leaderboard?limit=10" | jq
```

✅ Verify: Diana appears in leaderboard with 30 total_received

#### 9.6 Check Diana's Audit Trail

```bash
curl -X GET "http://127.0.0.1:8000/admin/audit-logs?user_id=4" \
  -H "Authorization: Bearer $ALICE_TOKEN" | jq
```

✅ Verify: All Diana's actions logged (create_user, login_success, redeem)

---

## 📊 Test Summary Checklist

After running all tests, verify:

### User Management
- ✅ User registration with validation
- ✅ Password hashing
- ✅ Email uniqueness
- ✅ Password strength requirements

### Authentication
- ✅ JWT token generation
- ✅ Login with email/password
- ✅ Token-based authorization
- ✅ Role-based access control
- ✅ Failed login attempt logging

### Recognition
- ✅ Peer-to-peer credit transfer
- ✅ Balance deduction/addition
- ✅ Monthly sending limit (100 credits)
- ✅ Self-recognition prevention
- ✅ Receiver validation
- ✅ Credit amount validation

### Endorsement
- ✅ Endorse recognitions
- ✅ Duplicate endorsement prevention
- ✅ Recognition ID validation

### Redemption
- ✅ Convert credits to vouchers (5 INR/credit)
- ✅ Balance deduction
- ✅ Insufficient balance handling

### Leaderboard
- ✅ Sorted by total_received
- ✅ Recognition count
- ✅ Endorsement count
- ✅ Pagination

### Admin Functions
- ✅ Month reset with carry-forward
- ✅ Admin-only access
- ✅ Duplicate reset prevention
- ✅ Audit log retrieval with filters

### Audit Logging
- ✅ All actions logged
- ✅ IP address capture
- ✅ Detailed context in JSON
- ✅ Filtering capabilities

### Security
- ✅ JWT signature verification
- ✅ Token expiration
- ✅ Password hashing (bcrypt)
- ✅ Authentication required
- ✅ Authorization enforcement

---

## 📁 Project Structure

```
rippling-task/
├── src/
│   ├── main.py           # FastAPI app & endpoints
│   ├── models.py         # SQLModel database models
│   ├── schemas.py        # Pydantic request/response schemas
│   ├── auth.py           # JWT authentication & authorization
│   ├── audit.py          # Audit logging helpers
│   ├── db.py             # Database connection & session
│   └── boostly.db        # SQLite database (auto-created)
├── test-cases/
│   └── test-cases.txt    # Comprehensive test cases
├── requirements.txt      # Python dependencies
├── README.md             # This file
├── JWT-AUTHENTICATION.md # JWT auth documentation
└── .gitignore           # Git ignore rules
```

## 🛠 Technology Stack

- **Framework**: FastAPI 0.100+
- **Database ORM**: SQLModel (Pydantic + SQLAlchemy)
- **Database**: SQLite (local, zero setup)
- **Authentication**: JWT (python-jose)
- **Password Hashing**: bcrypt (passlib)
- **Validation**: Pydantic
- **Server**: Uvicorn (ASGI)

## 📝 Key Endpoints

### Public Endpoints
- `POST /register` - Register new user
- `POST /login` - Login and get JWT token
- `GET /leaderboard` - View leaderboard

### Authenticated Endpoints (Require JWT Token)
- `POST /recognize` - Send credits to peer
- `POST /recognitions/{id}/endorse` - Endorse recognition
- `POST /redeem` - Redeem credits for vouchers

### Admin Endpoints (Require Admin Role)
- `POST /admin/reset_month` - Reset monthly credits
- `GET /admin/audit-logs` - View audit logs

## 🔒 Security Features

1. **JWT Authentication**
   - HS256 algorithm
   - 24-hour token expiration
   - Signature verification

2. **Password Security**
   - Bcrypt hashing
   - Minimum 8 characters
   - Never stored in plain text

3. **Authorization**
   - Role-based access control
   - Admin-only endpoints
   - Token-based permissions

4. **Audit Trail**
   - All actions logged
   - IP address tracking
   - Failed login attempts

5. **Input Validation**
   - Pydantic models
   - Email format validation
   - Credit amount limits
   - SQL injection protection

## 🐛 Troubleshooting

### Server Won't Start

**Error**: `Address already in use`

**Solution**:
```bash
# Kill existing process
lsof -ti:8000 | xargs kill -9

# Or use different port
uvicorn main:app --reload --port 8001
```

### Database Issues

**Error**: Database locked or corrupted

**Solution**:
```bash
# Remove database and restart
rm src/boostly.db
# Restart server to recreate
```

### Authentication Fails

**Error**: "Could not validate credentials"

**Solution**:
1. Check token hasn't expired (24 hours)
2. Verify Authorization header format: `Bearer <token>`
3. Ensure token wasn't modified
4. Try logging in again to get fresh token

### jq Command Not Found

**Error**: `jq: command not found`

**Solution**:
```bash
# Install jq
sudo apt-get install jq   # Ubuntu/Debian
brew install jq           # macOS
```

**Or**: Remove `| jq` from commands and read raw JSON

## 📚 Additional Resources

- **API Documentation**: http://127.0.0.1:8000/docs (when server running)
- **JWT Authentication Guide**: See `JWT-AUTHENTICATION.md`
- **Comprehensive Test Cases**: See `test-cases/test-cases.txt`

## 🤝 API Usage Best Practices

1. **Store JWT tokens securely**
   - Don't expose in URLs
   - Use httpOnly cookies for web apps
   - Clear on logout

2. **Handle token expiration**
   - Tokens expire after 24 hours
   - Implement automatic re-login
   - Show clear error messages

3. **Rate limiting** (consider implementing)
   - Limit login attempts
   - Throttle API requests
   - Prevent abuse

4. **Error handling**
   - Check response status codes
   - Parse error messages
   - Implement retry logic

## 🎯 Business Logic Summary

### Credit System
- **Monthly Grant**: 100 credits per user
- **Carry Forward**: Unused credits (max 50)
- **Sending Limit**: 100 credits per month
- **Redemption Rate**: 5 INR per credit

### User Roles
- **User (ID > 1)**: Normal permissions
- **Admin (ID = 1)**: Can reset month, view audit logs

### Recognition Flow
1. Sender must have sufficient grant_balance
2. Credits deducted from sender's grant_balance
3. Sender's sent_this_month incremented
4. Credits added to receiver's redeemable_balance
5. Receiver's total_received incremented
6. All changes atomic (database transaction)

## 📞 Support

For issues or questions:
1. Check server logs for detailed errors
2. Review API documentation at `/docs`
3. Verify all test cases pass
4. Check audit logs for system events

## 🎉 Success Criteria

Your application is working correctly if:
- ✅ All test commands complete successfully
- ✅ Server starts without errors
- ✅ JWT authentication works
- ✅ Users can register and login
- ✅ Credits transfer correctly
- ✅ Leaderboard displays properly
- ✅ Admin functions work
- ✅ Audit logs capture all actions

**Congratulations! Your Boostly application is ready to use! 🚀**

