import logging
import redis.asyncio as aioredis
from redis.asyncio import Redis
from redis.exceptions import RedisError, ConnectionError
from src.setup import REDIS_PASSWORD, REDIS_HOST

logger = logging.getLogger(__name__)
redis_client = aioredis.from_url(
    f"redis://:{REDIS_PASSWORD}@{REDIS_HOST}:6379",  # phải sửa cái này trước khi deploy
    password=REDIS_PASSWORD,
    decode_responses=True,
    socket_connect_timeout=5,
    socket_keepalive=True,
    health_check_interval=30,
)


async def get_redis_client() -> Redis:
    try:
        await redis_client.ping()
        return redis_client
    except (ConnectionError, RedisError) as e:
        logger.error(f"Redis connection error: {e}")
        raise


async def create_client(client_id: str, ttl: int = 3600) -> bool:
    try:
        key = f"client:{client_id}"
        await redis_client.set(key, "connected", ex=ttl)
        logger.info(f"Client created: {client_id}")
        return True
    except RedisError as e:
        logger.error(f"Failed to create client {client_id}: {e}")
        return False


async def client_exists(client_id: str) -> bool:
    try:
        key = f"client:{client_id}"
        exists = await redis_client.exists(key)
        return exists == 1
    except RedisError as e:
        logger.error(f"Failed to check client {client_id}: {e}")
        return False


async def delete_client(client_id: str) -> bool:
    try:
        key = f"client:{client_id}"
        result = await redis_client.delete(key)
        logger.info(f"Client deleted: {client_id}")
        return result > 0
    except RedisError as e:
        logger.error(f"Failed to delete client {client_id}: {e}")
        return False


async def extend_client_ttl(client_id: str, ttl: int = 3600) -> bool:
    try:
        key = f"client:{client_id}"
        result = await redis_client.expire(key, ttl)
        if result:
            logger.debug(f"Extended TTL for client {client_id}")
        return result > 0
    except RedisError as e:
        logger.error(f"Failed to extend TTL for client {client_id}: {e}")
        return False


async def set_cache(key: str, value: str, ttl: int | None = None) -> bool:
    try:
        if ttl:
            await redis_client.set(key, value, ex=ttl)
        else:
            await redis_client.set(key, value)
        logger.debug(f"Cache set: {key}")
        return True
    except RedisError as e:
        logger.error(f"Failed to set cache {key}: {e}")
        return False


async def get_cache(key: str) -> str | None:
    try:
        value = await redis_client.get(key)
        return value
    except RedisError as e:
        logger.error(f"Failed to get cache {key}: {e}")
        return None


async def delete_cache(key: str) -> bool:
    try:
        result = await redis_client.delete(key)
        return result > 0
    except RedisError as e:
        logger.error(f"Failed to delete cache {key}: {e}")
        return False


async def clear_all_cache() -> bool:
    try:
        await redis_client.flushdb()
        logger.warning("All cache cleared!")
        return True
    except RedisError as e:
        logger.error(f"Failed to clear cache: {e}")
        return False


async def get_cache_ttl(key: str) -> int:
    try:
        ttl = await redis_client.ttl(key)
        return ttl
    except RedisError as e:
        logger.error(f"Failed to get TTL for {key}: {e}")
        return -2


async def close_redis():
    try:
        await redis_client.close()
        logger.info("Redis connection closed")
    except Exception as e:
        logger.error(f"Failed to close Redis connection: {e}")
