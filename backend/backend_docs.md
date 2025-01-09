# Backend Documentation

## Overview
This is a FastAPI-based backend for a Slack-like communication platform. The system supports real-time messaging, channel management, and user authentication through Auth0. The application uses PostgreSQL for data persistence and WebSocket connections for real-time communication.

## Directory Structure
```
backend/
├── alembic/              # Database migration files
├── tests/                # Test files
├── __pycache__/         # Python cache files
├── .pytest_cache/       # Pytest cache
├── database.py          # Database configuration
├── models.py            # SQLAlchemy models
├── schemas.py           # Pydantic schemas
├── crud.py             # Database operations
├── main.py             # FastAPI application
├── auth0.py            # Auth0 authentication
├── api_docs.md         # API documentation
├── backend_docs.md     # Backend documentation
├── requirements.txt    # Python dependencies
├── .env               # Environment variables
└── alembic.ini        # Alembic configuration
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
     - `channels`: Many-to-many with Channel

2. `Channel`
   - **Purpose**: Represents chat channels
   - **Fields**:
     - `id`: Primary key
     - `name`: Channel name
     - `description`: Channel description
     - `owner_id`: Channel creator's user ID
     - `created_at`: Channel creation timestamp
     - `is_private`: Privacy status
     - `join_code`: Invitation code for private channels
   - **Relationships**:
     - `messages`: One-to-many with Message
     - `users`: Many-to-many with User
     - `owner`: One-to-one with User
     - `roles`: One-to-many with ChannelRole

3. `Message`
   - **Purpose**: Represents chat messages
   - **Fields**:
     - `id`: Primary key
     - `content`: Message text
     - `created_at`: Message creation timestamp
     - `updated_at`: Last edit timestamp
     - `user_id`: Author's user ID
     - `channel_id`: Channel ID
   - **Relationships**:
     - `user`: Many-to-one with User
     - `channel`: Many-to-one with Channel
     - `reactions`: One-to-many with MessageReaction

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

### 3. `schemas.py`
**Purpose**: Defines Pydantic models for request/response validation and serialization

**Key Schema Categories**:

1. Message-related:
   - `MessageBase`: Base message schema
   - `MessageCreate`: Message creation schema
   - `Message`: Complete message schema with relationships
   - `MessageList`: Paginated message list

2. Channel-related:
   - `ChannelBase`: Base channel schema
   - `ChannelCreate`: Channel creation schema
   - `Channel`: Complete channel schema with relationships
   - `ChannelRole`: Channel role schema
   - `ChannelInvite`: Channel invitation schema
   - `ChannelMemberUpdate`: Member role update schema
   - `ChannelPrivacyUpdate`: Privacy settings schema

3. User-related:
   - `UserBase`: Base user schema
   - `UserCreate`: User creation schema
   - `User`: Complete user schema with relationships
   - `UserInChannel`: Simplified user representation
   - `UserBioUpdate`: Bio update schema
   - `UserNameUpdate`: Name update schema

4. Reaction-related:
   - `ReactionBase`: Base reaction schema
   - `ReactionCreate`: Reaction creation schema
   - `Reaction`: Complete reaction schema
   - `MessageReactionCreate`: Reaction assignment schema
   - `MessageReaction`: Complete message reaction schema

5. Authentication:
   - `Token`: JWT token schema
   - `TokenData`: Token payload schema

### 4. `crud.py`
**Purpose**: Implements database operations and business logic

**Key Function Categories**:

1. User Operations:
   - User retrieval by ID, email, or Auth0 ID
   - User creation and updates
   - Auth0 user synchronization

2. Channel Operations:
   - Channel CRUD operations
   - Member management
   - Role management
   - Privacy settings
   - Invitation handling

3. Message Operations:
   - Message CRUD operations
   - Message retrieval with pagination
   - Reaction management

### 5. `auth0.py`
**Purpose**: Manages Auth0 authentication and authorization

**Key Features**:
- JWT token validation
- Public key caching
- User authentication middleware
- Auth0 integration configuration

### 6. `main.py`
**Purpose**: FastAPI application entry point and route definitions

**Key Features**:
- API route definitions
- WebSocket connection management
- CORS configuration
- Authentication middleware
- Real-time event handling

## Database Migrations
The project uses Alembic for database schema migrations. See the Migrations section in the documentation for detailed information about managing database changes.

## WebSocket Events
The application supports real-time events for:
- Message operations (create, update, delete)
- Channel updates
- Member management
- Reaction management

For detailed API endpoints and request/response formats, please refer to `api_docs.md`.

## Environment Variables
Required environment variables:
- `DB_URL`: PostgreSQL database URL
- `AUTH0_DOMAIN`: Auth0 domain
- `AUTH0_API_IDENTIFIER`: Auth0 API identifier
- `MAX_WEBSOCKET_CONNECTIONS_PER_USER`: Maximum WebSocket connections per user (default: 5)
- `MAX_TOTAL_WEBSOCKET_CONNECTIONS`: Maximum total WebSocket connections (default: 1000)

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
``` 