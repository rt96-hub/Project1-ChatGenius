# Search Endpoints

All endpoints in this router require authentication via Bearer token. They provide search functionality across messages, users, channels, and files.

## Rate Limiting
- Maximum requests per minute: 60 (configurable via `MAX_SEARCH_REQUESTS_PER_MINUTE` env var)
- Cache expiration: 300 seconds (5 minutes, configurable via `SEARCH_CACHE_EXPIRATION_SECONDS` env var)

## Endpoints

### GET /search/messages
Search through message content across accessible channels.

#### Request
- Headers:
  - `Authorization`: Bearer token (required)
- Query Parameters:
  - `query`: string (required) - Search text
  - `channel_id`: integer (optional) - Limit search to specific channel
  - `from_date`: datetime (optional) - Start date for search range
  - `to_date`: datetime (optional) - End date for search range
  - `from_user`: integer (optional) - Filter by message author
  - `limit`: integer (optional, default: 50, max: 100)
  - `skip`: integer (optional, default: 0)
  - `sort_by`: string (optional, default: "created_at")
  - `sort_order`: string (optional, default: "desc")

#### Response
- Status: 200 OK
- Body:
  ```json
  {
    "messages": [Message],
    "total": "integer",
    "has_more": "boolean"
  }
  ```

### GET /search/users
Search for users by name or email.

#### Request
- Headers:
  - `Authorization`: Bearer token (required)
- Query Parameters:
  - `query`: string (required) - Search text
  - `exclude_channel`: integer (optional) - Exclude users from specific channel
  - `only_channel`: integer (optional) - Only include users from specific channel
  - `limit`: integer (optional, default: 50, max: 100)
  - `skip`: integer (optional, default: 0)
  - `sort_by`: string (optional, default: "name")
  - `sort_order`: string (optional, default: "desc")

#### Response
- Status: 200 OK
- Body:
  ```json
  {
    "users": [User],
    "total": "integer",
    "has_more": "boolean"
  }
  ```

### GET /search/channels
Search for channels by name or description.

#### Request
- Headers:
  - `Authorization`: Bearer token (required)
- Query Parameters:
  - `query`: string (required) - Search text
  - `include_private`: boolean (optional, default: false)
  - `is_dm`: boolean (optional) - Filter for DM channels
  - `member_id`: integer (optional) - Filter by channel member
  - `limit`: integer (optional, default: 50, max: 100)
  - `skip`: integer (optional, default: 0)
  - `sort_by`: string (optional, default: "name")
  - `sort_order`: string (optional, default: "desc")

#### Response
- Status: 200 OK
- Body:
  ```json
  {
    "channels": [Channel],
    "total": "integer",
    "has_more": "boolean"
  }
  ```

### GET /search/files
Search for files by name or associated message content.

#### Request
- Headers:
  - `Authorization`: Bearer token (required)
- Query Parameters:
  - `query`: string (required) - Search text
  - `channel_id`: integer (optional) - Limit search to specific channel
  - `file_type`: string (optional) - Filter by file type
  - `from_date`: datetime (optional) - Start date for search range
  - `to_date`: datetime (optional) - End date for search range
  - `uploaded_by`: integer (optional) - Filter by uploader
  - `limit`: integer (optional, default: 50, max: 100)
  - `skip`: integer (optional, default: 0)
  - `sort_by`: string (optional, default: "uploaded_at")
  - `sort_order`: string (optional, default: "desc")

#### Response
- Status: 200 OK
- Body:
  ```json
  {
    "files": [File],
    "total": "integer",
    "has_more": "boolean"
  }
  ```

## Error Responses
- 400 Bad Request: Invalid date range or parameters
- 401 Unauthorized: Missing or invalid token
- 403 Forbidden: Not authorized to search in specified channel
- 429 Too Many Requests: Rate limit exceeded
- 500 Internal Server Error: Search operation failed 