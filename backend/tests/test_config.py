"""Tests for configuration loading"""

import pytest
from app.config import settings


def test_environment_variable_loading():
    """Test that environment variables are loaded correctly"""
    assert settings.APP_NAME == "PupMatch API"
    assert settings.JWT_ALGORITHM == "HS256"
    assert settings.ACCESS_TOKEN_EXPIRE_MINUTES == 1440


def test_database_configuration():
    """Test database configuration is set"""
    assert settings.DATABASE_URL is not None
    assert "postgresql" in settings.DATABASE_URL
    assert settings.DATABASE_POOL_SIZE > 0
    assert settings.DATABASE_MAX_OVERFLOW > 0


def test_redis_configuration():
    """Test Redis configuration is set"""
    assert settings.REDIS_URL is not None
    assert "redis" in settings.REDIS_URL
    assert settings.REDIS_MAX_CONNECTIONS > 0


def test_security_configuration():
    """Test security settings are configured"""
    assert settings.SECRET_KEY is not None
    assert len(settings.SECRET_KEY) > 0
    assert settings.ALLOWED_ORIGINS is not None
    assert len(settings.ALLOWED_ORIGINS) > 0


def test_rate_limiting_configuration():
    """Test rate limiting settings"""
    assert settings.RATE_LIMIT_PER_USER > 0
    assert settings.RATE_LIMIT_PER_IP > 0


def test_file_upload_configuration():
    """Test file upload settings"""
    assert settings.MAX_UPLOAD_SIZE > 0
    assert len(settings.ALLOWED_IMAGE_TYPES) > 0
    assert "image/jpeg" in settings.ALLOWED_IMAGE_TYPES


def test_cache_ttl_configuration():
    """Test cache TTL settings"""
    assert settings.CACHE_TTL_PROFILE > 0
    assert settings.CACHE_TTL_RECOMMENDATIONS > 0
    assert settings.CACHE_TTL_SESSION > 0
