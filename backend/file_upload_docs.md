# File Upload API Documentation

## Overview
The File Upload API provides endpoints for uploading, downloading, and managing files attached to messages in channels. Files are stored in AWS S3 with appropriate access controls.

## Authentication
All endpoints require a valid JWT token in the Authorization header:
```
Authorization: Bearer <token>
```

## File Upload Configurations
- Maximum file size: 50MB (configurable via `MAX_FILE_SIZE_MB`)
- Allowed file types (configurable via `ALLOWED_FILE_TYPES`):
  - Images (`image/*`)
  - PDFs (`application/pdf`)
  - Text files (`text/*`)

## Endpoints

### Upload File
**Endpoint**: `POST /files/upload`  
**Description**: Upload a file and attach it to a message.

**Request**:
- Content-Type: `multipart/form-data`
- Body:
  - `file`: File to upload (required)
  - `message_id`: Integer - ID of the message to attach the file to (required)

**Response**: FileUpload object
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
**Description**: Generate a presigned URL for downloading a file.

**Response**:
```json
{
    "download_url": "https://s3.amazonaws.com/bucket/key?AWSAccessKeyId=..."
}
```

**Notes**:
- URL expires in 1 hour
- File name is preserved in Content-Disposition header

**Error Responses**:
- `403 Forbidden`: User not authorized to access this file
- `404 Not Found`: File not found
- `500 Internal Server Error`: Failed to generate presigned URL

### Delete File
**Endpoint**: `DELETE /files/{file_id}`  
**Description**: Soft delete a file upload. Only the file uploader or message author can delete the file.

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

### Search Files
**Endpoint**: `GET /search/files`  
**Description**: Search for files by name or associated message content.

**Query Parameters**:
- `query`: Search query string (required)
- `channel_id`: Filter by channel ID (optional)
- `file_type`: Filter by file type (optional)
- `from_date`: Filter by upload date range start (optional)
- `to_date`: Filter by upload date range end (optional)
- `uploaded_by`: Filter by uploader user ID (optional)
- `skip`: Number of results to skip (default: 0)
- `limit`: Maximum number of results to return (default: 50)
- `sort_by`: Field to sort by (default: "uploaded_at")
- `sort_order`: Sort order "asc" or "desc" (default: "desc")

**Response**:
```json
{
    "total": 100,
    "items": [
        {
            "id": 1,
            "message_id": 123,
            "file_name": "example.pdf",
            "content_type": "application/pdf",
            "file_size": 1024567,
            "s3_key": "messages/123/20240315-123456-abcd1234.pdf",
            "uploaded_at": "2024-03-15T12:34:56.789Z",
            "uploaded_by": 456,
            "is_deleted": false,
            "channel_id": 789,
            "message_content": "Check out this document"
        }
    ]
}
```

**Error Responses**:
- `400 Bad Request`: Invalid date range
- `403 Forbidden`: Not authorized to search in specified channel
- `500 Internal Server Error`: Search failed

## WebSocket Events

### File Upload Event
Sent when a file is uploaded successfully:
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

### File Deleted Event
Sent when a file is deleted:
```json
{
    "type": "file_deleted",
    "channel_id": 123,
    "file_id": 1,
    "message_id": 456
}
```

## Environment Variables

### AWS Configuration
- `AWS_ACCESS_KEY_ID`: AWS access key for S3 access
- `AWS_SECRET_ACCESS_KEY`: AWS secret key for S3 access
- `AWS_S3_BUCKET_NAME`: S3 bucket name for file storage
- `AWS_S3_REGION`: AWS region for S3 (default: us-east-2)

### File Upload Configuration
- `MAX_FILE_SIZE_MB`: Maximum file size in MB (default: 50)
- `ALLOWED_FILE_TYPES`: Comma-separated list of allowed MIME types (default: "image/*,application/pdf,text/*") 