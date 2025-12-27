"""Tests for database setup and connectivity"""

import pytest
import pytest_asyncio
from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine

from app.config import settings


@pytest_asyncio.fixture
async def db_engine():
    """Create a database engine for testing"""
    engine = create_async_engine(settings.DATABASE_URL, echo=False)
    yield engine
    await engine.dispose()


@pytest.mark.asyncio
async def test_database_connection(db_engine):
    """Test that we can connect to the database"""
    async with db_engine.connect() as conn:
        result = await conn.execute(text("SELECT 1"))
        assert result.scalar() == 1


@pytest.mark.asyncio
async def test_postgis_extension_enabled(db_engine):
    """Test that PostGIS extension is enabled"""
    async with db_engine.connect() as conn:
        result = await conn.execute(
            text("SELECT EXISTS(SELECT 1 FROM pg_extension WHERE extname = 'postgis')")
        )
        has_postgis = result.scalar()
        assert has_postgis is True, "PostGIS extension is not enabled"


@pytest.mark.asyncio
async def test_postgis_functions_work(db_engine):
    """Test that PostGIS functions are working"""
    async with db_engine.connect() as conn:
        # Test ST_MakePoint and ST_Distance functions
        result = await conn.execute(
            text("SELECT ST_Distance(ST_MakePoint(0, 0), ST_MakePoint(1, 1))")
        )
        distance = result.scalar()
        assert distance is not None
        assert distance > 0
        
        # Test ST_GeomFromText function
        result = await conn.execute(
            text("SELECT ST_AsText(ST_GeomFromText('POINT(0 0)', 4326))")
        )
        point = result.scalar()
        assert point == "POINT(0 0)"


@pytest.mark.asyncio
async def test_database_tables_exist(db_engine):
    """Test that all required tables exist after migrations"""
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
    
    async with db_engine.connect() as conn:
        for table in expected_tables:
            result = await conn.execute(
                text(f"SELECT EXISTS(SELECT 1 FROM information_schema.tables WHERE table_name = '{table}')")
            )
            exists = result.scalar()
            assert exists is True, f"Table '{table}' does not exist"


@pytest.mark.asyncio
async def test_spatial_indexes_exist(db_engine):
    """Test that spatial indexes are created"""
    async with db_engine.connect() as conn:
        # Check for profiles location index
        result = await conn.execute(
            text("""
                SELECT EXISTS(
                    SELECT 1 FROM pg_indexes 
                    WHERE tablename = 'profiles' 
                    AND indexname = 'idx_profiles_location'
                )
            """)
        )
        has_profiles_index = result.scalar()
        assert has_profiles_index is True, "Spatial index on profiles.location does not exist"
        
        # Check for playgrounds location index
        result = await conn.execute(
            text("""
                SELECT EXISTS(
                    SELECT 1 FROM pg_indexes 
                    WHERE tablename = 'playgrounds' 
                    AND indexname = 'idx_playgrounds_location'
                )
            """)
        )
        has_playgrounds_index = result.scalar()
        assert has_playgrounds_index is True, "Spatial index on playgrounds.location does not exist"


@pytest.mark.asyncio
async def test_enum_types_exist(db_engine):
    """Test that custom enum types are created"""
    async with db_engine.connect() as conn:
        # Check for activity_level_enum
        result = await conn.execute(
            text("SELECT EXISTS(SELECT 1 FROM pg_type WHERE typname = 'activity_level_enum')")
        )
        has_activity_level = result.scalar()
        assert has_activity_level is True, "activity_level_enum type does not exist"
        
        # Check for distance_unit_enum
        result = await conn.execute(
            text("SELECT EXISTS(SELECT 1 FROM pg_type WHERE typname = 'distance_unit_enum')")
        )
        has_distance_unit = result.scalar()
        assert has_distance_unit is True, "distance_unit_enum type does not exist"


@pytest.mark.asyncio
async def test_foreign_key_constraints_exist(db_engine):
    """Test that foreign key constraints are properly set up"""
    async with db_engine.connect() as conn:
        # Check profiles -> users foreign key
        result = await conn.execute(
            text("""
                SELECT EXISTS(
                    SELECT 1 FROM information_schema.table_constraints 
                    WHERE constraint_type = 'FOREIGN KEY' 
                    AND table_name = 'profiles'
                )
            """)
        )
        has_fk = result.scalar()
        assert has_fk is True, "Foreign key constraints on profiles table do not exist"


@pytest.mark.asyncio
async def test_unique_constraints_exist(db_engine):
    """Test that unique constraints are properly set up"""
    async with db_engine.connect() as conn:
        # Check users email unique constraint
        result = await conn.execute(
            text("""
                SELECT EXISTS(
                    SELECT 1 FROM information_schema.table_constraints 
                    WHERE constraint_type = 'UNIQUE' 
                    AND table_name = 'users'
                    AND constraint_name LIKE '%email%'
                )
            """)
        )
        has_unique = result.scalar()
        assert has_unique is True, "Unique constraint on users.email does not exist"
        
        # Check likes unique constraint
        result = await conn.execute(
            text("""
                SELECT EXISTS(
                    SELECT 1 FROM information_schema.table_constraints 
                    WHERE constraint_type = 'UNIQUE' 
                    AND table_name = 'likes'
                    AND constraint_name = 'uq_like_user_target'
                )
            """)
        )
        has_like_unique = result.scalar()
        assert has_like_unique is True, "Unique constraint on likes (user_id, target_id) does not exist"


@pytest.mark.asyncio
async def test_indexes_exist(db_engine):
    """Test that important indexes are created"""
    expected_indexes = [
        ('users', 'ix_users_email'),
        ('profiles', 'ix_profiles_user_id'),
        ('likes', 'ix_likes_user_id'),
        ('likes', 'ix_likes_target_id'),
        ('matches', 'ix_matches_created_at'),
        ('messages', 'ix_messages_conversation_id'),
    ]
    
    async with db_engine.connect() as conn:
        for table, index in expected_indexes:
            result = await conn.execute(
                text(f"""
                    SELECT EXISTS(
                        SELECT 1 FROM pg_indexes 
                        WHERE tablename = '{table}' 
                        AND indexname = '{index}'
                    )
                """)
            )
            exists = result.scalar()
            assert exists is True, f"Index '{index}' on table '{table}' does not exist"


@pytest.mark.asyncio
async def test_cascade_delete_configured(db_engine):
    """Test that cascade delete is properly configured"""
    async with db_engine.connect() as conn:
        # Check that foreign keys have ON DELETE CASCADE
        result = await conn.execute(
            text("""
                SELECT COUNT(*) FROM information_schema.referential_constraints
                WHERE delete_rule = 'CASCADE'
            """)
        )
        cascade_count = result.scalar()
        assert cascade_count > 0, "No CASCADE delete rules found on foreign keys"
