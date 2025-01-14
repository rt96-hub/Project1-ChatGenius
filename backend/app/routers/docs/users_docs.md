# User Endpoints

All endpoints in this router require authentication via Bearer token. They handle user-related operations including profile management and user information retrieval.

## Endpoints

### GET /users/me
Get the current authenticated user's information.

#### Request
- Headers:
  - `Authorization`: Bearer token (required)

#### Response
- Status: 200 OK
- Body (User schema):
  ```json
  {
    "id": "integer",
    "auth0_id": "string",
    "email": "string",
    "name": "string",
    "picture": "string",
    "bio": "string",
    "created_at": "datetime",
    "updated_at": "datetime"
  }
  ```

### GET /users/by-last-dm
Get all users ordered by their last DM interaction with the current user.

#### Request
- Headers:
  - `Authorization`: Bearer token (required)
- Query Parameters:
  - `skip`: integer (optional, default: 0)
  - `limit`: integer (optional, default: 100)

#### Response
- Status: 200 OK
- Body: Array of UserWithLastDM objects
  ```json
  [
    {
      "id": "integer",
      "auth0_id": "string",
      "email": "string",
      "name": "string",
      "picture": "string",
      "bio": "string",
      "last_dm_at": "datetime",
      "created_at": "datetime",
      "updated_at": "datetime"
    }
  ]
  ```

### GET /users/
Get list of all users.

#### Request
- Headers:
  - `Authorization`: Bearer token (required)
- Query Parameters:
  - `skip`: integer (optional, default: 0)
  - `limit`: integer (optional, default: 100)

#### Response
- Status: 200 OK
- Body: Array of User objects

### GET /users/{user_id}
Get a specific user's information.

#### Request
- Headers:
  - `Authorization`: Bearer token (required)
- Path Parameters:
  - `user_id`: integer

#### Response
- Status: 200 OK
- Body: User object

### PUT /users/me/bio
Update the current user's bio.

#### Request
- Headers:
  - `Authorization`: Bearer token (required)
- Body (UserBioUpdate schema):
  ```json
  {
    "bio": "string"
  }
  ```

#### Response
- Status: 200 OK
- Body: Updated User object

### PUT /users/me/name
Update the current user's name.

#### Request
- Headers:
  - `Authorization`: Bearer token (required)
- Body (UserNameUpdate schema):
  ```json
  {
    "name": "string"
  }
  ```

#### Response
- Status: 200 OK
- Body: Updated User object

## Error Responses
- 400 Bad Request: Invalid request data
- 401 Unauthorized: Missing or invalid token
- 404 Not Found: User not found
- 500 Internal Server Error: Server-side error 