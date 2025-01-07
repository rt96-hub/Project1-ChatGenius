# Backend Authentication Requirements

## Auth0 Integration

The frontend is configured to use Auth0 for authentication. The backend needs to handle Auth0's JWT tokens and provide two main endpoints for authentication flow.

## Required Endpoints

### 1. POST /auth/sync
This endpoint is called when a user successfully authenticates with Auth0.

**Request:**
```json
{
  "email": "user@example.com",
  "auth0_id": "auth0|123456789",
  "name": "User Name"
}
```

**Headers:**
```
Authorization: Bearer <auth0_jwt_token>
```

**Expected Response (200 OK):**
```json
{
  "id": 1,
  "email": "user@example.com",
  "name": "User Name"
}
```

**Purpose:**
- Sync Auth0 user data with the local database
- Create a new user record if it doesn't exist
- Update existing user information if the user already exists
- Return the user's database record

### 2. GET /auth/verify
This endpoint verifies that the Auth0 token is valid and the user has access.

**Headers:**
```
Authorization: Bearer <auth0_jwt_token>
```

**Expected Response (200 OK):**
```json
{
  "valid": true,
  "user": {
    "id": 1,
    "email": "user@example.com",
    "name": "User Name"
  }
}
```

**Purpose:**
- Validate the Auth0 JWT token
- Confirm the user exists in the local database
- Return the user's information if valid

## Token Validation Requirements

The backend should validate Auth0 tokens with the following checks:

1. Token format is valid JWT
2. Token signature is valid (using Auth0 public key)
3. Token is not expired
4. Token issuer matches Auth0 domain
5. Token audience matches the API identifier

## Error Responses

### Unauthorized (401)
When token is invalid, expired, or missing:
```json
{
  "error": "unauthorized",
  "message": "Invalid or expired token"
}
```

### Not Found (404)
When user doesn't exist in database:
```json
{
  "error": "not_found",
  "message": "User not found"
}
```

### Bad Request (400)
When request body is invalid:
```json
{
  "error": "bad_request",
  "message": "Invalid request body"
}
```

## Database Schema Updates

The users table should include:
```sql
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL,
    name VARCHAR(255),
    auth0_id VARCHAR(255) UNIQUE NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);
```

## Implementation Notes

1. All protected routes should verify the Auth0 token before processing requests
2. The Auth0 token should be used to identify the user for all authenticated requests
3. The backend should maintain the mapping between Auth0 IDs and local user IDs
4. User sessions should be managed entirely through Auth0 tokens
5. The backend should not create or manage its own JWT tokens

## Migration Changes Required

### Files to Remove or Significantly Modify
1. **security.py**
   - Remove password hashing functions
   - Remove JWT token creation
   - Replace token validation with Auth0 token validation
   - Update get_current_user to use Auth0 token validation

### Files to Update
1. **main.py**
   - Remove /token endpoint (Auth0 handles login)
   - Remove /register endpoint (Auth0 handles registration)
   - Add new /auth/sync and /auth/verify endpoints
   - Update WebSocket authentication to use Auth0 tokens
   - Update CORS settings to allow Auth0 domain

2. **models.py**
   - Remove password-related fields from User model
   - Add auth0_id field to User model
   - Add name and picture fields from Auth0 profile

3. **schemas.py**
   - Remove password-related schemas
   - Update UserCreate schema to accept Auth0 fields
   - Remove Token and TokenData schemas
   - Add Auth0 sync and verify response schemas

4. **crud.py**
   - Remove password-related functions (create_user, authenticate_user)
   - Add functions for Auth0 user sync
   - Add function to get user by auth0_id
   - Update user creation/update logic for Auth0

### Files to Create
1. **auth0.py**
   - Auth0 token validation utilities
   - Auth0 public key fetching and caching
   - Token verification middleware

### Environment Variables to Add
1. AUTH0_DOMAIN
2. AUTH0_API_IDENTIFIER
3. AUTH0_CLIENT_ID
4. AUTH0_CLIENT_SECRET

### Database Migrations Needed
1. Remove password-related columns
2. Add auth0_id column
3. Add name column
4. Add picture column
5. Update existing user records (if any) 