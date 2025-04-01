from redis_cache import RedisCache
from memcache_cache import MemcacheCache
from postgres_cache import PostgresCache
from python_cache import PythonCache

from cache_enum import CacheType


def create_cache(cache_type, thread_count, tracefile_path, log_dir_path, table_name):

    tracefile_name = tracefile_path.split("/")[-1]
    if cache_type == CacheType.SQLALCHEMY:
        return PostgresCache(thread_count, tracefile_name, log_dir_path, table_name)
    elif cache_type == CacheType.REDIS:
        return RedisCache(thread_count, tracefile_name, log_dir_path, table_name)
    elif cache_type == CacheType.MEMCACHE:
        return MemcacheCache(thread_count, tracefile_name, log_dir_path, table_name)
    elif cache_type == CacheType.PYTHON_DICT:
        return PythonCache(thread_count, tracefile_name, log_dir_path, table_name)
    else:
        return None
