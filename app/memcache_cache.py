from pymemcache.client.base import Client

import random
import json
import os
import time

from cache import Cache
from cache_enum import CacheType
from postgres_db import fetch_data_auto


class MemcacheCache(Cache):
    def __init__(self, thread_count, trace_file_name, log_dir_path, table_name):
        super().__init__(thread_count, trace_file_name, log_dir_path, table_name)
        self.cache_type = CacheType.MEMCACHE

        self.prep_cache()

        self.worker_threads()

    def create_connection(self):
        MEMCACHED_HOSTNAME = os.getenv('MEMCACHED_HOSTNAME')
        MEMCACHED_PORT = os.getenv('MEMCACHED_PORT')

        # print(MEMCACHED_HOSTNAME, MEMCACHED_PORT)
        return Client((MEMCACHED_HOSTNAME, MEMCACHED_PORT))

    def close_connection(conn):
        conn.close()

    def prep_cache(self):
        conn = self.create_connection()
        conn.flush_all()
        conn.close()

    def process_key(self, conn, key, count, threadNumber):
        stime = time.time()
        value = conn.get(key)
        if value:
            value = json.loads(value)
            self.log_cache(threadNumber, count, stime, key, value, True, False)
        else:
            value = fetch_data_auto(self.SourceTable, key, None, self.Session)
            conn.set(key, json.dumps(value))
            self.log_cache(threadNumber, count, stime, key, value, False, False)
