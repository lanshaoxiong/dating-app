# Authentication Module

User authentication service for PupMatch backend with JWT tokens and bcrypt password hashing.

## Features

- User registration with email/password
- Login with JWT token generation
- Token validation middleware
- Password hashing with bcrypt (cost factor 12)
- Password reset flow (placeholder)
- FastAPI route integration

---

## 🔄 Authentication Flow

### Complete Flow: Registration → Login → Protected Endpoint

```
1. REGISTER
   Client: POST /auth/register {"email": "user@example.com", "password": "pass123"}
   ↓
   routes.py: Validates RegisterRequest (email format, password length)
   ↓
   service.py: Checks email doesn't exist in database
   ↓
   service.py: Hashes password with bcrypt (cost factor 12)
   ↓
   database: INSERT INTO users (id, email, password_hash)
   ↓
   Client: 201 {"id": "abc-123", "email": "user@example.com"}

2. LOGIN
   Client: POST /auth/login {"email": "user@example.com", "password": "pass123"}
   ↓
   routes.py: Validates LoginRequest
   ↓
   service.py: Finds user by email in database
   ↓
   service.py: Verifies password against hash using bcrypt
   ↓
   service.py: Creates JWT token (user_id + expiration)
   ↓
   Client: 200 {"access_token": "eyJ...", "expires_in": 86400}

3. PROTECTED ENDPOINT
   Client: GET /some-protected-route
           Authorization: Bearer eyJ...
   ↓
   dependencies.py: Extracts token from Authorization header
   ↓
   service.py: Decodes JWT, validates signature
   ↓
   service.py: Checks token expiration
   ↓
   database: SELECT * FROM users WHERE id = 'abc-123'
   ↓
   endpoint: Executes with authenticated User object
   ↓
   Client: 200 {data}
```

---

## 📁 File Responsibilities

### **`__init__.py`** - Module Interface
**What it does:**
- Exports public API of auth module
- Makes imports cleaner: `from auth import AuthService`

### **`schemas.py`** - Data Validation
**What it does:**
- `RegisterRequest` - Validates email format, password length (8-100 chars)
- `LoginRequest` - Validates login credentials
- `AuthToken` - Formats JWT response (access_token, expires_in)
- `UserResponse` - User data WITHOUT password
- Uses Pydantic for automatic validation

### **`service.py`** - Business Logic
**What it does:**

**`register(email, password)`:**
- Checks if email exists → `UserAlreadyExistsError`
- Hashes password with bcrypt
- Creates user in database
- Returns UserResponse

**`login(email, password)`:**
- Finds user by email → `InvalidCredentialsError` if not found
- Verifies password → `InvalidCredentialsError` if wrong
- Generates JWT token
- Returns AuthToken

**`validate_token(token)`:**
- Decodes JWT → `InvalidTokenError` if invalid
- Checks expiration → `InvalidTokenError` if expired
- Gets user from database → `UserNotFoundError` if missing
- Returns User

**Private methods:**
- `_hash_password()` - Bcrypt hashing (cost factor 12)
- `_verify_password()` - Bcrypt verification
- `_create_access_token()` - JWT generation (HS256)

### **`routes.py`** - HTTP Endpoints
**What it does:**
- `POST /auth/register` - Create new user (201 Created)
- `POST /auth/login` - Get JWT token (200 OK)
- `GET /auth/me` - Get current user info (requires auth)
- `POST /auth/password-reset/request` - Request password reset (204 No Content)

**Why separate from service:**
- Service = reusable business logic
- Routes = HTTP-specific (status codes, headers)
- Service works with GraphQL, CLI, tests

### **`dependencies.py`** - FastAPI Middleware
**What it does:**

**`get_auth_service(db)`:**
- Creates AuthService with database session
- Dependency injection for routes

**`get_current_user(credentials, auth_service)`:**
- Extracts Bearer token from header
- Validates token
- Returns authenticated User
- Raises 401 if invalid

**`require_auth(current_user)`:**
- Alias for `get_current_user`
- Clearer intent in code

**Usage in endpoints:**
```python
@app.get("/protected")
async def protected(user: User = Depends(get_current_user)):
    return {"user_id": user.id}
```

### **`exceptions.py`** - Error Types
**What it does:**
- `InvalidCredentialsError` - Wrong email/password
- `UserAlreadyExistsError` - Email taken
- `InvalidTokenError` - Bad/expired JWT
- `UserNotFoundError` - User doesn't exist

**Why custom exceptions:**
- Clear error types
- Easy to catch specific errors
- Better error messages
- Separates business errors from HTTP errors

---

## 🔐 Security Details

### Password Hashing (Bcrypt)
```python
# Registration
password = "mypassword"
↓
bcrypt.hashpw(password, salt)  # Cost factor 12
↓
"$2b$12$..." (stored in database)

# Login
password = "mypassword"
↓
bcrypt.checkpw(password, stored_hash)
↓
True/False
```

**Why bcrypt:**
- Slow by design (prevents brute force)
- Automatic salt generation
- Cost factor adjustable (12 = ~250ms per hash)
- Industry standard

### JWT Tokens
```python
# Token Creation
payload = {
    "sub": "user-id-123",      # User ID
    "exp": 1735689600,         # Expiration timestamp
    "iat": 1735603200          # Issued at timestamp
}
↓
jwt.encode(payload, SECRET_KEY, algorithm="HS256")
↓
"eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."

# Token Validation
token = "eyJ..."
↓
jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
↓
{"sub": "user-id-123", "exp": 1735689600, "iat": 1735603200}
```

**Why JWT:**
- Stateless (no server-side session storage)
- Scalable (works across multiple servers)
- Self-contained (includes user ID)
- Signed (tamper-proof)

---

## 🔐 Authentication vs Authorization

### Authentication = "Who are you?"
**Verifying identity** - Proving you are who you claim to be.

**In our system:**
```python
# Authentication: Verify the user is logged in
@app.get("/profile")
async def get_profile(current_user: User = Depends(get_current_user)):
    # ✓ User is authenticated (we know WHO they are)
    return {"user_id": current_user.id}
```

**What happens:**
1. User provides token
2. System validates token
3. System confirms: "Yes, you are user-id-123"

### Authorization = "What can you do?"
**Verifying permissions** - Checking if you're allowed to perform an action.

**In our system:**
```python
# Authorization: Check if user can access THIS specific resource
@app.delete("/profile/{profile_id}")
async def delete_profile(
    profile_id: str,
    current_user: User = Depends(get_current_user)  # Authentication
):
    profile = await db.get(Profile, profile_id)
    
    # Authorization: Check ownership
    if profile.user_id != current_user.id:
        raise HTTPException(403, "Not your profile")  # Forbidden
    
    await db.delete(profile)
    return {"deleted": True}
```

**What happens:**
1. User is authenticated (we know who they are)
2. User tries to delete profile X
3. System checks: "Does this user OWN profile X?"
4. If yes → allow, if no → 403 Forbidden

### Real-World Examples

**Authentication:**
```python
# ✓ Are you logged in?
GET /auth/me
Authorization: Bearer eyJ...

# If token valid → 200 OK (authenticated)
# If token invalid → 401 Unauthorized (not authenticated)
```

**Authorization:**
```python
# ✓ Are you logged in? (authentication)
# ✓ Can you access THIS resource? (authorization)
GET /profile/user-456
Authorization: Bearer eyJ...  # Token for user-123

# User-123 is authenticated (valid token)
# But trying to access user-456's profile
# → 403 Forbidden (not authorized)
```

### HTTP Status Codes

- **401 Unauthorized** = Authentication failed (who are you?)
  - No token provided
  - Invalid token
  - Expired token
  
- **403 Forbidden** = Authorization failed (what can you do?)
  - Valid token (authenticated)
  - But not allowed to access this resource
  - Example: Trying to delete someone else's profile

### In Our Auth Module

**What we implement:**
- ✅ **Authentication** - `get_current_user()` verifies WHO you are
- ⚠️ **Authorization** - Each endpoint checks WHAT you can do

**Example:**
```python
# Authentication (in auth module)
current_user = Depends(get_current_user)  # WHO are you?

# Authorization (in each endpoint)
if resource.owner_id != current_user.id:  # WHAT can you do?
    raise HTTPException(403)
```

### Summary

| Concept | Question | Example | Status Code |
|---------|----------|---------|-------------|
| **Authentication** | Who are you? | Login, validate token | 401 Unauthorized |
| **Authorization** | What can you do? | Check ownership, permissions | 403 Forbidden |

**Simple analogy:**
- **Authentication** = Showing your ID at the door (proving who you are)
- **Authorization** = Checking if your ticket allows you into VIP section (what you can access)

---

## 🎯 How to Use Tokens

### Get a Token (Login)

```bash
curl -X POST http://localhost:8000/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email": "user@example.com", "password": "mypassword"}'

# Response:
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "expires_in": 86400
}
```

### Use Token in Requests

```bash
# Include token in Authorization header
curl -X GET http://localhost:8000/auth/me \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
```

### Frontend Usage (React Native)

```javascript
// 1. Login and store token
const login = async (email, password) => {
  const response = await fetch('http://localhost:8000/auth/login', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ email, password })
  });
  
  const data = await response.json();
  
  // Store token in AsyncStorage
  await AsyncStorage.setItem('access_token', data.access_token);
  
  return data;
};

// 2. Use token in subsequent requests
const getProfile = async () => {
  const token = await AsyncStorage.getItem('access_token');
  
  const response = await fetch('http://localhost:8000/profile', {
    headers: {
      'Authorization': `Bearer ${token}`
    }
  });
  
  return response.json();
};

// 3. Handle token expiration
const makeAuthenticatedRequest = async (url, options = {}) => {
  const token = await AsyncStorage.getItem('access_token');
  
  const response = await fetch(url, {
    ...options,
    headers: {
      ...options.headers,
      'Authorization': `Bearer ${token}`
    }
  });
  
  if (response.status === 401) {
    // Token expired, redirect to login
    await AsyncStorage.removeItem('access_token');
    navigation.navigate('Login');
  }
  
  return response.json();
};
```

### Backend Usage (Protect Endpoints)

```python
from fastapi import Depends
from auth.dependencies import get_current_user
from db.models.user import User

# Simple protected endpoint
@app.get("/profile")
async def get_profile(current_user: User = Depends(get_current_user)):
    # current_user is automatically populated from token
    return {
        "user_id": current_user.id,
        "email": current_user.email
    }

# Protect with ownership check
@app.delete("/profile/{profile_id}")
async def delete_profile(
    profile_id: str,
    current_user: User = Depends(get_current_user)
):
    profile = await db.get(Profile, profile_id)
    
    # Ensure user owns this profile
    if profile.user_id != current_user.id:
        raise HTTPException(403, "Not your profile")
    
    await db.delete(profile)
    return {"deleted": True}

# Optional authentication
from typing import Optional

@app.get("/public-or-private")
async def mixed_endpoint(
    current_user: Optional[User] = Depends(get_current_user)
):
    if current_user:
        return {"message": f"Hello {current_user.email}"}
    else:
        return {"message": "Hello guest"}
```

### Token Validation Flow

```
Client Request
    ↓
Authorization: Bearer eyJ...
    ↓
dependencies.py: get_current_user()
    ↓
Extract token from header
    ↓
service.py: validate_token()
    ↓
1. Decode JWT (verify signature)
2. Check expiration
3. Extract user_id from "sub"
4. Query database for user
    ↓
Return User object
    ↓
Endpoint executes with authenticated user
```

### What's Inside the Token

```python
# Decoded JWT payload
{
  "sub": "user-id-123",      # User ID (who you are)
  "exp": 1735689600,         # Expiration (when it expires)
  "iat": 1735603200          # Issued at (when it was created)
}

# The token is signed with SECRET_KEY
# If anyone modifies it, signature verification fails
```

### Token Lifecycle

```
1. User logs in
   ↓
2. Server generates JWT (expires in 24h)
   ↓
3. Client stores token
   ↓
4. Client includes token in every request
   ↓
5. Server validates token on each request
   ↓
6. After 24h, token expires
   ↓
7. Client must login again
```

### Key Points

- **Stateless**: Server doesn't store sessions, just validates signature
- **Self-contained**: Token includes user ID, no database lookup needed for validation
- **Secure**: Signed with SECRET_KEY, cannot be tampered with
- **Expires**: After 24 hours, must login again
- **Bearer scheme**: Standard HTTP authentication (`Authorization: Bearer <token>`)

The token is your "proof of identity" - once you have it, you can access protected endpoints without sending your password again!

---

## 🎯 How Files Work Together

### Registration Example

```python
# 1. Client sends request
POST /auth/register
Body: {"email": "user@example.com", "password": "pass123"}

# 2. routes.py receives it
@router.post("/register")
async def register(request: RegisterRequest, ...):
    # RegisterRequest validates email format, password length
    user = await auth_service.register(request.email, request.password)
    return user

# 3. service.py processes it
async def register(self, email: str, password: str):
    # Check if exists
    existing = await db.query(User).filter_by(email=email).first()
    if existing:
        raise UserAlreadyExistsError()
    
    # Hash password
    hash = bcrypt.hashpw(password.encode(), salt)
    
    # Create user
    user = User(id=uuid4(), email=email, password_hash=hash)
    db.add(user)
    await db.commit()
    
    return UserResponse(id=user.id, email=user.email)

# 4. Client receives response
201 Created
{"id": "abc-123", "email": "user@example.com", "created_at": "..."}
```

### Protected Endpoint Example

```python
# 1. Define protected endpoint
@app.get("/profile")
async def get_profile(user: User = Depends(get_current_user)):
    return {"user_id": user.id, "email": user.email}

# 2. Client sends request with token
GET /profile
Authorization: Bearer eyJ...

# 3. dependencies.py intercepts
async def get_current_user(credentials, auth_service):
    token = credentials.credentials  # Extract "eyJ..."
    user = await auth_service.validate_token(token)
    return user

# 4. service.py validates token
async def validate_token(self, token: str):
    payload = jwt.decode(token, SECRET_KEY)  # Decode JWT
    user_id = payload["sub"]                 # Extract user ID
    
    if payload["exp"] < now():               # Check expiration
        raise InvalidTokenError("Expired")
    
    user = await db.get(User, user_id)       # Get from database
    return user

# 5. Endpoint executes with user
user.id = "abc-123"
user.email = "user@example.com"
```

---

## Structure

```
auth/
├── __init__.py          # Module exports
├── service.py           # AuthService implementation
├── schemas.py           # Pydantic request/response models
├── routes.py            # FastAPI endpoints
├── dependencies.py      # FastAPI dependencies (get_current_user)
├── exceptions.py        # Custom exceptions
└── README.md            # This file
```

## Usage

### Register User

```python
POST /auth/register
{
  "email": "user@example.com",
  "password": "securepassword123"
}

Response: 201 Created
{
  "id": "uuid",
  "email": "user@example.com",
  "created_at": "2024-12-26T..."
}
```

### Login

```python
POST /auth/login
{
  "email": "user@example.com",
  "password": "securepassword123"
}

Response: 200 OK
{
  "access_token": "eyJ...",
  "token_type": "bearer",
  "expires_in": 86400
}
```

### Get Current User

```python
GET /auth/me
Authorization: Bearer eyJ...

Response: 200 OK
{
  "id": "uuid",
  "email": "user@example.com",
  "created_at": "2024-12-26T..."
}
```

### Protected Endpoints

```python
from fastapi import Depends
from auth.dependencies import get_current_user
from db.models.user import User

@app.get("/protected")
async def protected_route(current_user: User = Depends(get_current_user)):
    return {"user_id": current_user.id}
```

## Implementation Details

### Password Hashing

- **Algorithm**: bcrypt
- **Cost Factor**: 12 (configurable, balances security and performance)
- **Salt**: Automatically generated per password
- **Irreversible**: Cannot recover original password from hash

### JWT Tokens

- **Algorithm**: HS256 (HMAC with SHA-256)
- **Expiration**: 24 hours (configurable via `ACCESS_TOKEN_EXPIRE_MINUTES`)
- **Payload**: Contains user ID (`sub`) and expiration (`exp`)
- **Secret**: Configured via `SECRET_KEY` environment variable

### Security

- Passwords never stored in plain text
- Passwords never logged or exposed in responses
- JWT tokens signed with secret key
- Token expiration enforced
- Invalid credentials return generic error (don't reveal if email exists)

## Configuration

Set in `backend/.env`:

```env
SECRET_KEY=your-secret-key-here
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=1440  # 24 hours
```

## Error Handling

### Custom Exceptions

- `InvalidCredentialsError` - Wrong email/password
- `UserAlreadyExistsError` - Email already registered
- `InvalidTokenError` - Invalid or expired JWT
- `UserNotFoundError` - User doesn't exist

### HTTP Status Codes

- `201` - User created successfully
- `200` - Login successful
- `401` - Invalid credentials or token
- `409` - Email already exists
- `404` - User not found

## Testing

See Task 4.3 for property-based tests validating:
- **Property 1**: Authentication Token Validity
- **Property 2**: Password Hash Irreversibility
- **Property 14**: Token Expiration

## Requirements Validated

✅ **Requirement 1.1** - User registration with hashed credentials
✅ **Requirement 1.2** - Login returns authentication token
✅ **Requirement 1.5** - Token validation on protected endpoints
✅ **Requirement 1.6** - Token expiration handling
