# Database Package

This directory contains all database-related code for the PupMatch backend.

## Structure

```
db/
├── __init__.py              # Package initialization, exports database utilities
├── database.py              # Database connection and session management
├── models/                  # SQLAlchemy ORM models
│   ├── __init__.py         # Model exports
│   ├── user.py             # User authentication model
│   ├── profile.py          # Profile, Photo, Prompt, UserPreferences models
│   ├── matching.py         # Like, Pass, Match models
│   ├── messaging.py        # Conversation, Message models
│   └── playground.py       # Playground model with PostGIS geometry
├── migrations/             # Alembic database migrations
│   ├── alembic.ini         # Alembic configuration
│   └── alembic/            # Migration scripts
│       ├── env.py          # Alembic environment configuration
│       ├── script.py.mako  # Migration template
│       └── versions/       # Migration version files
└── scripts/                # Database utility scripts
    ├── init_db.sql         # SQL initialization script
    ├── setup_database.py   # Automated database setup
    └── test_migrations.py  # Migration testing script
```

## Usage

### Database Connection

```python
from db import get_db, Base, engine

# Get database session (FastAPI dependency)
async def some_endpoint(db: AsyncSession = Depends(get_db)):
    # Use db session
    pass
```

### Models

```python
from db.models import User, Profile, Match, Message

# Use models in your code
user = User(id="123", email="user@example.com")
```

### Migrations

```bash
# Run migrations from backend directory
alembic -c db/migrations/alembic.ini upgrade head

# Create new migration
alembic -c db/migrations/alembic.ini revision --autogenerate -m "description"

# Rollback migration
alembic -c db/migrations/alembic.ini downgrade -1
```

### Setup Scripts

```bash
# Set up database with PostGIS
python3 db/scripts/setup_database.py

# Test migrations
python3 db/scripts/test_migrations.py
```

## Key Features

- **Async SQLAlchemy 2.0**: All database operations use async/await
- **PostGIS Support**: Geospatial queries for location-based matching
- **Connection Pooling**: Configured for high concurrency (20 + 10 overflow)
- **Type Safety**: Full type hints with Mapped types
- **Comprehensive Indexes**: 30+ indexes for query performance
- **Cascade Deletion**: Proper referential integrity

## Models Overview

| Model | Description |
|-------|-------------|
| User | Authentication with email/password |
| Profile | User profile with puppy information |
| Photo | Profile photos (2-6 per profile) |
| Prompt | Profile prompts and answers |
| UserPreferences | Matching preferences (age, distance, activity) |
| Like | User likes on other profiles |
| Pass | User passes on other profiles |
| Match | Mutual likes between users |
| Conversation | Chat threads between matched users |
| Message | Individual messages in conversations |
| Playground | Favorite playground locations with GPS coordinates |

## Documentation

- **Setup Guide**: `../DATABASE_SETUP.md`
- **Quick Start**: `../QUICKSTART.md`
- **Implementation Summary**: `../IMPLEMENTATION_SUMMARY.md`
