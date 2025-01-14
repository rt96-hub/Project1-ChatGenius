# Authentication Endpoints

All endpoints in this router handle authentication-related operations. They require valid Auth0 Bearer tokens in the Authorization header.

## POST /sync

Synchronizes Auth0 user data with the local database.

### Request
- Headers:
  - `Authorization`: Bearer token (required)
- Body (UserCreate schema):
  ```json
  {
    "auth0_id": "string",
    "email": "string",
    "name": "string",
    "picture": "string"
  }
  ```

### Response
- Status: 200 OK
- Body (User schema):
  ```json
  {
    "id": "integer",
    "auth0_id": "string",
    "email": "string",
    "name": "string",
    "picture": "string",
    "created_at": "datetime",
    "updated_at": "datetime"
  }
  ```

### Error Responses
- 401 Unauthorized: Missing or invalid authorization header
- 403 Forbidden: Token subject doesn't match provided Auth0 ID
- 500 Internal Server Error: Server-side error

## GET /verify

Verifies Auth0 token and returns user data.

### Request
- Headers:
  - `Authorization`: Bearer token (required)

### Response
- Status: 200 OK
- Body:
  ```json
  {
    "valid": true,
    "user": {
      "id": "integer",
      "auth0_id": "string",
      "email": "string",
      "name": "string",
      "picture": "string",
      "created_at": "datetime",
      "updated_at": "datetime"
    }
  }
  ```

### Error Responses
- 401 Unauthorized: Missing or invalid authorization header
- 404 Not Found: User not found in database
- 500 Internal Server Error: Server-side error

## Authentication Details
All endpoints in this router require a valid Auth0 Bearer token in the Authorization header. The token must be in the format:
```
Authorization: Bearer <token>
```

The token is verified using Auth0's verification process and must contain valid claims including a subject ('sub') that matches the user's Auth0 ID. 