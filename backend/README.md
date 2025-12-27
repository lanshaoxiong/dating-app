# PupMatch Backend API

Backend API for PupMatch - A puppy dating application built with FastAPI, GraphQL, PostgreSQL, and Redis.

## Technology Stack

- **Framework**: FastAPI with Strawberry GraphQL
- **Database**: PostgreSQL with PostGIS extension
- **Cache**: Redis
- **Background Jobs**: Celery
- **Storage**: AWS S3
- **Authentication**: JWT tokens
- **ORM**: SQLAlchemy 2.0 (async)
- **Testing**: pytest, Hypothesis

---

## 🚀 Quick Setup (5 minutes)

### 1. Install Dependencies

```bash
cd backend

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install Python packages
pip install -r requirements.txt
```

### 2. Install & Start Services

```bash
# Install PostgreSQL with PostGIS and Redis
brew install postgresql@14 postgis redis

# Start services
brew services start postgresql@14
brew services start redis
```

### 3. Setup Database

```bash
# Run automated setup
python3 db/scripts/setup_database.py

# Apply migrations
alembic -c db/migrations/alembic.ini upgrade head

# Verify everything works
python3 db/scripts/checkpoint_verify.py
```

### 4. Start the Server

```bash
uvicorn app.main:app --reload
```

Visit http://localhost:8000/docs for API documentation.

---

## 📁 Project Structure

```
backend/
├── app/                          # Application Layer
│   ├── main.py                  # FastAPI entry point
│   ├── config.py                # Configuration (env vars)
│   ├── redis_client.py          # Redis client
│   ├── celery_app.py            # Background jobs
│   ├── schemas/                 # Pydantic schemas
│   └── services/                # Business logic
│
├── db/                           # Database Layer
│   ├── database.py              # Connection management
│   ├── models/                  # SQLAlchemy models (11 tables)
│   ├── migrations/              # Alembic migrations
│   ├── scripts/                 # Setup & utility scripts
│   ├── tests/                   # Database tests
│   └── README.md                # Database documentation
│
├── tests/                        # Application Tests
│   ├── conftest.py              # Pytest config
│   ├── test_config.py           # Config tests
│   └── test_redis_connection.py # Redis tests
│
├── .env                          # Environment variables
├── requirements.txt              # Dependencies
└── README.md                     # This file
```

### Layer Responsibilities

- **`app/`** - API endpoints, business logic, external integrations
- **`db/`** - Data persistence, schema management, database utilities
- **`tests/`** - Application tests (API, services, integration)
- **`db/tests/`** - Database tests (models, migrations, connections)

---

## 🔧 Common Commands

### Database
```bash
# Setup database
python3 db/scripts/setup_database.py

# Run migrations
alembic -c db/migrations/alembic.ini upgrade head

# Verify setup
python3 db/scripts/checkpoint_verify.py

# Test database
pytest db/tests/ -v
```

### Development
```bash
# Start API server
uvicorn app.main:app --reload

# Start Celery worker
celery -A app.celery_app worker --loglevel=info

# Run all tests
pytest

# Run with coverage
pytest --cov=app --cov=db
```

### Services
```bash
# Start PostgreSQL
brew services start postgresql@14

# Start Redis
brew services start redis

# Check service status
brew services list
```

---

## 🗄️ Database

See **[db/README.md](db/README.md)** for complete database documentation.

### Quick Reference

**11 Tables:**
- `users`, `profiles`, `photos`, `prompts`, `user_preferences`
- `likes`, `passes`, `matches`
- `conversations`, `messages`
- `playgrounds`

**Key Features:**
- PostGIS for geospatial queries
- Async SQLAlchemy 2.0
- 30+ indexes (including spatial GIST)
- Connection pooling (20 + 10 overflow)
- Cascade deletion

**Import Models:**
```python
from db.database import Base, get_db, engine
from db.models import User, Profile, Match, Message, Playground
```

---

## ⚙️ Configuration

Create `backend/.env` (copy from `.env.example`):

```env
# Database
DATABASE_URL=postgresql+asyncpg://postgres:postgres@localhost:5432/pupmatch
DATABASE_POOL_SIZE=20
DATABASE_MAX_OVERFLOW=10

# Redis
REDIS_URL=redis://localhost:6379/0
REDIS_MAX_CONNECTIONS=50

# Security
SECRET_KEY=your-secret-key-here
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=1440

# AWS S3
AWS_ACCESS_KEY_ID=your-key
AWS_SECRET_ACCESS_KEY=your-secret
S3_BUCKET_NAME=pupmatch-photos

# CORS
ALLOWED_ORIGINS=["http://localhost:3000","http://localhost:19006"]
```

---

## 🧪 Testing

```bash
# Run all tests
pytest

# Run specific test suite
pytest tests/              # Application tests
pytest db/tests/           # Database tests

# Run with coverage
pytest --cov=app --cov=db --cov-report=html

# Run property-based tests only
pytest -m property
```

---

## 🐛 Troubleshooting

### PostgreSQL not connecting
```bash
brew services start postgresql@14
pg_isready
```

### Redis not connecting
```bash
brew services start redis
redis-cli ping
```

### Migration errors
```bash
alembic -c db/migrations/alembic.ini current
alembic -c db/migrations/alembic.ini downgrade -1
alembic -c db/migrations/alembic.ini upgrade head
```

### Import errors
```bash
source venv/bin/activate
pip install -r requirements.txt
```

---

## 🚀 API Documentation

Once the server is running:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **GraphQL Playground**: http://localhost:8000/graphql

---

## 📖 Development

### Code Style

```bash
black app/ tests/
isort app/ tests/
mypy app/
```

### Import Conventions

```python
# Database
from db.database import Base, get_db, engine
from db.models import User, Profile, Match

# Application
from app.config import settings
from app.main import app
from app.services.auth import AuthService  # When implemented
```

---

## 🏗️ Next Steps

1. ✅ Database setup complete
2. ⏭️ Implement authentication service (Task 4)
3. ⏭️ Implement profile management (Task 5)
4. ⏭️ Add GraphQL layer
5. ⏭️ Add WebSocket support

See [.kiro/specs/backend-api/tasks.md](../.kiro/specs/backend-api/tasks.md) for the full implementation plan.

---

## 📚 Additional Documentation

- **[db/README.md](db/README.md)** - Complete database documentation (setup, models, migrations, PostGIS)

---

## 💡 Tips

- Always activate virtual environment: `source venv/bin/activate`
- Run scripts from `backend` directory
- Use `db/scripts/checkpoint_verify.py` to diagnose issues
- Check `db/README.md` for database details

---

## License

Proprietary - PupMatch Team
