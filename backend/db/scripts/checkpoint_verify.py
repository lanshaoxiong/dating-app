#!/usr/bin/env python3
"""
Checkpoint Verification Script for Task 3

This script verifies that the database setup is complete and working:
1. Checks that all required files exist
2. Verifies database connection
3. Checks PostGIS extension
4. Verifies all tables exist
5. Checks indexes and constraints
6. Tests Redis connection

Run this from the backend directory:
    cd backend
    source venv/bin/activate
    python3 db/scripts/checkpoint_verify.py

Or from the db/scripts directory:
    cd backend/db/scripts
    source ../../venv/bin/activate
    python3 checkpoint_verify.py
"""

import asyncio
import sys
from pathlib import Path
import os

# Add parent directories to path to import app modules
script_dir = Path(__file__).parent
backend_dir = script_dir.parent.parent
sys.path.insert(0, str(backend_dir))

# Change to backend directory for relative paths
os.chdir(backend_dir)

# Color codes for terminal output
GREEN = '\033[92m'
RED = '\033[91m'
YELLOW = '\033[93m'
BLUE = '\033[94m'
RESET = '\033[0m'


def print_header(text):
    """Print a section header"""
    print(f"\n{BLUE}{'=' * 60}{RESET}")
    print(f"{BLUE}{text}{RESET}")
    print(f"{BLUE}{'=' * 60}{RESET}\n")


def print_success(text):
    """Print success message"""
    print(f"{GREEN}✓{RESET} {text}")


def print_error(text):
    """Print error message"""
    print(f"{RED}✗{RESET} {text}")


def print_warning(text):
    """Print warning message"""
    print(f"{YELLOW}⚠{RESET} {text}")


def check_files():
    """Check that all required files exist"""
    print_header("1. Checking File Structure")
    
    required_files = [
        "db/database.py",
        "db/models/__init__.py",
        "db/models/user.py",
        "db/models/profile.py",
        "db/models/matching.py",
        "db/models/messaging.py",
        "db/models/playground.py",
        "db/migrations/alembic.ini",
        "db/migrations/alembic/env.py",
        "db/migrations/alembic/versions/2024_12_26_1430-001_initial_schema.py",
        "app/config.py",
        "app/main.py",
        "tests/conftest.py",
        "tests/test_config.py",
        "db/tests/test_database_setup.py",
        "tests/test_redis_connection.py",
    ]
    
    all_exist = True
    for filepath in required_files:
        if Path(filepath).exists():
            print_success(f"{filepath}")
        else:
            print_error(f"{filepath} - MISSING")
            all_exist = False
    
    return all_exist


async def check_database():
    """Check database connection and setup"""
    print_header("2. Checking Database Connection")
    
    try:
        from sqlalchemy import text
        from sqlalchemy.ext.asyncio import create_async_engine
        from app.config import settings
        
        engine = create_async_engine(settings.DATABASE_URL, echo=False)
        
        try:
            async with engine.connect() as conn:
                # Test basic connection
                result = await conn.execute(text("SELECT 1"))
                if result.scalar() == 1:
                    print_success("Database connection successful")
                else:
                    print_error("Database connection failed")
                    return False
                
                # Check PostGIS extension
                result = await conn.execute(
                    text("SELECT EXISTS(SELECT 1 FROM pg_extension WHERE extname = 'postgis')")
                )
                if result.scalar():
                    print_success("PostGIS extension is enabled")
                else:
                    print_error("PostGIS extension is NOT enabled")
                    return False
                
                # Get PostGIS version
                result = await conn.execute(text("SELECT PostGIS_Version()"))
                version = result.scalar()
                print_success(f"PostGIS version: {version}")
                
                # Test PostGIS functions
                result = await conn.execute(
                    text("SELECT ST_Distance(ST_MakePoint(0, 0), ST_MakePoint(1, 1))")
                )
                distance = result.scalar()
                print_success(f"PostGIS functions working (test distance: {distance:.4f})")
                
                return True
        finally:
            await engine.dispose()
            
    except ImportError as e:
        print_error(f"Missing dependencies: {e}")
        print_warning("Run: pip install -r requirements.txt")
        return False
    except Exception as e:
        print_error(f"Database connection error: {e}")
        print_warning("Make sure PostgreSQL is running and DATABASE_URL is correct in .env")
        return False


async def check_tables():
    """Check that all tables exist"""
    print_header("3. Checking Database Tables")
    
    try:
        from sqlalchemy import text
        from sqlalchemy.ext.asyncio import create_async_engine
        from app.config import settings
        
        engine = create_async_engine(settings.DATABASE_URL, echo=False)
        
        expected_tables = [
            'users',
            'profiles',
            'photos',
            'prompts',
            'user_preferences',
            'likes',
            'passes',
            'matches',
            'conversations',
            'messages',
            'playgrounds',
            'alembic_version'
        ]
        
        try:
            async with engine.connect() as conn:
                all_exist = True
                for table in expected_tables:
                    result = await conn.execute(
                        text(f"SELECT EXISTS(SELECT 1 FROM information_schema.tables WHERE table_name = '{table}')")
                    )
                    if result.scalar():
                        print_success(f"Table '{table}' exists")
                    else:
                        print_error(f"Table '{table}' does NOT exist")
                        all_exist = False
                
                if not all_exist:
                    print_warning("Run migrations: alembic -c db/migrations/alembic.ini upgrade head")
                
                return all_exist
        finally:
            await engine.dispose()
            
    except Exception as e:
        print_error(f"Error checking tables: {e}")
        return False


async def check_indexes():
    """Check that important indexes exist"""
    print_header("4. Checking Database Indexes")
    
    try:
        from sqlalchemy import text
        from sqlalchemy.ext.asyncio import create_async_engine
        from app.config import settings
        
        engine = create_async_engine(settings.DATABASE_URL, echo=False)
        
        important_indexes = [
            ('users', 'ix_users_email'),
            ('profiles', 'ix_profiles_user_id'),
            ('profiles', 'idx_profiles_location'),  # Spatial index
            ('likes', 'ix_likes_user_id'),
            ('matches', 'ix_matches_created_at'),
            ('playgrounds', 'idx_playgrounds_location'),  # Spatial index
        ]
        
        try:
            async with engine.connect() as conn:
                all_exist = True
                for table, index in important_indexes:
                    result = await conn.execute(
                        text(f"""
                            SELECT EXISTS(
                                SELECT 1 FROM pg_indexes 
                                WHERE tablename = '{table}' 
                                AND indexname = '{index}'
                            )
                        """)
                    )
                    if result.scalar():
                        print_success(f"Index '{index}' on '{table}'")
                    else:
                        print_error(f"Index '{index}' on '{table}' does NOT exist")
                        all_exist = False
                
                return all_exist
        finally:
            await engine.dispose()
            
    except Exception as e:
        print_error(f"Error checking indexes: {e}")
        return False


async def check_redis():
    """Check Redis connection"""
    print_header("5. Checking Redis Connection")
    
    try:
        import redis.asyncio as redis
        from app.config import settings
        
        client = redis.from_url(settings.REDIS_URL, decode_responses=True)
        
        try:
            # Test ping
            pong = await client.ping()
            if pong:
                print_success("Redis connection successful")
            else:
                print_error("Redis ping failed")
                return False
            
            # Test set/get
            await client.set("checkpoint_test", "success")
            value = await client.get("checkpoint_test")
            if value == "success":
                print_success("Redis set/get operations working")
            else:
                print_error("Redis set/get operations failed")
                return False
            
            # Clean up
            await client.delete("checkpoint_test")
            
            return True
        finally:
            await client.close()
            
    except ImportError as e:
        print_error(f"Missing dependencies: {e}")
        print_warning("Run: pip install -r requirements.txt")
        return False
    except Exception as e:
        print_error(f"Redis connection error: {e}")
        print_warning("Make sure Redis is running and REDIS_URL is correct in .env")
        return False


async def run_tests():
    """Run pytest tests"""
    print_header("6. Running Tests")
    
    try:
        import subprocess
        
        # Run config tests
        print("Running configuration tests...")
        result = subprocess.run(
            ["python3", "-m", "pytest", "tests/test_config.py", "-v"],
            capture_output=True,
            text=True
        )
        
        if result.returncode == 0:
            print_success("Configuration tests passed")
        else:
            print_error("Configuration tests failed")
            print(result.stdout)
            print(result.stderr)
            return False
        
        # Run database tests
        print("\nRunning database setup tests...")
        result = subprocess.run(
            ["python3", "-m", "pytest", "db/tests/test_database_setup.py", "-v"],
            capture_output=True,
            text=True
        )
        
        if result.returncode == 0:
            print_success("Database setup tests passed")
        else:
            print_error("Database setup tests failed")
            print(result.stdout)
            print(result.stderr)
            return False
        
        # Run Redis tests
        print("\nRunning Redis connection tests...")
        result = subprocess.run(
            ["python3", "-m", "pytest", "tests/test_redis_connection.py", "-v"],
            capture_output=True,
            text=True
        )
        
        if result.returncode == 0:
            print_success("Redis connection tests passed")
        else:
            print_error("Redis connection tests failed")
            print(result.stdout)
            print(result.stderr)
            return False
        
        return True
        
    except Exception as e:
        print_error(f"Error running tests: {e}")
        return False


async def main():
    """Run all verification checks"""
    print(f"\n{BLUE}{'=' * 60}{RESET}")
    print(f"{BLUE}Task 3 Checkpoint: Database Setup Verification{RESET}")
    print(f"{BLUE}{'=' * 60}{RESET}")
    
    results = {}
    
    # Check files
    results['files'] = check_files()
    
    # Check database
    results['database'] = await check_database()
    
    # Check tables (only if database connection works)
    if results['database']:
        results['tables'] = await check_tables()
        results['indexes'] = await check_indexes()
    else:
        results['tables'] = False
        results['indexes'] = False
    
    # Check Redis
    results['redis'] = await check_redis()
    
    # Run tests (only if everything else passes)
    if all(results.values()):
        results['tests'] = await run_tests()
    else:
        results['tests'] = False
        print_header("6. Running Tests")
        print_warning("Skipping tests due to previous failures")
    
    # Summary
    print_header("Summary")
    
    for check, passed in results.items():
        if passed:
            print_success(f"{check.capitalize()} check passed")
        else:
            print_error(f"{check.capitalize()} check failed")
    
    print()
    
    if all(results.values()):
        print(f"{GREEN}{'=' * 60}{RESET}")
        print(f"{GREEN}✅ All checks passed! Database setup is complete.{RESET}")
        print(f"{GREEN}{'=' * 60}{RESET}")
        print("\nNext steps:")
        print("  - Task 4: Implement authentication service")
        print("  - Task 5: Implement profile management service")
        return 0
    else:
        print(f"{RED}{'=' * 60}{RESET}")
        print(f"{RED}❌ Some checks failed. Please review the output above.{RESET}")
        print(f"{RED}{'=' * 60}{RESET}")
        print("\nTroubleshooting:")
        print("  1. Install dependencies: pip install -r requirements.txt")
        print("  2. Start PostgreSQL: brew services start postgresql@14")
        print("  3. Start Redis: brew services start redis")
        print("  4. Run migrations: alembic -c db/migrations/alembic.ini upgrade head")
        print("  5. Check .env file has correct DATABASE_URL and REDIS_URL")
        return 1


if __name__ == "__main__":
    sys.exit(asyncio.run(main()))
