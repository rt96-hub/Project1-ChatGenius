# Backend Documentation

## Overview
This is a FastAPI-based backend for a Slack-like communication platform. The system supports real-time messaging, channel management, user authentication through Auth0, message reactions, and file storage with AWS S3. The application uses PostgreSQL for data persistence and WebSocket connections for real-time communication.

## Directory Structure
```
backend/
├── alembic/              # Database migration files
├── scripts/              # Utility scripts for deployment and maintenance
├── tests/                # Test files
├── __pycache__/         # Python cache files
├── .pytest_cache/       # Pytest cache
├── database.py          # Database configuration
├── models.py            # SQLAlchemy models
├── schemas.py           # Pydantic schemas
├── crud.py             # Database operations
├── main.py             # FastAPI application and endpoints
├── auth0.py            # Auth0 authentication
├── file_uploads.py     # File upload handling and S3 integration
├── websocket_manager.py # WebSocket connection management
├── api_docs.md         # API documentation
├── backend_docs.md     # Backend documentation
├── requirements.txt    # Primary Python dependencies
├── requirements2.txt   # Extended Python dependencies
├── .env               # Environment variables
├── Dockerfile         # Container configuration
├── alembic.ini        # Alembic migration configuration
├── pytest-local.ini   # Local pytest configuration
└── seed_reactions.py  # Script for seeding reaction data
```

## Core Components

### 1. `database.py`
**Purpose**: Handles database connection and session management

**Key Components**:
- SQLAlchemy engine configuration using environment variables
- Session management with `SessionLocal`
- Base declarative model for SQLAlchemy models

**Dependencies**:
- Environment variable: `DB_URL` for PostgreSQL connection
- SQLAlchemy
- python-dotenv

### 2. `models.py`
**Purpose**: Defines SQLAlchemy ORM models that represent database tables

**Models**:

1. `User`
   - **Purpose**: Represents application users
   - **Fields**:
     - `id`: Primary key
     - `auth0_id`: Unique Auth0 identifier
     - `email`: User's email (unique)
     - `is_active`: Account status
     - `created_at`: Account creation timestamp
     - `name`: Display name
     - `picture`: Profile picture URL
     - `bio`: User biography
   - **Relationships**:
     - `messages`: One-to-many with Message
     - `channels`: Many-to-many with Channel through UserChannel

2. `Channel`
   - **Purpose**: Represents chat channels and DMs
   - **Fields**:
     - `id`: Primary key
     - `name`: Channel name
     - `description`: Channel description
     - `owner_id`: Channel creator's user ID
     - `created_at`: Channel creation timestamp
     - `is_private`: Privacy status
     - `is_dm`: Direct message flag
     - `join_code`: Invitation code for private channels
   - **Relationships**:
     - `messages`: One-to-many with Message
     - `users`: Many-to-many with User through UserChannel
     - `owner`: One-to-one with User
     - `roles`: One-to-many with ChannelRole
   - **Constraints**:
     - DM channels must be private

3. `Message`
   - **Purpose**: Represents chat messages and their replies
   - **Fields**:
     - `id`: Primary key
     - `content`: Message text
     - `created_at`: Message creation timestamp
     - `updated_at`: Last edit timestamp
     - `user_id`: Author's user ID
     - `channel_id`: Channel ID
     - `parent_id`: ID of the message being replied to (unique, optional)
   - **Relationships**:
     - `user`: Many-to-one with User
     - `channel`: Many-to-one with Channel
     - `reactions`: One-to-many with MessageReaction
     - `parent`: One-to-one with Message (self-referential for replies)
     - `reply`: One-to-one back reference to child message
   - **Constraints**:
     - Unique constraint on parent_id (ensures one reply per message)
     - Foreign key constraint from parent_id to messages.id

4. `UserChannel`
   - **Purpose**: Association table for user-channel memberships
   - **Fields**:
     - `user_id`: User ID (primary key)
     - `channel_id`: Channel ID (primary key)

5. `ChannelRole`
   - **Purpose**: Manages user roles within channels
   - **Fields**:
     - `id`: Primary key
     - `channel_id`: Channel ID
     - `user_id`: User ID
     - `role`: Role name
     - `created_at`: Role assignment timestamp
   - **Relationships**:
     - `channel`: Many-to-one with Channel
     - `user`: Many-to-one with User

6. `Reaction`
   - **Purpose**: Defines available message reactions
   - **Fields**:
     - `id`: Primary key
     - `code`: Unique reaction identifier
     - `is_system`: System/custom reaction flag
     - `image_url`: Custom reaction image URL
     - `created_at`: Creation timestamp
   - **Relationships**:
     - `message_reactions`: One-to-many with MessageReaction

7. `MessageReaction`
   - **Purpose**: Tracks user reactions to messages
   - **Fields**:
     - `id`: Primary key
     - `message_id`: Message ID
     - `reaction_id`: Reaction ID
     - `user_id`: User ID
     - `created_at`: Reaction timestamp
   - **Relationships**:
     - `message`: Many-to-one with Message
     - `reaction`: Many-to-one with Reaction
     - `user`: Many-to-one with User
   - **Constraints**:
     - Unique constraint on (message_id, reaction_id, user_id)

### 3. `main.py`
**Purpose**: FastAPI application entry point and route definitions

**Key Features**:
- WebSocket connection management for real-time updates
- CORS configuration
- Authentication middleware
- API route definitions for:
  - User management
  - Channel operations
  - Message handling
  - Reaction management
  - Direct messaging
  - Role management

**Dependencies**:
- FastAPI
- WebSocket support
- Auth0 integration
- Database session management

### 4. `auth0.py`
**Purpose**: Handles Auth0 authentication and authorization

**Key Features**:
- JWT token validation
- Public key caching
- User authentication middleware
- Auth0 integration configuration

**Dependencies**:
- python-jose[cryptography]
- Auth0 domain and API identifier from environment variables

### 5. `crud.py`
**Purpose**: Implements database operations and business logic

**Key Operations**:
- User management (create, read, update)
- Channel operations (create, read, update, delete)
- Message handling (create, read, update, delete)
- Reaction management
- Role management
- Direct message handling

**Dependencies**:
- SQLAlchemy
- Database models
- Pydantic schemas

### 6. `file_uploads.py`
**Purpose**: Handles file upload operations and AWS S3 integration

**Key Features**:
- File upload validation and processing
- AWS S3 integration for file storage
- File download URL generation
- File deletion handling

**Key Components**:
- S3 client configuration
- File type validation
- Unique S3 key generation
- File size limits enforcement
- WebSocket event broadcasting for file operations

**Dependencies**:
- boto3: AWS SDK for Python
- python-magic: File type detection
- Environment variables for AWS configuration

### 7. `websocket_manager.py`
**Purpose**: Manages WebSocket connections and real-time event broadcasting

**Key Components**:
- Connection management for users and channels
- Connection limits enforcement
- Event broadcasting to channel members
- Handling of disconnections and cleanup

**Key Features**:
- Per-user connection tracking
- Channel membership management
- Real-time event broadcasting for:
  - Messages
  - Channel updates
  - Member management
  - File operations
  - Reactions

**Dependencies**:
- FastAPI WebSocket support
- Pydantic schemas for event data

## Environment Configuration
Required environment variables:
- `DB_URL`: PostgreSQL database URL
- `AUTH0_DOMAIN`: Auth0 domain
- `AUTH0_API_IDENTIFIER`: Auth0 API identifier
- `MAX_WEBSOCKET_CONNECTIONS_PER_USER`: Maximum WebSocket connections per user (default: 5)
- `MAX_TOTAL_WEBSOCKET_CONNECTIONS`: Maximum total WebSocket connections (default: 1000)
- `AWS_ACCESS_KEY_ID`: AWS access key for S3
- `AWS_SECRET_ACCESS_KEY`: AWS secret key for S3
- `AWS_S3_BUCKET_NAME`: S3 bucket name for file storage
- `AWS_S3_REGION`: AWS region for S3 (default: us-east-1)
- `MAX_FILE_SIZE_MB`: Maximum file size in MB (default: 50)
- `ALLOWED_FILE_TYPES`: Comma-separated list of allowed MIME types

## WebSocket Events
The application supports real-time events for:
- Message operations (create, update, delete)
- Channel updates (create, update, privacy changes)
- Member management (join, leave, role updates)
- Reaction management (add, remove)
- File operations:
  - File uploads (create)
  - File deletions
  - Download URL generation

## Dependencies
Key dependencies from requirements.txt:
- FastAPI: Web framework
- SQLAlchemy: ORM
- Pydantic: Data validation
- python-jose[cryptography]: JWT handling
- python-dotenv: Environment variable management
- psycopg2-binary: PostgreSQL adapter
- websockets: WebSocket support
- alembic: Database migrations
- boto3: AWS SDK for Python
- python-magic: File type detection
- python-multipart: File upload handling

For detailed API endpoints and request/response formats, please refer to `api_docs.md`. 