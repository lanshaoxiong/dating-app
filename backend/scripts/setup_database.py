"""Database setup script for PupMatch

This script:
1. Creates the database if it doesn't exist
2. Enables PostGIS extension
3. Verifies the setup
"""

import asyncio
import sys
from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine

from app.config import settings


async def setup_database():
    """Set up PostgreSQL database with PostGIS extension"""
    
    # Parse database URL to get connection info
    db_url = settings.DATABASE_URL
    
    # Create connection to postgres database (not pupmatch)
    # to create the pupmatch database if needed
    base_url = db_url.rsplit('/', 1)[0] + '/postgres'
    
    print("Connecting to PostgreSQL...")
    engine = create_async_engine(base_url, isolation_level="AUTOCOMMIT")
    
    try:
        async with engine.connect() as conn:
            # Check if database exists
            result = await conn.execute(
                text("SELECT 1 FROM pg_database WHERE datname = 'pupmatch'")
            )
            exists = result.scalar()
            
            if not exists:
                print("Creating pupmatch database...")
                await conn.execute(text("CREATE DATABASE pupmatch"))
                print("✓ Database created")
            else:
                print("✓ Database already exists")
    
    finally:
        await engine.dispose()
    
    # Now connect to pupmatch database to enable PostGIS
    print("\nEnabling PostGIS extension...")
    engine = create_async_engine(settings.DATABASE_URL)
    
    try:
        async with engine.connect() as conn:
            # Enable PostGIS extension
            await conn.execute(text("CREATE EXTENSION IF NOT EXISTS postgis"))
            await conn.commit()
            
            # Verify PostGIS installation
            result = await conn.execute(text("SELECT PostGIS_Version()"))
            version = result.scalar()
            print(f"✓ PostGIS enabled (version: {version})")
            
            # Verify connection pooling settings
            print(f"\n✓ Connection pool configured:")
            print(f"  - Pool size: {settings.DATABASE_POOL_SIZE}")
            print(f"  - Max overflow: {settings.DATABASE_MAX_OVERFLOW}")
            
    finally:
        await engine.dispose()
    
    print("\n✅ Database setup complete!")
    return True


async def verify_setup():
    """Verify database setup"""
    print("\nVerifying database setup...")
    
    engine = create_async_engine(settings.DATABASE_URL)
    
    try:
        async with engine.connect() as conn:
            # Check PostGIS
            result = await conn.execute(
                text("SELECT EXISTS(SELECT 1 FROM pg_extension WHERE extname = 'postgis')")
            )
            has_postgis = result.scalar()
            
            if has_postgis:
                print("✓ PostGIS extension is enabled")
            else:
                print("✗ PostGIS extension is NOT enabled")
                return False
            
            # Test a simple geospatial query
            result = await conn.execute(
                text("SELECT ST_Distance(ST_MakePoint(0, 0), ST_MakePoint(1, 1))")
            )
            distance = result.scalar()
            print(f"✓ PostGIS functions working (test distance: {distance:.4f})")
            
    finally:
        await engine.dispose()
    
    return True


if __name__ == "__main__":
    try:
        asyncio.run(setup_database())
        asyncio.run(verify_setup())
    except Exception as e:
        print(f"\n❌ Error: {e}", file=sys.stderr)
        sys.exit(1)
