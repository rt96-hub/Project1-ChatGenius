# Channel Endpoints

All endpoints in this router require authentication via Bearer token. They handle channel-related operations including creation, updates, and member management.

## Endpoints

### POST /
Creates a new channel.

#### Request
- Headers:
  - `Authorization`: Bearer token (required)
- Body (ChannelCreate schema):
  ```json
  {
    "name": "string",
    "description": "string",
    "is_private": "boolean"
  }
  ```

#### Response
- Status: 200 OK
- Body (Channel schema):
  ```json
  {
    "id": "integer",
    "name": "string",
    "description": "string",
    "owner_id": "integer",
    "is_private": "boolean",
    "is_dm": "boolean",
    "created_at": "datetime",
    "updated_at": "datetime"
  }
  ```

### GET /me
Returns list of channels the current user is a member of.

#### Request
- Headers:
  - `Authorization`: Bearer token (required)
- Query Parameters:
  - `skip`: integer (optional, default: 0)
  - `limit`: integer (optional, default: 100)

#### Response
- Status: 200 OK
- Body: Array of Channel objects

### GET /available
Returns list of public channels available to join.

#### Request
- Headers:
  - `Authorization`: Bearer token (required)
- Query Parameters:
  - `skip`: integer (optional, default: 0)
  - `limit`: integer (optional, default: 50)

#### Response
- Status: 200 OK
- Body: Array of Channel objects

### GET /{channel_id}
Get details of a specific channel.

#### Request
- Headers:
  - `Authorization`: Bearer token (required)
- Path Parameters:
  - `channel_id`: integer

#### Response
- Status: 200 OK
- Body: Channel object

### PUT /{channel_id}
Update channel details (owner only).

#### Request
- Headers:
  - `Authorization`: Bearer token (required)
- Path Parameters:
  - `channel_id`: integer
- Body (ChannelCreate schema):
  ```json
  {
    "name": "string",
    "description": "string",
    "is_private": "boolean"
  }
  ```

#### Response
- Status: 200 OK
- Body: Updated Channel object

### DELETE /{channel_id}
Delete a channel (owner only).

#### Request
- Headers:
  - `Authorization`: Bearer token (required)
- Path Parameters:
  - `channel_id`: integer

#### Response
- Status: 200 OK
- Body: Deleted Channel object

### GET /{channel_id}/members
Get list of channel members.

#### Request
- Headers:
  - `Authorization`: Bearer token (required)
- Path Parameters:
  - `channel_id`: integer

#### Response
- Status: 200 OK
- Body: Array of UserInChannel objects
  ```json
  {
    "user_id": "integer",
    "name": "string",
    "email": "string",
    "picture": "string"
  }
  ```

### DELETE /{channel_id}/members/{user_id}
Remove a member from channel (owner only).

#### Request
- Headers:
  - `Authorization`: Bearer token (required)
- Path Parameters:
  - `channel_id`: integer
  - `user_id`: integer

#### Response
- Status: 200 OK
- Body:
  ```json
  {
    "message": "Member removed successfully"
  }
  ```

### PUT /{channel_id}/privacy
Update channel privacy settings (owner only).

#### Request
- Headers:
  - `Authorization`: Bearer token (required)
- Path Parameters:
  - `channel_id`: integer
- Body:
  ```json
  {
    "is_private": "boolean"
  }
  ```

#### Response
- Status: 200 OK
- Body: Updated Channel object

### POST /{channel_id}/join
Join a public channel.

#### Request
- Headers:
  - `Authorization`: Bearer token (required)
- Path Parameters:
  - `channel_id`: integer

#### Response
- Status: 200 OK
- Body: Channel object

### POST /{channel_id}/leave
Leave a channel.

#### Request
- Headers:
  - `Authorization`: Bearer token (required)
- Path Parameters:
  - `channel_id`: integer

#### Response
- Status: 200 OK
- Body:
  ```json
  {
    "message": "Successfully left the channel"
  }
  ```

### POST /dm
Create a new DM channel.

#### Request
- Headers:
  - `Authorization`: Bearer token (required)
- Body:
  ```json
  {
    "user_ids": ["integer"]
  }
  ```

#### Response
- Status: 200 OK
- Body: Channel object

### GET /me/dms
Get list of user's DM channels.

#### Request
- Headers:
  - `Authorization`: Bearer token (required)
- Query Parameters:
  - `skip`: integer (optional, default: 0)
  - `limit`: integer (optional, default: 100)

#### Response
- Status: 200 OK
- Body: Array of Channel objects

## WebSocket Events

The channel router broadcasts several events through WebSocket connections:

1. `channel_update`: When channel details are updated
2. `member_left`: When a member leaves or is removed from a channel
3. `privacy_updated`: When channel privacy settings change
4. `member_joined`: When a new member joins a channel
5. `channel_created`: When a new channel is created

## Error Responses
- 400 Bad Request: Invalid request data
- 401 Unauthorized: Missing or invalid token
- 403 Forbidden: Insufficient permissions
- 404 Not Found: Channel or user not found
- 500 Internal Server Error: Server-side error 