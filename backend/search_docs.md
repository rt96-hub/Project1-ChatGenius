# Search Endpoints Documentation

## Overview
This document outlines the requirements for implementing search functionality across different entities in the chat application: messages, users, channels, and files.

## Authentication
All search endpoints require authentication using JWT token in the Authorization header:
```
Authorization: Bearer <token>
```

## Common Parameters
All search endpoints share these common query parameters:
- `query`: String - The search term(s)
- `limit`: Integer - Maximum number of results to return (default: 50)
- `skip`: Integer - Number of results to skip for pagination (default: 0)
- `sort_by`: String - Field to sort by (default varies by endpoint)
- `sort_order`: String - Either "asc" or "desc" (default: "desc")

## Message Search
**Endpoint**: `GET /search/messages`

**Description**: Search through message content across all channels the user has access to.

**Additional Query Parameters**:
- `channel_id`: Integer (optional) - Limit search to specific channel
- `from_date`: DateTime (optional) - Start date for message search
- `to_date`: DateTime (optional) - End date for message search
- `from_user`: Integer (optional) - Filter by sender user ID

**Response**:
```json
{
    "messages": [
        {
            "id": 1,
            "content": "Hello, world!",
            "created_at": "2024-03-15T12:34:56.789Z",
            "updated_at": "2024-03-15T12:34:56.789Z",
            "channel_id": 123,
            "user_id": 456,
            "parent_id": null,
            "has_replies": false,
            "channel": {
                "id": 123,
                "name": "general",
                "is_private": false
            },
            "user": {
                "id": 456,
                "email": "user@example.com",
                "name": "John Doe",
                "picture": "https://example.com/avatar.jpg"
            },
            "reactions": [],
            "files": [],
            "highlight": {
                "content": ["Hello, <em>world</em>!"]
            }
        }
    ],
    "total": 100,
    "has_more": true
}
```

## User Search
**Endpoint**: `GET /search/users`

**Description**: Search for users by name or email.

**Additional Query Parameters**:
- `exclude_channel`: Integer (optional) - Exclude users from specific channel
- `only_channel`: Integer (optional) - Only include users from specific channel

**Response**:
```json
{
    "users": [
        {
            "id": 1,
            "email": "user@example.com",
            "name": "John Doe",
            "picture": "https://example.com/avatar.jpg",
            "bio": "User biography",
            "is_active": true,
            "created_at": "2024-03-15T12:34:56.789Z",
            "channels": [],
            "messages": [],
            "highlight": {
                "name": ["John <em>Doe</em>"],
                "email": ["<em>user</em>@example.com"]
            }
        }
    ],
    "total": 50,
    "has_more": true
}
```

## Channel Search
**Endpoint**: `GET /search/channels`

**Description**: Search for channels by name or description.

**Additional Query Parameters**:
- `include_private`: Boolean (optional) - Include private channels in search (default: false)
- `is_dm`: Boolean (optional) - Filter by DM status
- `member_id`: Integer (optional) - Filter by channel member

**Response**:
```json
{
    "channels": [
        {
            "id": 1,
            "name": "general",
            "description": "General discussion",
            "is_private": false,
            "is_dm": false,
            "created_at": "2024-03-15T12:34:56.789Z",
            "owner_id": 123,
            "users": [],
            "messages": [],
            "member_count": 50,
            "highlight": {
                "name": ["<em>general</em>"],
                "description": ["<em>General</em> discussion"]
            }
        }
    ],
    "total": 25,
    "has_more": true
}
```

## File Search
**Endpoint**: `GET /search/files`

**Description**: Search for files by name or associated message content.

**Additional Query Parameters**:
- `channel_id`: Integer (optional) - Limit search to specific channel
- `file_type`: String (optional) - Filter by file type (e.g., "pdf", "image")
- `from_date`: DateTime (optional) - Start date for file upload search
- `to_date`: DateTime (optional) - End date for file upload search
- `uploaded_by`: Integer (optional) - Filter by uploader user ID

**Response**:
```json
{
    "files": [
        {
            "id": 1,
            "file_name": "example.pdf",
            "content_type": "application/pdf",
            "file_size": 1024567,
            "message_id": 123,
            "s3_key": "uploads/example.pdf",
            "uploaded_at": "2024-03-15T12:34:56.789Z",
            "uploaded_by": 456,
            "is_deleted": false,
            "channel_id": 789,
            "message_content": "Check out this document",
            "highlight": {
                "file_name": ["<em>example</em>.pdf"],
                "message_content": ["Check out this <em>document</em>"]
            }
        }
    ],
    "total": 75,
    "has_more": true
}
```

## Error Responses
All endpoints may return these error responses:

### 400 Bad Request
```json
{
    "detail": "Invalid search parameters"
}
```

### 401 Unauthorized
```json
{
    "detail": "Invalid or missing authentication token"
}
```

### 403 Forbidden
```json
{
    "detail": "Not authorized to search in this context"
}
```

### 429 Too Many Requests
```json
{
    "detail": "Search rate limit exceeded"
}
```

## Implementation Requirements

### Search Engine
- Use PostgreSQL's full-text search capabilities for initial implementation
- Consider migrating to Elasticsearch for better performance and features when needed

### Performance Requirements
- Search results should return within 500ms
- Support for at least 100 concurrent search requests
- Cache frequent search results
- Implement rate limiting to prevent abuse

### Security Requirements
- Sanitize all search inputs
- Respect channel and file access permissions
- Log all search queries for audit purposes
- Implement rate limiting per user
- Filter out sensitive information from search results

### Future Enhancements
1. Advanced search syntax support
   - Exact phrase matching
   - Field-specific searches
   - Boolean operators
   - Date range filters

2. Search result improvements
   - Fuzzy matching
   - Relevance scoring
   - Faceted search
   - Search suggestions
   - Autocomplete

3. Performance optimizations
   - Result caching
   - Asynchronous search
   - Batch processing
   - Search result pagination 