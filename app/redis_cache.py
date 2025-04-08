
"""
RedisCache Class

This class is responsible for caching data in a Redis database. It extends the Cache class and provides methods for creating connections, flushing caches, and processing cache requests.
"""

import redis

from cache_enum import CacheType
from cache import Cache

import random
import json
import os
import time

from postgres_db import fetch_data_auto


class RedisCache(Cache):
    """
    RedisCache class constructor.

    Initializes the cache with the specified thread count, trace file name, log directory path, and table name.
    Sets the cache type to Redis and prepares the cache.
    """

    def __init__(self, thread_count, trace_file_name, log_dir_path, table_name):
        super().__init__(thread_count, trace_file_name, log_dir_path, table_name)
        self.cache_type = CacheType.REDIS

        # Prepare the cache
        self.prep_cache()

        # Create worker threads
        self.worker_threads()

    """
    Creates a connection to the Redis database.

    Returns a Redis connection object.
    """

    def create_connection(self):
        # Get Redis hostname and port from environment variables
        REDIS_HOSTNAME = os.getenv('REDIS_HOSTNAME')
        REDIS_PORT = os.getenv('REDIS_PORT')
        return redis.Redis(host=REDIS_HOSTNAME, port=REDIS_PORT)

    """
    Prepares the cache by flushing all existing data.

    Closes the Redis connection.
    """

    def prep_cache(self):
        # Create a Redis connection
        conn = self.create_connection()
        # Flush all existing data
        conn.flushall()
        # Close the Redis connection
        conn.close()

    """
    Processes a cache request.

    Parameters:
    - conn (Redis connection): The Redis connection object.
    - key (str): The key to process.
    - count (int): The cache count.
    - threadNumber (int): The thread number.

    Returns:
    - None
    """

    def process_key(self, conn, key, count, threadNumber):
        # Get the current time
        stime = time.time()

        # Check if the key already exists in the cache
        if conn.exists(key):
            # Get the cached value
            value = json.loads(conn.get(key))
            # Log the cache hit
            self.log_cache(threadNumber, count, stime, key, value, True)
        else:
            # No key in the cache, grab the database value and populate the cache
            value = fetch_data_auto(self.SourceTable, key, None, self.Session)
            # Log the cache miss
            self.log_cache(threadNumber, count, stime, key, value, False)
            # Set the key in the cache
            conn.set(key, json.dumps(value))
