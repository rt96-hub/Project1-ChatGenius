# API Documentation

## Authentication
All endpoints except WebSocket connections require a valid JWT token in the Authorization header:
```
Authorization: Bearer <token>
```

## User Management

### Get Current User
**Endpoint**: `GET /users/me`
**Description**: Get the current authenticated user's profile.

**Response**:
```json
{
    "id": 1,
    "email": "user@example.com",
  "name": "John Doe",
  "picture": "https://example.com/avatar.jpg",
  "bio": "User biography",
    "is_active": true,
  "created_at": "2024-03-15T12:34:56.789Z"
}
```

## Channel Management

### Create Channel
**Endpoint**: `POST /channels`
**Description**: Create a new channel.

**Request Body**:
```json
{
    "name": "general",
  "description": "General discussion",
    "is_private": false
}
```

**Response**: Channel object

### Get Channel
**Endpoint**: `GET /channels/{channel_id}`
**Description**: Get channel details.

**Response**: Channel object with members

### Join Channel
**Endpoint**: `POST /channels/{channel_id}/join`
**Description**: Join a public channel.

**Response**: Channel object

## Message Management

### Create Message
**Endpoint**: `POST /channels/{channel_id}/messages`
**Description**: Create a new message in a channel.

**Request Body**:
```json
{
    "content": "Hello, world!"
}
```

**Response**: Message object

### Get Channel Messages
**Endpoint**: `GET /channels/{channel_id}/messages`
**Description**: Get messages in a channel.

**Query Parameters**:
- `limit`: Maximum number of messages (default: 50)
- `before`: Get messages before this timestamp
- `after`: Get messages after this timestamp

**Response**: Array of Message objects

## File Management

### Upload File
**Endpoint**: `POST /files/upload`
**Description**: Upload a file to be attached to a message.

**Request**:
- Content-Type: `multipart/form-data`
- Body:
  - `file`: File to upload (required)
  - `message_id`: Integer - ID of the message to attach the file to (required)

**Response**:
```json
{
    "id": 1,
  "message_id": 123,
  "file_name": "example.pdf",
  "content_type": "application/pdf",
  "file_size": 1024567,
  "s3_key": "messages/123/20240315-123456-abcd1234.pdf",
  "uploaded_at": "2024-03-15T12:34:56.789Z",
  "uploaded_by": 456,
  "is_deleted": false
}
```

**Error Responses**:
- `400 Bad Request`: Invalid file type or size
- `403 Forbidden`: User not authorized to upload to this message
- `404 Not Found`: Message not found
- `500 Internal Server Error`: S3 upload failed

### Get Download URL
**Endpoint**: `GET /files/{file_id}/download-url`
**Description**: Get a presigned URL for downloading a file.

**Response**:
```json
{
  "download_url": "https://s3.amazonaws.com/...",
  "expires_at": "2024-03-15T13:34:56.789Z"
}
```

**Error Responses**:
- `403 Forbidden`: User not authorized to access this file
- `404 Not Found`: File not found
- `500 Internal Server Error`: Failed to generate presigned URL

### Delete File
**Endpoint**: `DELETE /files/{file_id}`
**Description**: Soft delete a file upload.

**Response**:
```json
{
  "message": "File deleted successfully"
}
```

**Error Responses**:
- `403 Forbidden`: User not authorized to delete this file
- `404 Not Found`: File not found
- `500 Internal Server Error`: Failed to delete file

## WebSocket Events

### Connection
Connect to the WebSocket endpoint with:
```
ws://localhost:8000/ws?token=<jwt_token>
```

### Message Events

#### New Message
```json
{
    "type": "new_message",
  "channel_id": 123,
    "message": {
        "id": 1,
        "content": "Hello, world!",
    "created_at": "2024-03-15T12:34:56.789Z",
    "user_id": 456,
    "channel_id": 123,
        "user": {
      "id": 456,
            "email": "user@example.com",
      "name": "John Doe"
    }
    }
}
```

### Channel Events

#### Member Joined
```json
{
    "type": "member_joined",
  "channel_id": 123,
    "user": {
    "id": 456,
        "email": "user@example.com",
    "name": "John Doe",
    "picture": "https://example.com/avatar.jpg"
    }
}
```

### File Events

#### File Upload
```json
{
  "type": "file_upload",
  "channel_id": 123,
  "file": {
        "id": 1,
    "message_id": 456,
    "file_name": "example.pdf",
    "content_type": "application/pdf",
    "file_size": 1024567,
    "uploaded_at": "2024-03-15T12:34:56.789Z",
    "uploaded_by": 789
  },
  "message": {
    "id": 456,
    "content": "File attachment",
    "user_id": 789,
    "channel_id": 123,
    "created_at": "2024-03-15T12:34:56.789Z"
  }
}
```

#### File Deleted
```json
{
  "type": "file_deleted",
  "channel_id": 123,
  "file_id": 1,
  "message_id": 456
}
```

## Environment Variables

### Server Configuration
- `ROOT_PATH`: Root path for the API (optional)
- `PORT`: Server port (default: 8000)

### Database Configuration
- `DB_URL`: PostgreSQL database URL

### Auth0 Configuration
- `AUTH0_DOMAIN`: Auth0 domain
- `AUTH0_API_IDENTIFIER`: Auth0 API identifier

### WebSocket Configuration
- `MAX_WEBSOCKET_CONNECTIONS_PER_USER`: Maximum WebSocket connections per user (default: 5)
- `MAX_TOTAL_WEBSOCKET_CONNECTIONS`: Maximum total WebSocket connections (default: 1000)

### File Storage Configuration
- `AWS_ACCESS_KEY_ID`: AWS access key for S3 access
- `AWS_SECRET_ACCESS_KEY`: AWS secret key for S3 access
- `AWS_S3_BUCKET_NAME`: S3 bucket name for file storage
- `AWS_S3_REGION`: AWS region for S3 (default: us-east-1)
- `MAX_FILE_SIZE_MB`: Maximum file size in MB (default: 50)
- `ALLOWED_FILE_TYPES`: Comma-separated list of allowed MIME types (default: "image/*,application/pdf,text/*") 