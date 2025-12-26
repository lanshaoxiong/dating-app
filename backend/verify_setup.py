"""Verify backend setup without requiring external dependencies"""

import os
import sys
from pathlib import Path


def check_file_exists(filepath: str) -> bool:
    """Check if a file exists"""
    return Path(filepath).exists()


def check_directory_exists(dirpath: str) -> bool:
    """Check if a directory exists"""
    return Path(dirpath).is_dir()


def verify_project_structure():
    """Verify the project structure is correct"""
    print("Verifying PupMatch Backend Project Structure...\n")
    
    checks = {
        "Configuration Files": [
            "pyproject.toml",
            "requirements.txt",
            ".env.example",
            ".env",
            ".gitignore",
            "README.md",
            "alembic.ini",
        ],
        "Application Structure": [
            "app/__init__.py",
            "app/main.py",
            "app/config.py",
            "app/database.py",
            "app/redis_client.py",
            "app/celery_app.py",
        ],
        "Directories": [
            "app/models",
            "app/schemas",
            "app/services",
            "tests",
            "alembic",
            "alembic/versions",
        ],
        "Test Files": [
            "tests/__init__.py",
            "tests/conftest.py",
            "tests/test_config.py",
        ],
        "Alembic Files": [
            "alembic/env.py",
            "alembic/script.py.mako",
        ],
    }
    
    all_passed = True
    
    for category, items in checks.items():
        print(f"📁 {category}:")
        for item in items:
            # Check if it's a directory (no extension or explicit directory)
            if "/" in item and not any(item.endswith(ext) for ext in [".py", ".toml", ".txt", ".ini", ".md", ".mako"]):
                exists = check_directory_exists(item)
            else:
                exists = check_file_exists(item)
            
            symbol = "✅" if exists else "❌"
            print(f"  {symbol} {item}")
            if not exists:
                all_passed = False
        print()
    
    return all_passed


def verify_dependencies():
    """Verify dependencies are listed in requirements.txt"""
    print("Verifying Dependencies...\n")
    
    required_packages = [
        "fastapi",
        "strawberry-graphql",
        "sqlalchemy",
        "pydantic",
        "asyncpg",
        "redis",
        "celery",
        "boto3",
        "python-jose",
        "pytest",
        "hypothesis",
    ]
    
    with open("requirements.txt", "r") as f:
        content = f.read().lower()
    
    all_found = True
    for package in required_packages:
        found = package in content
        symbol = "✅" if found else "❌"
        print(f"  {symbol} {package}")
        if not found:
            all_found = False
    
    print()
    return all_found


def verify_environment_config():
    """Verify environment configuration"""
    print("Verifying Environment Configuration...\n")
    
    required_vars = [
        "DATABASE_URL",
        "REDIS_URL",
        "SECRET_KEY",
        "AWS_ACCESS_KEY_ID",
        "CELERY_BROKER_URL",
    ]
    
    with open(".env.example", "r") as f:
        content = f.read()
    
    all_found = True
    for var in required_vars:
        found = var in content
        symbol = "✅" if found else "❌"
        print(f"  {symbol} {var}")
        if not found:
            all_found = False
    
    print()
    return all_found


def main():
    """Run all verification checks"""
    print("=" * 60)
    print("PupMatch Backend Setup Verification")
    print("=" * 60)
    print()
    
    structure_ok = verify_project_structure()
    deps_ok = verify_dependencies()
    env_ok = verify_environment_config()
    
    print("=" * 60)
    if structure_ok and deps_ok and env_ok:
        print("✅ All checks passed! Backend setup is complete.")
        print("\nNext steps:")
        print("1. Install dependencies: pip install -r requirements.txt")
        print("2. Set up PostgreSQL with PostGIS extension")
        print("3. Set up Redis")
        print("4. Run migrations: alembic upgrade head")
        print("5. Start the server: uvicorn app.main:app --reload")
        return 0
    else:
        print("❌ Some checks failed. Please review the output above.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
