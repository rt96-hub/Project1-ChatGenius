# Backend Documentation

## Overview
This is a FastAPI-based backend for a Slack-like communication platform. The system supports real-time messaging, channel management, and user authentication through Auth0. The application uses PostgreSQL for data persistence and WebSocket connections for real-time communication.

## Core Components

### 1. `database.py`
**Purpose**: Database connection and session management

**Key Components**:
- SQLAlchemy engine configuration
- Session management
- Base declarative model

**Dependencies**:
- Environment variables (DB_URL)
- SQLAlchemy
- Python-dotenv

### 2. `models.py`
**Purpose**: SQLAlchemy ORM models defining the database schema

**Models**:
1. `User`
   - Fields: id, auth0_id, email, is_active, created_at, name, picture
   - Relationships: messages, channels
   
2. `Channel`
   - Fields: id, name, description, owner_id, created_at, is_private, join_code
   - Relationships: messages, users, owner, roles
   
3. `Message`
   - Fields: id, content, created_at, updated_at, user_id, channel_id
   - Relationships: user, channel, reactions
   
4. `UserChannel` (Association table)
   - Fields: user_id, channel_id

5. `ChannelRole`
   - Fields: id, channel_id, user_id, role, created_at
   - Relationships: channel, user

6. `Reaction`
   - Fields: id, code, is_system, image_url, created_at
   - Relationships: message_reactions
   - Purpose: Stores available reactions (both system emojis and custom uploaded ones)
   
7. `MessageReaction`
   - Fields: id, message_id, reaction_id, user_id, created_at
   - Relationships: message, reaction, user
   - Constraints: Unique constraint on (message_id, reaction_id, user_id)
   - Purpose: Associates reactions with messages and the users who made them

**Dependencies**:
- SQLAlchemy
- `database.py`

### 3. `schemas.py`
**Purpose**: Pydantic models for request/response validation and serialization

**Key Schemas**:
1. Message-related:
   - `MessageBase`, `MessageCreate`, `Message`
   - `MessageList` (for pagination)
   
2. Channel-related:
   - `ChannelBase`, `ChannelCreate`, `Channel`
   - `ChannelRoleBase`, `ChannelRole`
   - `ChannelInvite`
   - `ChannelMemberUpdate`
   - `ChannelPrivacyUpdate`
   
3. User-related:
   - `UserBase`, `UserCreate`, `User`
   - `UserInChannel` (simplified user representation)
   
4. Authentication:
   - `Token`, `TokenData`

**Dependencies**:
- Pydantic
- `models.py`

### 4. `crud.py`
**Purpose**: Database operations and business logic

**Key Functions**:

1. User Operations:
   - `get_user(db, user_id)`
   - `get_user_by_email(db, email)`
   - `get_user_by_auth0_id(db, auth0_id)`
   - `get_users(db, skip, limit)`
   - `sync_auth0_user(db, user_data)`

2. Channel Operations:
   - `create_channel(db, channel, creator_id)`
   - `get_channel(db, channel_id)`
   - `get_user_channels(db, user_id, skip, limit)`
   - `update_channel(db, channel_id, channel_update)`
   - `delete_channel(db, channel_id)`
   - `get_channel_members(db, channel_id)`
   - `remove_channel_member(db, channel_id, user_id)`
   - `update_channel_privacy(db, channel_id, privacy_update)`
   - `create_channel_invite(db, channel_id)`
   - `get_user_channel_role(db, channel_id, user_id)`
   - `update_user_channel_role(db, channel_id, user_id, role)`
   - `leave_channel(db, channel_id, user_id)`

3. Message Operations:
   - `create_message(db, channel_id, user_id, message)`
   - `get_channel_messages(db, channel_id, skip, limit)`
   - `update_message(db, message_id, message_update)`
   - `delete_message(db, message_id)`
   - `get_message(db, message_id)`

**Dependencies**:
- SQLAlchemy
- `models.py`
- `schemas.py`

### 5. `auth0.py`
**Purpose**: Handles Auth0 authentication, token verification, and user management

**Key Components**:

1. Auth0 Configuration:
   - Environment variables setup (AUTH0_DOMAIN, AUTH0_API_IDENTIFIER)
   - Public key caching with `@lru_cache`
   - HTTPBearer security scheme

2. Key Functions:
   - `get_auth0_public_key()`: Fetches and caches Auth0 public key for token verification
     - Input: None
     - Output: JWKS (JSON Web Key Set)
     - Cache: Implements LRU cache for performance
   
   - `verify_token(token: str)`: Verifies Auth0 JWT tokens
     - Input: JWT token string
     - Output: Decoded token payload
     - Validation:
       - Verifies token signature using Auth0 public key
       - Validates audience and issuer
       - Checks token expiration
   
   - `get_current_user(request, credentials, db)`: FastAPI dependency for user authentication
     - Input: 
       - HTTP request
       - Bearer token credentials
       - Database session
     - Output: Current authenticated user
     - Dependencies: `crud.py` for user lookup

**Error Handling**:
- JWT validation errors (401 Unauthorized)
- User not found errors (404 Not Found)
- Auth0 public key fetch errors
- Detailed error logging

**Dependencies**:
- External:
  - python-jose[cryptography]
  - requests
  - fastapi.security
- Internal:
  - `crud.py`
  - `database.py`

**Required Environment Variables**:
- `AUTH0_DOMAIN`: Auth0 tenant domain
- `AUTH0_API_IDENTIFIER`: API identifier in Auth0

**Authentication Flow**:
1. Client sends request with Auth0 JWT token
2. Token is validated against Auth0 public key
3. User is looked up by Auth0 ID in local database
4. Request proceeds with authenticated user context

### 5. `main.py`
**Purpose**: FastAPI application and endpoint definitions

**Key Components**:

1. Application Setup:
   - CORS middleware configuration
   - Database initialization
   - WebSocket connection manager

2. WebSocket Management:
   - `ConnectionManager` class for handling real-time connections
   - Methods: connect, disconnect, broadcast_to_channel

**API Endpoints**:

1. Authentication:
   ```
   POST /auth/sync - Sync Auth0 user data
   GET /auth/verify - Verify Auth0 token
   ```

2. WebSocket:
   ```
   WS /ws - WebSocket connection endpoint
   ```

3. User Management:
   ```
   GET /users/me - Get current user
   GET /users/ - List users
   GET /users/{user_id} - Get specific user
   ```

4. Channel Management:
   ```
   POST /channels/ - Create channel
   GET /channels/me - List user's channels
   GET /channels/{channel_id} - Get channel
   PUT /channels/{channel_id} - Update channel
   DELETE /channels/{channel_id} - Delete channel
   ```

5. Message Management:
   ```
   POST /channels/{channel_id}/messages - Create message
   GET /channels/{channel_id}/messages - List messages
   PUT /channels/{channel_id}/messages/{message_id} - Update message
   DELETE /channels/{channel_id}/messages/{message_id} - Delete message
   ```

6. Channel Membership:
   ```
   GET /channels/{channel_id}/members - List channel members
   DELETE /channels/{channel_id}/members/{user_id} - Remove member
   PUT /channels/{channel_id}/privacy - Update privacy settings
   POST /channels/{channel_id}/invite - Create invite
   POST /channels/{channel_id}/leave - Leave channel
   ```

7. Channel Roles:
   ```
   GET /channels/{channel_id}/role - Get user's role
   PUT /channels/{channel_id}/roles/{user_id} - Update user's role
   ```

**Dependencies**:
- FastAPI
- SQLAlchemy
- `crud.py`
- `models.py`
- `schemas.py`
- `auth0.py`

## Environment Variables
Required environment variables:
- `DB_URL`: PostgreSQL database URL
- `AUTH0_DOMAIN`: Auth0 domain
- `AUTH0_API_IDENTIFIER`: Auth0 API identifier
- `MAX_WEBSOCKET_CONNECTIONS_PER_USER`: Default 5
- `MAX_TOTAL_WEBSOCKET_CONNECTIONS`: Default 1000

## Dependencies
Key dependencies (from requirements.txt):
- FastAPI
- SQLAlchemy
- Pydantic
- python-jose[cryptography]
- python-dotenv
- psycopg2-binary
- websockets

## System Dependencies
The following files/systems depend on each other in this order:
1. `database.py` (Base dependency)
2. `models.py` (depends on database.py)
3. `schemas.py` (depends on models.py)
4. `crud.py` (depends on models.py and schemas.py)
5. `auth0.py` (depends on crud.py)
6. `main.py` (depends on all other files)

## Error Handling
- HTTP exceptions for API errors
- Logging configuration for error tracking
- WebSocket connection management with proper cleanup
- Database session management with proper closure 

## Database Migrations with Alembic

### Overview
The project uses Alembic for database migrations, which is integrated with SQLAlchemy models. Alembic tracks database schema changes and provides version control for the database structure.

### Directory Structure
```
backend/
├── alembic/
│   ├── versions/         # Migration version files
│   ├── env.py           # Alembic environment configuration
│   └── script.py.mako   # Migration file template
└── alembic.ini          # Alembic configuration file
```

### Key Components

1. **alembic.ini**
   - Main configuration file
   - Defines database connection string
   - Sets migration script location
   - Configures logging and template settings

2. **env.py**
   - Establishes connection between Alembic and SQLAlchemy models
   - Imports all models from `models.py`
   - Sets up database URL configuration
   - Handles migration context

3. **versions/**
   - Contains numbered migration scripts
   - Each script has upgrade() and downgrade() functions
   - Maintains chronological order of schema changes

### Common Commands

1. **Create a New Migration**
   ```bash
   alembic revision -m "description_of_changes"
   ```
   - Creates a new migration file in versions/
   - Add SQL changes in upgrade() and downgrade() functions

2. **Generate Automatic Migrations**
   ```bash
   alembic revision --autogenerate -m "description_of_changes"
   ```
   - Detects model changes automatically
   - Generates migration script based on differences between models and database

3. **Apply Migrations**
   ```bash
   alembic upgrade head           # Apply all pending migrations
   alembic upgrade +1             # Apply next migration
   alembic upgrade revision_id    # Upgrade to specific revision
   ```

4. **Rollback Migrations**
   ```bash
   alembic downgrade -1           # Rollback last migration
   alembic downgrade revision_id  # Rollback to specific revision
   alembic downgrade base        # Rollback all migrations
   ```

5. **View Migration Information**
   ```bash
   alembic current     # Show current revision
   alembic history     # Show migration history
   alembic heads       # Show latest revisions
   ```

### Migration Workflow

1. **Making Database Changes**
   ```python
   # 1. Update models.py with new changes
   class User(Base):
       __tablename__ = "users"
       new_field = Column(String, nullable=True)  # Add new field

   # 2. Generate migration
   $ alembic revision --autogenerate -m "add new_field to users"

   # 3. Review generated migration in versions/
   # 4. Apply migration
   $ alembic upgrade head
   ```

2. **Best Practices**
   - Always review autogenerated migrations
   - Include both upgrade and downgrade paths
   - Test migrations on development database first
   - Back up production database before migrating
   - Run migrations during low-traffic periods

### Integration with Models

- Alembic automatically detects changes in `models.py`
- Supported changes include:
  - New tables/models
  - New columns
  - Modified columns
  - Removed columns/tables
  - New relationships
  - New indices or constraints

### Error Handling

1. **Common Issues**
   - Migration conflicts
   - Failed migrations
   - Data type conversion errors

2. **Recovery Steps**
   ```bash
   # If migration fails
   alembic downgrade -1    # Rollback to last working version
   
   # Fix issues in migration script
   # Retry migration
   alembic upgrade head
   ```

### Environment Variables
Required for migrations:
- `DB_URL`: Same database URL used by the application
- `PYTHONPATH`: Must include project root for model imports

### Dependencies
- alembic
- sqlalchemy
- psycopg2-binary (for PostgreSQL) 

### WebSocket Events

The application supports the following real-time events:

1. Message Events:
   - `new_message`: When a new message is sent
   - `message_update`: When a message is edited
   - `message_delete`: When a message is deleted

2. Channel Events:
   - `channel_update`: When channel details are updated
   - `member_joined`: When a new member joins a channel
   - `member_left`: When a member leaves a channel
   - `role_updated`: When a member's role is updated
   - `privacy_updated`: When channel privacy settings are updated

### API Endpoints

1. Channel Membership:
   ```
   GET /channels/{channel_id}/members - List channel members
   DELETE /channels/{channel_id}/members/{user_id} - Remove member
   PUT /channels/{channel_id}/privacy - Update privacy settings
   POST /channels/{channel_id}/invite - Create invite
   POST /channels/{channel_id}/leave - Leave channel
   ```

2. Channel Roles:
   ```
   GET /channels/{channel_id}/role - Get user's role
   PUT /channels/{channel_id}/roles/{user_id} - Update user's role
   ``` 