
"""
PythonCache Class

This class implements a caching mechanism using a Python dictionary. It provides methods for getting and setting cache entries, as well as logging cache hits and misses.

Attributes:
    lock (threading.Lock): A lock object used for thread safety.
    cache_type (CacheType): The type of cache, which is set to CacheType.PYTHON_CACHE.
    max_size (int): The maximum size of the cache. Defaults to 0, which means the cache has no size limit.
    size (int): The current size of the cache.
    cache_d (dict): A dictionary that stores the cache entries.
    lru_queue (llist.dllist): A doubly linked list that stores the least recently used (LRU) cache entries.
"""

import time
import threading
import llist

from cache import Cache
from cache_enum import CacheType
from postgres_db import fetch_data_auto


class LRUCache:
    OVERSIZED_EX_MSG = "Value size large than max LRUCache size"
    VALUE_TYPE_EX_MSG = "Value must be bytes type"

    def __init__(self, max_size=0):
        self.size = 0
        self.max_size = max_size
        self.cache_d = {}
        self.lru_queue = llist.dllist()

    def has(self, key):
        if key in self.cache_d:
            return True
        return False

    """
    Gets a value from the cache.

    Parameters:
    - key (str): The key to get the value for.

    Returns:
    - value (any): The value associated with the key, or None if the key is not in the cache.
    """

    def get_from_cache(self, key):
        if key not in self.cache_d:
            return None

        cache_entry = self.cache_d[key]
        if self.max_size > 0:
            sameKey = self.lru_queue.remove(cache_entry["noderef"])
            assert key == sameKey
            self.lru_queue.appendleft(key)
            self.cache_d[key] = {
                "value": cache_entry["value"], "noderef": self.lru_queue.first}
        return cache_entry["value"]
    """
    Sets a value in the cache.

    Parameters:
    - key (str): The key to set the value for.
    - value (any): The value to set.

    Returns:
    - None
    """

    def set_cache(self, key, value):
        if not isinstance(value, bytes):
            raise Exception(self.VALUE_TYPE_EX_MSG)

        if key in self.cache_d:
            self.cache_d[key] = {"value": value,
                                 "noderef": self.cache_d[key]["noderef"]}
            return

        if self.max_size > 0:
            # data is stored as bytes in this test application. Adjust for differences in testing
            value_size = len(value)
            if value_size > self.max_size:
                raise Exception(self.OVERSIZED_EX_MSG)

            while self.size + value_size > self.max_size:
                if self.lru_queue.size > 0:
                    end_node = self.lru_queue.pop()
                    rvalue = self.cache_d[end_node]["value"]
                    self.size -= len(rvalue)
                    del self.cache_d[end_node]
                else:
                    raise Exception(
                        "cache has size greater than zero but no entries.")
            self.size += value_size
            self.lru_queue.appendleft(key)
            self.cache_d[key] = {"value": value,
                                 "noderef": self.lru_queue.first}
        else:
            self.cache_d[key] = {"value": value}


class PythonCache(Cache):
    """
    Constructor.

    Initializes the cache with the specified thread count, trace file name, log directory path, table name, max size, and initialization of workers.

    Parameters:
    - thread_count (int): The number of threads.
    - trace_file_name (str): The name of the trace file.
    - log_dir_path (str): The path to the log directory.
    - table_name (str): The name of the table.
    - max_size (int, optional): The maximum byte size of the cache. Defaults to 0.
    - init_workers (bool, optional): Whether to initialize the workers. Defaults to True.
    """
    lock = threading.Lock()

    def __init__(self, thread_count,
                 trace_file_name,
                 log_dir_path,
                 table_name,
                 max_size=0, init_workers=True):
        super().__init__(thread_count, trace_file_name, log_dir_path, table_name)
        self.cache_type = CacheType.PYTHON_CACHE
        self.lrucache = LRUCache(max_size)
        self.prep_cache()

        if init_workers:
            self.worker_threads()

    """
    Creates a connection to the Redis database.

    Returns:
    - None
    """

    def create_connection(self):
        pass

    """
    Closes a Redis connection.

    Parameters:
    - conn (redis.Redis): The Redis connection object.

    Returns:
    - None
    """
    def close_connection(conn):
        pass

    """
    Prepares the cache by flushing all existing data.

    Returns:
    - None
    """

    def prep_cache(self):
        pass

    """
    Processes a cache request.

    Parameters:
    - _, (str, int): The key and count to process.
    - threadNumber (int): The thread number.

    Returns:
    - None
    """

    def process_key(self, _, key, count, threadNumber):
        stime = time.time()

        # Python dictionaries aren't thread safe
        self.lock.acquire()
        try:
            if self.lrucache.has(key):
                value = self.get_from_cache(key)

                self.log_cache(threadNumber, count, stime,
                               key, value, True, False)
            else:
                value = fetch_data_auto(
                    self.SourceTable, key, None, self.Session)
                cacheBytes = bytes.fromhex(value)
                self.set_cache(key, cacheBytes)
                self.log_cache(threadNumber, count, stime,
                               key, value, False, False)
        finally:
            # Release the lock
            self.lock.release()
