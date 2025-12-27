# Database Module

Complete database setup, models, migrations, and utilities for PupMatch backend.

## Quick Start

### 1. Install PostgreSQL & PostGIS

**macOS:**
```bash
brew install postgresql@14 postgis
brew services start postgresql@14
```

**Docker:**
```bash
docker run -d --name pupmatch-db \
  -e POSTGRES_PASSWORD=postgres \
  -e POSTGRES_DB=pupmatch \
  -p 5432:5432 \
  postgis/postgis:14-3.3
```

### 2. Setup Database

```bash
cd backend
pip install -r requirements.txt
python3 db/scripts/setup_database.py
alembic -c db/migrations/alembic.ini upgrade head
```

### 3. Verify

```bash
python3 db/scripts/checkpoint_verify.py
```

---

## Structure

```
db/
├── database.py              # Connection & session management
├── models/                  # SQLAlchemy ORM models
│   ├── user.py             # User authentication
│   ├── profile.py          # Profile, Photo, Prompt, Preferences
│   ├── matching.py         # Like, Pass, Match
│   ├── messaging.py        # Conversation, Message
│   └── playground.py       # Playground locations (PostGIS)
├── migrations/              # Alembic migrations
│   ├── alembic.ini
│   └── alembic/versions/   # Migration files
├── scripts/                 # Utility scripts
│   ├── setup_database.py   # Automated setup
│   ├── checkpoint_verify.py # Verification
│   └── test_migrations.py  # Migration testing
└── tests/                   # Database tests
    └── test_database_setup.py
```

---

## Database Schema

### Tables (11 total)

**Core:**
- `users` - Authentication (email, password_hash)
- `profiles` - User profiles with location (PostGIS POINT)
- `photos` - Profile photos (2-6 per profile, ordered)
- `prompts` - Profile prompts and answers
- `user_preferences` - Matching preferences (age, distance, activity)

**Matching:**
- `likes` - User likes on profiles
- `passes` - User passes on profiles
- `matches` - Mutual likes

**Messaging:**
- `conversations` - Chat threads between matches
- `messages` - Individual messages

**Location:**
- `playgrounds` - Favorite locations with GPS coordinates (PostGIS POINT)

### Key Features

- **PostGIS** - Geospatial queries for location-based matching
- **Async SQLAlchemy 2.0** - Non-blocking database operations
- **30+ Indexes** - Including spatial GIST indexes
- **Connection Pooling** - 20 connections + 10 overflow
- **Cascade Deletion** - Automatic cleanup of related data
- **Type Safety** - Full type hints with Mapped types

---

## Usage

### Import Models

```python
from db.database import Base, get_db, engine
from db.models import User, Profile, Match, Message, Playground
```

### Database Session

```python
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from db import get_db

async def endpoint(db: AsyncSession = Depends(get_db)):
    # Use db session
    result = await db.execute(select(User))
    users = result.scalars().all()
```

---

## Migrations

### Common Commands

```bash
# Apply migrations
alembic -c db/migrations/alembic.ini upgrade head

# Create new migration
alembic -c db/migrations/alembic.ini revision --autogenerate -m "description"

# Rollback one step
alembic -c db/migrations/alembic.ini downgrade -1

# Check current version
alembic -c db/migrations/alembic.ini current

# View history
alembic -c db/migrations/alembic.ini history
```

---

## Configuration

Set in `backend/.env`:

```env
DATABASE_URL=postgresql+asyncpg://postgres:postgres@localhost:5432/pupmatch
DATABASE_POOL_SIZE=20
DATABASE_MAX_OVERFLOW=10
```

**Connection String Format:**
```
postgresql+asyncpg://[user]:[password]@[host]:[port]/[database]
```

---

## PostGIS Spatial Queries

### Find Nearby Profiles (within 25 miles)

```sql
SELECT p.* 
FROM profiles p
WHERE ST_DWithin(
    p.location::geography,
    ST_SetSRID(ST_MakePoint(-122.4194, 37.7749), 4326)::geography,
    40233.6  -- 25 miles in meters
);
```

### Calculate Distance

```sql
SELECT ST_Distance(
    ST_SetSRID(ST_MakePoint(lon1, lat1), 4326)::geography,
    ST_SetSRID(ST_MakePoint(lon2, lat2), 4326)::geography
) / 1609.34 AS distance_miles;
```

---

## Scripts

### Setup & Verification

```bash
# Automated database setup
python3 db/scripts/setup_database.py

# Comprehensive verification
python3 db/scripts/checkpoint_verify.py

# Test migrations
python3 db/scripts/test_migrations.py
```

### What checkpoint_verify.py Checks

1. ✅ All required files exist
2. ✅ Database connection works
3. ✅ PostGIS extension enabled
4. ✅ All tables created
5. ✅ Indexes and constraints exist
6. ✅ Redis connection works
7. ✅ All tests pass

---

## Testing

```bash
# Run database tests
pytest db/tests/ -v

# Run all tests
pytest tests/ db/tests/ -v
```

---

## Troubleshooting

### PostgreSQL Not Running

```bash
# macOS
brew services start postgresql@14
pg_isready

# Docker
docker start pupmatch-db
docker ps
```

### PostGIS Extension Missing

```bash
psql -U postgres -d pupmatch
CREATE EXTENSION IF NOT EXISTS postgis;
SELECT PostGIS_Version();
```

### Migration Errors

```bash
# Check current state
alembic -c db/migrations/alembic.ini current

# Rollback and retry
alembic -c db/migrations/alembic.ini downgrade -1
alembic -c db/migrations/alembic.ini upgrade head
```

---

## Implementation Details

### Models (11 total)

All models use:
- Async SQLAlchemy 2.0 with `Mapped` type hints
- UUID primary keys (String(36))
- Automatic timestamps (`created_at`, `updated_at`)
- Cascade deletion for referential integrity
- Proper indexes on foreign keys and frequently queried fields

### Spatial Data

- **SRID 4326** - WGS84 coordinate system (standard GPS)
- **Geometry Type** - POINT for locations
- **GIST Indexes** - Fast spatial queries
- **Geography Casting** - Accurate distance calculations

### Connection Pooling

- **Pool Size**: 20 connections
- **Max Overflow**: 10 additional connections
- **Total Capacity**: 30 concurrent connections
- **Async Engine**: Non-blocking I/O

---

## Production Considerations

### Managed Database Services

- AWS RDS with PostGIS
- Supabase (PostgreSQL + PostGIS built-in)
- Google Cloud SQL
- Railway or Render

### Security

```env
# Enable SSL
DATABASE_URL=postgresql+asyncpg://user:pass@host:5432/db?ssl=require
```

### Backups

```bash
# Backup
pg_dump -U postgres -Fc pupmatch > backup.dump

# Restore
pg_restore -U postgres -d pupmatch backup.dump
```

---

## Requirements

- PostgreSQL 14+ with PostGIS extension
- Python 3.11+
- SQLAlchemy 2.0+
- Alembic
- asyncpg (async PostgreSQL driver)
- GeoAlchemy2 (PostGIS integration)
