# Data Seeding Implementation Checklist

## Initial Setup

### 1. Install Required Packages
- [x] Add Faker to requirements.txt
- [x] Run: `pip install -r requirements.txt`

### 2. Create Directory Structure
- [x] Create directory: `backend/scripts` (if it doesn't exist)
- [x] Create file: `backend/scripts/__init__.py`
- [x] Create file: `backend/scripts/seed_data.py`

## Implementation Steps

### 1. Basic Script Setup
- [x] Create basic script structure in `seed_data.py`:
```python
from faker import Faker
from datetime import datetime
import random
from sqlalchemy.orm import Session
from typing import List

from models import User, Channel, Message, UserChannel, MessageReaction, Reaction
from database import SessionLocal

fake = Faker()

def main():
    db = SessionLocal()
    try:
        # Implementation will go here
        pass
    finally:
        db.close()

if __name__ == "__main__":
    main()
```

### 2. User Generation Implementation
- [x] Create `create_fake_users` function that:
  - [x] Takes parameters:
    - [x] SQLAlchemy database session
    - [x] Number of users to create (default: 10)
  - [x] Returns List[User]
  - [x] Works with User model fields:
    - [x] auth0_id (format: "auth0|<uuid>")
    - [x] email (must be unique)
    - [x] is_active (boolean)
    - [x] created_at (timestamp within current year)
    - [x] name
    - [x] picture (avatar URL)
    - [x] bio (max 200 chars)
  - [x] Implements proper database transaction handling
  - [x] Returns list of created users for further use

### 3. Channel Generation Implementation
- [x] Create `create_fake_channels` function that:
  - [x] Takes parameters:
    - [x] SQLAlchemy database session
    - [x] List of available users
    - [x] Number of channels to create (default: 5)
  - [x] Returns List[Channel]
  - [x] Implements channel type logic:
    - [x] 30% chance of being a DM channel
    - [x] 40% chance of being private for regular channels
  - [x] Works with Channel model fields:
    - [x] name (owner name + DM for DMs)
    - [x] description (null for DMs)
    - [x] owner_id (from available users)
    - [x] created_at (timestamp within current year)
    - [x] is_private (always true for DMs)
    - [x] is_dm (boolean)
    - [x] join_code (only for private non-DM channels)

### 4. Channel Membership Implementation
- [x] Create `add_users_to_channels` function that:
  - [x] Takes parameters:
    - [x] SQLAlchemy database session
    - [x] List of available users
    - [x] List of channels
  - [x] Implements membership logic:
    - [x] For DM channels:
      - [x] Exactly 2 users per channel
      - [x] Ensure the owner is the first user
      - [x] Ensure that the users are not the same
    - [x] For regular channels:
      - [x] Random number of users (minimum 2, maximum all users)
      - [x] Ensure channel owner is always included
  - [x] Works with UserChannel model:
    - [x] user_id
    - [x] channel_id

### 5. Message Generation Implementation
- [x] Create `create_fake_messages` function that:
  - [x] Takes parameters:
    - [x] SQLAlchemy database session
    - [x] List of channels
    - [x] List of users
    - [x] Messages per channel (default: 20)
  - [x] Returns List[Message]
  - [x] Implements message creation logic:
    - [x] Only create messages from channel members
    - [x] 60% chance of message being a sentence
    - [x] 40% chance of message being a paragraph
    - [x] 20% chance of generating a reply to each message
  - [x] Works with Message model fields:
    - [x] content
    - [x] created_at (timestamp within current year)
    - [x] updated_at
    - [x] user_id (must be channel member)
    - [x] channel_id
    - [x] parent_id (for replies)

### 6. Reaction Implementation
- [x] Create `add_reactions_to_messages` function that:
  - [x] Takes parameters:
    - [x] SQLAlchemy database session
    - [x] List of messages
    - [x] List of users
    - [x] List of available reactions (fetched from database)
  - [x] Implements reaction logic:
    - [x] 40% chance of adding reactions to any message
    - [x] 1-3 reactions per message when chosen
    - [x] Prevent duplicate reactions from same user
  - [x] Works with MessageReaction model:
    - [x] message_id
    - [x] reaction_id
    - [x] user_id
    - [x] created_at
  - [x] Implements proper error handling for duplicates

### 7. Main Function Implementation
- [x] Create main function that:
  - [x] Implements proper database session handling
  - [x] Verifies reactions exist before starting
  - [x] Executes seeding functions in correct order:
    - [x] Users first
    - [x] Then channels
    - [x] Then channel memberships
    - [x] Then messages
    - [x] Finally reactions
  - [x] Provides progress feedback to user
  - [x] Implements proper error handling
  - [x] Ensures proper cleanup on failure

## Testing and Running

### 1. Prepare Database
- [ ] Ensure database is running
- [ ] Run migrations: `alembic upgrade head`
- [ ] Run reactions seeding: `python backend/scripts/seed_reactions.py`
- [ ] Run on docker with 'docker-compose backend cmd

### 2. Test Script
- [ ] Run script: `python backend/scripts/seed_data.py`
- [ ] Verify in database that:
  - [ ] Users were created
  - [ ] Channels were created
  - [ ] Messages were created
  - [ ] Replies were created
  - [ ] Reactions were added

### 3. Adjust Parameters (Optional)
If needed, modify these values in main():
- [ ] Number of users (`count=20`)
- [ ] Number of channels (`count=10`)
- [ ] Messages per channel (`messages_per_channel=20`)

## Cleanup (Optional)

### Create Cleanup Script
- [ ] Create `backend/scripts/cleanup_fake_data.py`
- [ ] Implement cleanup logic to remove seeded data
- [ ] Test cleanup script

## Troubleshooting

If you encounter issues:
1. Check database connection in .env
2. Verify all tables exist using migrations
3. Ensure reactions are seeded first
4. Check for unique constraint violations
5. Verify proper imports from models.py

## Next Steps

After successful implementation:
- [ ] Add script to deployment documentation
- [ ] Create specific test scenarios
- [ ] Add command-line arguments for customization
- [ ] Implement data cleanup script
- [ ] Add progress bars for long operations 

## Extending the Seeding System

### Adding New Features

#### 1. Adding New Model Support
When adding support for a new database model:
1. Create a new function following the pattern:
```python
def create_fake_[model_name](db: Session, dependencies: List[Any], count: int) -> List[Model]:
    items = []
    for _ in range(count):
        item = Model(
            # Add appropriate fake data for each field
            field1=fake.relevant_faker_method(),
            field2=fake.relevant_faker_method(),
            # Add relationships
            relationship_id=random.choice(dependencies).id
        )
        db.add(item)
        items.append(item)
    
    db.commit()
    return items
```

2. Add the function call to main():
```python
def main():
    db = SessionLocal()
    try:
        # ... existing code ...
        
        print(f"Creating fake {model_name}...")
        new_items = create_fake_[model_name](db, dependencies, count=10)
        
        # ... rest of the code ...
```

#### 2. Adding New Fields to Existing Models
When a model gets new fields:
1. Update the relevant creation function:
```python
def create_fake_users(db: Session, count: int = 10) -> List[User]:
    users = []
    for _ in range(count):
        user = User(
            # ... existing fields ...
            new_field=fake.relevant_faker_method(),  # Add new field
            another_new_field=generate_custom_data() # Add custom generation if needed
        )
        # ... rest of the function ...
```

2. If the new field requires custom data generation, create a helper function:
```python
def generate_custom_data() -> Any:
    # Custom logic for generating specific data
    return data
```

#### 3. Adding New Relationships
When adding new relationships between models:
1. Create a new association function:
```python
def associate_model_a_with_model_b(db: Session, model_a_items: List[ModelA], 
                                 model_b_items: List[ModelB]):
    for item_a in model_a_items:
        # Define relationship logic
        selected_items = random.sample(model_b_items, 
                                     random.randint(min_items, max_items))
        
        for item_b in selected_items:
            association = AssociationModel(
                model_a_id=item_a.id,
                model_b_id=item_b.id,
                # Additional fields if any
                created_at=fake.date_time_this_year()
            )
            db.add(association)
    
    db.commit()
```

2. Add the association call to main():
```python
def main():
    # ... existing code ...
    associate_model_a_with_model_b(db, model_a_items, model_b_items)
```

### Best Practices for Extensions

1. **Maintain Dependencies Order**
- Always create independent entities first
- Follow the dependency chain for related entities
- Update the main() function to reflect the correct order

2. **Data Consistency**
- Keep track of valid value ranges
- Maintain realistic relationships between entities
- Use consistent time ranges across related entities

3. **Error Handling**
```python
def safe_creation_with_retry(db: Session, create_func, max_retries=3):
    for attempt in range(max_retries):
        try:
            return create_func()
        except Exception as e:
            db.rollback()
            if attempt == max_retries - 1:
                raise e
            time.sleep(1)
```

4. **Custom Faker Providers**
When needed, create custom providers for specific data:
```python
from faker.providers import BaseProvider

class CustomProvider(BaseProvider):
    def custom_value(self):
        return self.random_element(['value1', 'value2', 'value3'])

# Usage:
fake.add_provider(CustomProvider)
```

### Example: Adding a New Feature

Let's say we're adding user status updates. Here's the complete process:

1. Create the new function:
```python
def create_fake_user_statuses(db: Session, users: List[User], 
                            count_per_user: int = 5) -> List[UserStatus]:
    statuses = []
    for user in users:
        for _ in range(count_per_user):
            status = UserStatus(
                user_id=user.id,
                status_text=fake.sentence(),
                emoji=random.choice(['😊', '🎉', '💻', '☕']),
                created_at=fake.date_time_this_year(),
                expires_at=fake.future_datetime(),
                is_active=random.choice([True, False])
            )
            db.add(status)
            statuses.append(status)
    
    db.commit()
    return statuses
```

2. Update main():
```python
def main():
    db = SessionLocal()
    try:
        # ... existing code ...
        
        print("Creating user statuses...")
        user_statuses = create_fake_user_statuses(db, users)
        
        print("Seeding completed successfully!")
    finally:
        db.close()
```

3. Add cleanup support:
```python
def cleanup_user_statuses(db: Session):
    db.query(UserStatus).delete()
    db.commit()
```

### Testing New Features

1. Create a test file for new seeding functions:
```python
def test_create_fake_user_statuses():
    db = SessionLocal()
    try:
        users = create_fake_users(db, count=5)
        statuses = create_fake_user_statuses(db, users, count_per_user=3)
        
        assert len(statuses) == 15  # 5 users * 3 statuses
        assert all(s.user_id is not None for s in statuses)
        assert all(s.status_text is not None for s in statuses)
    finally:
        db.close()
```

2. Run tests before committing changes:
```bash
pytest backend/tests/test_seed_data.py -v
```

### Maintenance Tips

1. Regularly update Faker version for new features
2. Keep seed data volume configurable
3. Document new seeding functions
4. Maintain consistent fake data patterns
5. Regular testing with new database migrations 