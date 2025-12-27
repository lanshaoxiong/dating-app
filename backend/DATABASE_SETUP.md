# Database Setup Guide

This guide explains how to set up the PostgreSQL database with PostGIS extension for PupMatch.

## Prerequisites

- PostgreSQL 14+ installed
- Python 3.11+ with dependencies installed
- Access to create databases and extensions

## Quick Start

### 1. Install PostgreSQL and PostGIS

**macOS (using Homebrew):**
```bash
brew install postgresql@14 postgis
brew services start postgresql@14
```

**Ubuntu/Debian:**
```bash
sudo apt-get update
sudo apt-get install postgresql-14 postgresql-14-postgis-3
sudo systemctl start postgresql
```

**Windows:**
- Download and install PostgreSQL from https://www.postgresql.org/download/windows/
- PostGIS is included in the installer (select it during installation)

### 2. Create Database and Enable PostGIS

**Option A: Using Python script (Recommended)**
```bash
cd backend
python3 db/scripts/setup_database.py
```

This script will:
- Create the `pupmatch` database if it doesn't exist
- Enable the PostGIS extension
- Verify the setup
- Display connection pool configuration

**Option B: Using SQL script**
```bash
# Connect to PostgreSQL
psql -U postgres

# Create database
CREATE DATABASE pupmatch;

# Connect to the database
\c pupmatch

# Enable PostGIS
CREATE EXTENSION IF NOT EXISTS postgis;

# Verify installation
SELECT PostGIS_Version();
```

### 3. Configure Environment Variables

Create or update `backend/.env`:
```env
DATABASE_URL=postgresql+asyncpg://postgres:postgres@localhost:5432/pupmatch
DATABASE_POOL_SIZE=20
DATABASE_MAX_OVERFLOW=10
```

Adjust the connection string based on your PostgreSQL setup:
- Username: `postgres` (or your PostgreSQL user)
- Password: `postgres` (or your PostgreSQL password)
- Host: `localhost` (or your PostgreSQL host)
- Port: `5432` (default PostgreSQL port)
- Database: `pupmatch`

### 4. Run Migrations

Apply all database migrations:
```bash
cd backend
alembic -c db/migrations/alembic.ini upgrade head
```

### 5. Verify Setup

Check that everything is working:
```bash
# Check current migration version
alembic -c db/migrations/alembic.ini current

# View migration history
alembic -c db/migrations/alembic.ini history

# Run migration tests
python3 db/scripts/test_migrations.py
```

## Database Schema

The database includes the following tables:

### Core Tables
- **users**: User accounts with authentication
- **profiles**: User profiles with puppy information
- **photos**: Profile photos (2-6 per profile)
- **prompts**: Profile prompts and answers
- **user_preferences**: Matching preferences (age, distance, activity level)

### Matching Tables
- **likes**: User likes on other profiles
- **passes**: User passes on other profiles
- **matches**: Mutual likes between users

### Messaging Tables
- **conversations**: Chat threads between matched users
- **messages**: Individual messages in conversations

### Location Tables
- **playgrounds**: Favorite playground locations with PostGIS geometry

## PostGIS Features

The database uses PostGIS for geospatial queries:

### Geometry Columns
- `profiles.location`: User location (POINT)
- `playgrounds.location`: Playground location (POINT)

### Spatial Indexes
- `idx_profiles_location`: GIST index on profile locations
- `idx_playgrounds_location`: GIST index on playground locations

### Example Spatial Queries

**Find profiles within 25 miles:**
```sql
SELECT p.* 
FROM profiles p
WHERE ST_DWithin(
    p.location::geography,
    ST_SetSRID(ST_MakePoint(-122.4194, 37.7749), 4326)::geography,
    40233.6  -- 25 miles in meters
);
```

**Calculate distance between two points:**
```sql
SELECT ST_Distance(
    ST_SetSRID(ST_MakePoint(-122.4194, 37.7749), 4326)::geography,
    ST_SetSRID(ST_MakePoint(-118.2437, 34.0522), 4326)::geography
) / 1609.34 AS distance_miles;
```

## Migration Management

### Create a New Migration

After modifying models:
```bash
alembic -c db/migrations/alembic.ini revision --autogenerate -m "description of changes"
```

### Apply Migrations
```bash
# Upgrade to latest
alembic -c db/migrations/alembic.ini upgrade head

# Upgrade to specific revision
alembic -c db/migrations/alembic.ini upgrade <revision_id>

# Upgrade one step
alembic -c db/migrations/alembic.ini upgrade +1
```

### Rollback Migrations
```bash
# Downgrade one step
alembic -c db/migrations/alembic.ini downgrade -1

# Downgrade to specific revision
alembic -c db/migrations/alembic.ini downgrade <revision_id>

# Downgrade all
alembic -c db/migrations/alembic.ini downgrade base
```

### View Migration Status
```bash
# Current revision
alembic -c db/migrations/alembic.ini current

# Migration history
alembic -c db/migrations/alembic.ini history

# Show SQL without executing
alembic -c db/migrations/alembic.ini upgrade head --sql
```

## Connection Pooling

The application uses SQLAlchemy's connection pooling:

- **Pool Size**: 20 connections (configurable via `DATABASE_POOL_SIZE`)
- **Max Overflow**: 10 additional connections (configurable via `DATABASE_MAX_OVERFLOW`)
- **Total Max Connections**: 30 (pool_size + max_overflow)

This configuration supports:
- High concurrent request handling
- Efficient connection reuse
- Automatic connection recycling

## Troubleshooting

### PostGIS Extension Not Found
```bash
# Check if PostGIS is installed
psql -U postgres -c "SELECT * FROM pg_available_extensions WHERE name = 'postgis';"

# If not installed, install PostGIS package for your system
```

### Connection Refused
```bash
# Check if PostgreSQL is running
pg_isready

# Start PostgreSQL (macOS)
brew services start postgresql@14

# Start PostgreSQL (Linux)
sudo systemctl start postgresql
```

### Permission Denied
```bash
# Grant superuser privileges (if needed)
psql -U postgres -c "ALTER USER your_user WITH SUPERUSER;"
```

### Migration Conflicts
```bash
# Check current state
alembic -c db/migrations/alembic.ini current

# If stuck, you can stamp the database to a specific revision
alembic -c db/migrations/alembic.ini stamp head

# Then try upgrading again
alembic -c db/migrations/alembic.ini upgrade head
```

## Performance Tips

1. **Indexes**: All frequently queried columns have indexes
2. **Spatial Indexes**: GIST indexes on geometry columns for fast spatial queries
3. **Connection Pooling**: Configured for optimal performance
4. **Async Operations**: All database operations use async/await for non-blocking I/O

## Security Notes

1. **Never commit `.env` files** with real credentials
2. **Use strong passwords** for production databases
3. **Enable SSL** for production database connections
4. **Restrict database access** to application servers only
5. **Regular backups** are essential for production

## Backup and Restore

### Backup
```bash
pg_dump -U postgres pupmatch > backup.sql
```

### Restore
```bash
psql -U postgres pupmatch < backup.sql
```

### Backup with PostGIS
```bash
pg_dump -U postgres -Fc pupmatch > backup.dump
```

### Restore from custom format
```bash
pg_restore -U postgres -d pupmatch backup.dump
```
