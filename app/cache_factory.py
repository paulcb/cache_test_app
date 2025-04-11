"""
Cache factory function for creating cache instances.
"""

from redis_cache import RedisCache
from memcache_cache import MemcacheCache
from postgres_cache import PostgresCache
from python_cache import PythonCache

from cache_enum import CacheType


def create_cache(cache_type: CacheType,
                 thread_count: int,
                 tracefile_path: str,
                 log_dir_path: str,
                 table_name: str) -> object:
    """
    Creates a cache instance based on the provided cache type.

    Args:
        cache_type (CacheType): Type of cache to create.
        thread_count (int): Number of threads to use for caching.
        tracefile_path (str): Path to the trace file.
        log_dir_path (str): Path to the log directory.
        table_name (str): Name of the cache table.

    Returns:
        object: The created cache instance, or None if the cache type is not supported.

    Raises:
        ValueError: If the cache type is not a valid CacheType enum value.
    """
    tracefile_name = tracefile_path.split("/")[-1]
    if cache_type not in [CacheType.SQLALCHEMY, CacheType.REDIS, CacheType.MEMCACHE, CacheType.PYTHON_CACHE]:
        raise ValueError("Invalid cache type. Supported types are: {}".format(
            [t.value for t in CacheType]))
    elif cache_type == CacheType.SQLALCHEMY:
        return PostgresCache(thread_count, tracefile_name, log_dir_path, table_name)
    elif cache_type == CacheType.REDIS:
        return RedisCache(thread_count, tracefile_name, log_dir_path, table_name)
    elif cache_type == CacheType.MEMCACHE:
        return MemcacheCache(thread_count, tracefile_name, log_dir_path, table_name)
    elif cache_type == CacheType.PYTHON_CACHE:
        return PythonCache(thread_count, tracefile_name, log_dir_path, table_name)
