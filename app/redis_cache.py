import redis

from cache_enum import CacheType
from cache import Cache

import random
import json
import os
import time

from postgres_db import fetch_data_auto


class RedisCache(Cache):
    def __init__(self, thread_count, trace_file_name, log_dir_path, table_name):
        super().__init__(thread_count, trace_file_name, log_dir_path, table_name)
        self.cache_type = CacheType.REDIS

        self.prep_cache()

        self.worker_threads()

    def create_connection(self):
        REDIS_HOSTNAME = os.getenv('REDIS_HOSTNAME')
        REDIS_PORT = os.getenv('REDIS_PORT')
        return redis.Redis(host=REDIS_HOSTNAME, port=REDIS_PORT)

    def prep_cache(self):
        conn = self.create_connection()
        conn.flushall()
        conn.close()

    # process next cache request
    def process_key(self, conn, key, count, threadNumber):
        stime = time.time()
        # is there a key already in the cache
        if conn.exists(key):
            value = json.loads(conn.get(key))
            self.log_cache(threadNumber, count, stime, key, value, True)
        else:
            # no key in the cache, so now grab the database value and populate the cache
            value = fetch_data_auto(self.SourceTable, key, None, self.Session)
            self.log_cache(threadNumber, count, stime,
                           key, value, False)
            conn.set(key, json.dumps(value))
