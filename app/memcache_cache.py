"""
Memcache cache class for caching data.
"""

from pymemcache.client.base import Client

import random
import json
import os
import time

from cache import Cache
from cache_enum import CacheType
from postgres_db import fetch_data_auto


class MemcacheCache(Cache):
    """
    Memcache cache class for caching data.
    
    Attributes:
    thread_count (int): Number of threads to use for caching.
    trace_file_name (str): Name of the trace file.
    log_dir_path (str): Path to the log directory.
    table_name (str): Name of the cache table.
    """
    def __init__(self, thread_count, trace_file_name, log_dir_path, table_name):
        """
        Initializes the Memcache cache instance.
        
        Parameters:
        thread_count (int): Number of threads to use for caching.
        trace_file_name (str): Name of the trace file.
        log_dir_path (str): Path to the log directory.
        table_name (str): Name of the cache table.
        """
        super().__init__(thread_count, trace_file_name, log_dir_path, table_name)
        self.cache_type = CacheType.MEMCACHE

        self.prep_cache()

        self.worker_threads()

    def create_connection(self):
        """
        Creates a connection to the Memcache server.
        
        Returns:
        Client: A Memcache client object.
        """
        MEMCACHED_HOSTNAME = os.getenv('MEMCACHED_HOSTNAME')
        MEMCACHED_PORT = os.getenv('MEMCACHED_PORT')

        # print(MEMCACHED_HOSTNAME, MEMCACHED_PORT)
        return Client((MEMCACHED_HOSTNAME, MEMCACHED_PORT))

    @staticmethod
    def close_connection(conn):
        """
        Closes a Memcache connection.
        
        Parameters:
        conn (Client): Memcache client object.
        """
        conn.close()

    def prep_cache(self):
        """
        Prepares the cache by flushing all data and closing the connection.
        """
        conn = self.create_connection()
        conn.flush_all()
        conn.close()

    def process_key(self, conn, key, count, threadNumber):
        """
        Processes a cache key.
        
        Parameters:
        conn (Client): Memcache client object.
        key (str): Key to process.
        count (int): Count to process.
        threadNumber (int): Thread number.
        """
        stime = time.time()
        value = conn.get(key)
        if value:
            value = json.loads(value)
            self.log_cache(threadNumber, count, stime, key, value, True, False)
        else:
            value = fetch_data_auto(self.SourceTable, key, None, self.Session)
            conn.set(key, json.dumps(value))
            self.log_cache(threadNumber, count, stime, key, value, False, False)
