# Quick Start: Database Setup

## Prerequisites Check

Before starting, verify you have:
- [ ] Python 3.11+ installed
- [ ] PostgreSQL 14+ installed (or Docker)

## Option 1: Local PostgreSQL (macOS)

### Step 1: Install PostgreSQL with PostGIS

```bash
# Install using Homebrew
brew install postgresql@14 postgis

# Start PostgreSQL
brew services start postgresql@14

# Verify it's running
pg_isready
```

### Step 2: Set Up Database

```bash
# Navigate to backend directory
cd backend

# Install Python dependencies
pip install -r requirements.txt

# Run database setup script
python3 db/scripts/setup_database.py
```

### Step 3: Run Migrations

```bash
# Apply database schema
alembic -c db/migrations/alembic.ini upgrade head

# Verify migrations
alembic -c db/migrations/alembic.ini current
```

### Step 4: Verify Setup

```bash
# Test database connection
python3 verify_setup.py
```

---

## Option 2: Docker (Easiest)

### Step 1: Start PostgreSQL Container

```bash
# Run PostgreSQL with PostGIS
docker run -d \
  --name pupmatch-db \
  -e POSTGRES_PASSWORD=postgres \
  -e POSTGRES_DB=pupmatch \
  -p 5432:5432 \
  postgis/postgis:14-3.3

# Verify container is running
docker ps
```

### Step 2: Install Dependencies & Run Migrations

```bash
cd backend

# Install Python dependencies
pip install -r requirements.txt

# Apply database schema
alembic -c db/migrations/alembic.ini upgrade head
```

### Step 3: Verify Setup

```bash
# Test database connection
python3 verify_setup.py
```

---

## Configuration

### Environment Variables

Create `backend/.env` file (copy from `.env.example`):

```env
# Database Configuration
DATABASE_URL=postgresql+asyncpg://postgres:postgres@localhost:5432/pupmatch
DATABASE_POOL_SIZE=20
DATABASE_MAX_OVERFLOW=10

# For cloud database, use format:
# DATABASE_URL=postgresql+asyncpg://username:password@host:port/database
```

### Connection String Format

```
postgresql+asyncpg://[user]:[password]@[host]:[port]/[database]
```

**Examples:**
- Local: `postgresql+asyncpg://postgres:postgres@localhost:5432/pupmatch`
- Docker: `postgresql+asyncpg://postgres:postgres@localhost:5432/pupmatch`
- Cloud: `postgresql+asyncpg://user:pass@db.example.com:5432/pupmatch`

---

## Troubleshooting

### PostgreSQL Not Running

```bash
# macOS - Start PostgreSQL
brew services start postgresql@14

# Check if running
pg_isready

# Check logs
brew services info postgresql@14
```

### Connection Refused

```bash
# Check if PostgreSQL is listening on port 5432
lsof -i :5432

# If port is in use by another process, stop it or change port
```

### PostGIS Extension Error

```bash
# Connect to database
psql -U postgres -d pupmatch

# Enable PostGIS manually
CREATE EXTENSION IF NOT EXISTS postgis;

# Verify
SELECT PostGIS_Version();
```

### Permission Denied

```bash
# Grant superuser privileges (if needed)
psql -U postgres -c "ALTER USER postgres WITH SUPERUSER;"
```

---

## Next Steps

After database setup:

1. ✅ Database is running
2. ✅ PostGIS extension enabled
3. ✅ Migrations applied
4. ✅ Connection verified

**You're ready to start the backend server!**

```bash
cd backend
uvicorn app.main:app --reload
```

---

## Useful Commands

### Database Management

```bash
# Check current migration
alembic -c db/migrations/alembic.ini current

# View migration history
alembic -c db/migrations/alembic.ini history

# Rollback one migration
alembic -c db/migrations/alembic.ini downgrade -1

# Upgrade to latest
alembic -c db/migrations/alembic.ini upgrade head
```

### PostgreSQL Commands

```bash
# Connect to database
psql -U postgres -d pupmatch

# List databases
\l

# List tables
\dt

# Describe table
\d users

# Exit
\q
```

### Docker Commands

```bash
# Stop database
docker stop pupmatch-db

# Start database
docker start pupmatch-db

# Remove database (WARNING: deletes all data)
docker rm -f pupmatch-db

# View logs
docker logs pupmatch-db
```

---

## Production Deployment

For production, consider:

1. **Managed Database Service:**
   - AWS RDS with PostGIS
   - Supabase (PostgreSQL with PostGIS built-in)
   - Google Cloud SQL
   - Railway or Render

2. **Update Environment Variables:**
   ```env
   DATABASE_URL=postgresql+asyncpg://user:pass@production-host:5432/pupmatch
   ```

3. **Enable SSL:**
   ```env
   DATABASE_URL=postgresql+asyncpg://user:pass@host:5432/pupmatch?ssl=require
   ```

4. **Run Migrations:**
   ```bash
   alembic -c db/migrations/alembic.ini upgrade head
   ```

---

## Need Help?

- 📖 Full documentation: `DATABASE_SETUP.md`
- 🐛 Issues: Check troubleshooting section above
- 💬 Questions: Open an issue on GitHub
