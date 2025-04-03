import time
import threading
import llist

from cache import Cache
from cache_enum import CacheType
from postgres_db import fetch_data_auto

# Used in cache_test_app to capture raw runtime performance of a cache outside of connecting to services
# like Redis
# TODO: Seperate LRU cache as object for PythonCache?
class PythonCache(Cache):
    lock = threading.Lock()

    def __init__(self, thread_count, trace_file_name, log_dir_path, table_name, max_size=0, init_workers=True):
        super().__init__(thread_count, trace_file_name, log_dir_path, table_name)
        self.cache_type = CacheType.PYTHON_DICT
        self.max_size = max_size
        self.size = 0
        self.cache_d = {}
        self.lru_queue = llist.dllist()
        self.prep_cache()

        if init_workers:
            self.worker_threads()

    def create_connection(self):
        pass

    def close_connection(conn):
        pass

    def prep_cache(self):
        pass

    def get_from_cache(self, key):
        if key not in self.cache_d:
            print("key not in cache.")
            return None
        
        cache_entry = self.cache_d[key]
        if self.max_size > 0:
            sameKey = self.lru_queue.remove(cache_entry["noderef"])
            assert key == sameKey
            self.lru_queue.appendleft(key)
            self.cache_d[key] = {"value": cache_entry["value"], "noderef": self.lru_queue.first}
        return cache_entry["value"]

    def set_cache(self, key, value):
        if key in self.cache_d:
            self.cache_d[key] = {"value": value, "noderef": self.cache_d[key]["noderef"]}
            return
            
        if self.max_size > 0:
            # data is stored as bytes in this test application. Adjust for differences in testing
            value_size = len(value) / 2
            while self.size + value_size > self.max_size:
                if self.lru_queue.size > 0:
                    end_node = self.lru_queue.pop()
                    rvalue = self.cache_d[end_node]["value"]
                    self.size -= len(rvalue) / 2
                    # print('end_node', end_node, 'rvalue', rvalue)
                    del self.cache_d[end_node]
                else:
                    raise Exception("cache has size greater than zero but no entries.")
            self.size += value_size
            self.lru_queue.appendleft(key)
        
            self.cache_d[key] = {"value": value, "noderef": self.lru_queue.first}
        else:
            self.cache_d[key] = {"value": value}
        
        
    def process_key(self, _, key, count, threadNumber):
        stime = time.time()

        # Python dictionaries aren't thread safe
        self.lock.acquire()
        try:
            # print('process_key', key)
            if key in self.cache_d:
                value = self.get_from_cache(key)

                self.log_cache(threadNumber, count, stime,
                               key, value, True, False)
                
            else:
                value = fetch_data_auto(self.SourceTable, key, None, self.Session)
                self.set_cache(key, value)
                self.log_cache(threadNumber, count, stime,
                               key, value, False, False)
        finally:
            # Release the lock
            self.lock.release()

