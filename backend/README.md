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

## Project Structure

```
backend/
├── app/
│   ├── __init__.py
│   ├── main.py              # FastAPI application entry point
│   ├── config.py            # Configuration settings
│   ├── database.py          # Database connection
│   ├── redis_client.py      # Redis client
│   ├── celery_app.py        # Celery configuration
│   ├── models/              # SQLAlchemy models
│   ├── schemas/             # Pydantic schemas
│   └── services/            # Business logic
├── tests/                   # Test suite
├── .env                     # Environment variables
├── pyproject.toml           # Poetry dependencies
└── requirements.txt         # Pip dependencies
```

## Setup

### Prerequisites

- Python 3.11+
- PostgreSQL 14+ with PostGIS extension
- Redis 6+
- AWS account (for S3 storage)

### Installation

1. **Install dependencies** (choose one):

   Using Poetry:
   ```bash
   poetry install
   ```

   Using pip:
   ```bash
   pip install -r requirements.txt
   ```

2. **Configure environment variables**:
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

3. **Set up PostgreSQL database**:
   ```sql
   CREATE DATABASE pupmatch;
   CREATE DATABASE pupmatch_test;
   \c pupmatch
   CREATE EXTENSION postgis;
   \c pupmatch_test
   CREATE EXTENSION postgis;
   ```

4. **Run database migrations**:
   ```bash
   alembic upgrade head
   ```

### Running the Application

1. **Start the API server**:
   ```bash
   uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
   ```

2. **Start Celery worker** (in another terminal):
   ```bash
   celery -A app.celery_app worker --loglevel=info
   ```

3. **Start Celery beat** (for scheduled tasks):
   ```bash
   celery -A app.celery_app beat --loglevel=info
   ```

### API Documentation

Once the server is running, visit:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc
- GraphQL Playground: http://localhost:8000/graphql

## Testing

Run all tests:
```bash
pytest
```

Run with coverage:
```bash
pytest --cov=app --cov-report=html
```

Run property-based tests only:
```bash
pytest -m property
```

## Development

### Code Style

This project follows PEP 8 style guidelines. Format code with:
```bash
black app/ tests/
isort app/ tests/
```

### Type Checking

Run type checking with:
```bash
mypy app/
```

## Environment Variables

See `.env.example` for all available configuration options.

Key variables:
- `DATABASE_URL`: PostgreSQL connection string
- `REDIS_URL`: Redis connection string
- `SECRET_KEY`: JWT secret key
- `AWS_ACCESS_KEY_ID`: AWS access key
- `AWS_SECRET_ACCESS_KEY`: AWS secret key
- `S3_BUCKET_NAME`: S3 bucket for photo storage

## License

Proprietary - PupMatch Team
