"""
Cache class for caching data.
"""

import threading
import time
import queue
import datetime

from sqlalchemy import MetaData
from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy.ext.automap import automap_base

from cache_enum import CacheType
from postgres_db import get_engine

class Cache:
    """
    Cache class for caching data.
    
    Attributes:
    thread_count (int): Number of threads to use for caching.
    log_dir_path (str): Path to the log directory.
    tracefile_name (str): Name of the trace file.
    table_name (str): Name of the cache table.
    """

    def __init__(self, thread_count, tracefile_name, log_dir_path, table_name):
        """
        Initializes the Cache instance.
        
        Parameters:
        thread_count (int): Number of threads to use for caching.
        tracefile_name (str): Name of the trace file.
        log_dir_path (str): Path to the log directory.
        table_name (str): Name of the cache table.
        
        Raises:
        Exception: If thread_count is less than 1.
        """
        if thread_count < 1:
            raise Exception("thread_count less than 1")
        self.thread_count = thread_count
        self.log_dir_path = log_dir_path
        self.tracefile_name = tracefile_name
        self.cache_worker_threads = []
        self.log_thread = None
        self.cache_type = CacheType.NONE

        self.keyQueue = queue.Queue(maxsize=100)
        self.request_log_queue = queue.Queue()

        self.engine = get_engine()
        session_factory = sessionmaker(bind=self.engine)
        self.Session = scoped_session(session_factory)
        self.table_name = table_name

        metadata = MetaData()
        metadata.reflect(self.engine, only=[self.table_name])
        BaseSourceTable = automap_base(metadata=metadata)
        BaseSourceTable.prepare()
        self.SourceTable = BaseSourceTable.classes[self.table_name]

    def prep_cache(self):
        """
        Prepares the cache by flushing all data and closing the connection.
        """
        pass

    def close(self):
        """
        Closes all threads and connections.
        """
        for worker_thread in self.cache_worker_threads:
            worker_thread.join()
        self.log_thread.join()

    def process_key(self, cache_conn, key, count, threadNumber):
        """
        Processes a cache key.
        
        Parameters:
        cache_conn (Client): Memcache client object.
        key (str): Key to process.
        count (int): Count to process.
        threadNumber (int): Thread number.
        """
        pass

    def create_connection(self):
        """
        Creates a connection to the Memcache server.
        
        Returns:
        Client: A Memcache client object.
        """
        return None

    def worker_threads(self):
        """
        Initializes the worker threads and log thread.
        """
        try:
            self.log_thread = threading.Thread(target=self.cache_log_worker)
            self.log_thread.start()
            for thread_number in range(self.thread_count):
                self.cache_worker_threads.append(threading.Thread(
                    target=self.cache_worker, args=(thread_number,)))
            for worker_thread in self.cache_worker_threads:
                worker_thread.start()
        except Exception as e:
            # if anything goes wrong on setup raise exception
            print(e)
            raise

    def cache_log_worker(self):
        """
        Logs cache data to a file.
        """
        datetime_object = datetime.datetime.now()
        string_format = "%d_%m_%Y_%H_%M"
        formatted_string = datetime_object.strftime(string_format)

        log_file = open(
            f"{self.log_dir_path}/{self.tracefile_name}_{formatted_string}_{self.cache_type.value}.log", 'w')

        csv_string = "cache_action,"
        csv_string += "thread_number,"
        csv_string += "count,"
        csv_string += "delta_time,"
        csv_string += "key,"
        csv_string += "value"

        log_file.write(str(csv_string) + '\n')

        queue_empty = False
        while not queue_empty:
            try:
                log_item = self.request_log_queue.get(block=True, timeout=1.0)
                csv_string = f'{log_item["cache_action"]},'
                csv_string += f'{log_item["thread_number"]},'
                csv_string += f'{log_item["count"]},'
                csv_string += f'{log_item["delta_time"]},'
                csv_string += f'{log_item["key"]},'
                csv_string += f'{log_item["value"]}'

                log_file.write(str(csv_string) + '\n')
                self.request_log_queue.task_done()
            except queue.Empty:
                if self.keyQueue.empty():
                    queue_empty = True
        log_file.close()

    def cache_worker(self, threadNumber):
        """
        Processes cache keys.
        
        Parameters:
        threadNumber (int): Thread number.
        """
        # child class specific
        cache_conn = self.create_connection()
        while True:
            key, count, queue_empty = self.next_queue_value()
            
            if queue_empty:
                break

            if key is None:
                continue

            self.process_key(cache_conn, key, count, threadNumber)

    def log_cache(self, threadNumber, count, stime, key=None, value=None, hit=False, debug=False):
        """
        Logs cache data to the log queue.
        
        Parameters:
        threadNumber (int): Thread number.
        count (int): Count to process.
        stime (float): Start time.
        key (str): Key to log.
        value (str): Value to log.
        hit (bool): Whether the cache hit.
        debug (bool): Whether to print debug information.
        """
        log_item = {"cache_action": hit if "hit" else "miss",
                    "thread_number": threadNumber,
                    "count": count, "delta_time": self.delta_time(stime),
                    "key": key,
                    "value": value}
        if debug:
            print(log_item)
        self.request_log_queue.put(log_item)

    def next_queue_value(self):
        """
        Gets the next value from the key queue.
        
        Returns:
        tuple: Key, count, and queue empty flag.
        """
        key = None
        count = None
        queue_empty = False
        try:
            key, count = self.keyQueue.get(block=True, timeout=1.00)
            self.keyQueue.task_done()
        except queue.Empty:
            if self.keyQueue.empty():
                queue_empty = True

        return key, count, queue_empty

    def delta_time(self, stime):
        """
        Calculates the delta time.
        
        Parameters:
        stime (float): Start time.
        
        Returns:
        str: Delta time in milliseconds.
        """
        end_time = (time.time() - stime) * 1000
        delta = "{:.4f}".format(end_time)
        return delta
