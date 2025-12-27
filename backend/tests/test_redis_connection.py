"""Tests for Redis connection"""

import pytest
import redis.asyncio as redis

from app.config import settings


@pytest.fixture
async def redis_client():
    """Create a Redis client for testing"""
    client = redis.from_url(settings.REDIS_URL, decode_responses=True)
    yield client
    await client.close()


@pytest.mark.asyncio
async def test_redis_connection(redis_client):
    """Test that we can connect to Redis"""
    # Test ping
    pong = await redis_client.ping()
    assert pong is True


@pytest.mark.asyncio
async def test_redis_set_get(redis_client):
    """Test basic Redis set and get operations"""
    # Set a test key
    await redis_client.set("test_key", "test_value")
    
    # Get the test key
    value = await redis_client.get("test_key")
    assert value == "test_value"
    
    # Clean up
    await redis_client.delete("test_key")


@pytest.mark.asyncio
async def test_redis_expiration(redis_client):
    """Test Redis key expiration"""
    # Set a key with expiration
    await redis_client.setex("test_expire", 1, "test_value")
    
    # Verify it exists
    value = await redis_client.get("test_expire")
    assert value == "test_value"
    
    # Check TTL
    ttl = await redis_client.ttl("test_expire")
    assert ttl > 0 and ttl <= 1


@pytest.mark.asyncio
async def test_redis_delete(redis_client):
    """Test Redis delete operation"""
    # Set a test key
    await redis_client.set("test_delete", "test_value")
    
    # Delete the key
    result = await redis_client.delete("test_delete")
    assert result == 1
    
    # Verify it's gone
    value = await redis_client.get("test_delete")
    assert value is None


@pytest.mark.asyncio
async def test_redis_hash_operations(redis_client):
    """Test Redis hash operations for caching"""
    # Set hash fields
    await redis_client.hset("test_hash", "field1", "value1")
    await redis_client.hset("test_hash", "field2", "value2")
    
    # Get hash field
    value = await redis_client.hget("test_hash", "field1")
    assert value == "value1"
    
    # Get all hash fields
    all_fields = await redis_client.hgetall("test_hash")
    assert all_fields == {"field1": "value1", "field2": "value2"}
    
    # Clean up
    await redis_client.delete("test_hash")


@pytest.mark.asyncio
async def test_redis_list_operations(redis_client):
    """Test Redis list operations for queuing"""
    # Push items to list
    await redis_client.rpush("test_list", "item1", "item2", "item3")
    
    # Get list length
    length = await redis_client.llen("test_list")
    assert length == 3
    
    # Pop item from list
    item = await redis_client.lpop("test_list")
    assert item == "item1"
    
    # Clean up
    await redis_client.delete("test_list")


@pytest.mark.asyncio
async def test_redis_pub_sub(redis_client):
    """Test Redis pub/sub for cache invalidation"""
    # Create a pubsub instance
    pubsub = redis_client.pubsub()
    
    # Subscribe to a channel
    await pubsub.subscribe("test_channel")
    
    # Publish a message
    await redis_client.publish("test_channel", "test_message")
    
    # Receive the message
    message = await pubsub.get_message(ignore_subscribe_messages=True, timeout=1.0)
    if message:
        assert message["type"] == "message"
        assert message["data"] == "test_message"
    
    # Clean up
    await pubsub.unsubscribe("test_channel")
    await pubsub.close()
