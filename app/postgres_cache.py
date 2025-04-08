"""
Cache management class for SQLAlchemy database.
"""

from sqlalchemy.sql import func
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy import Integer, DateTime, Index, String
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.exc import IntegrityError

import datetime
import time
import traceback

from cache_enum import CacheType
from cache import Cache
from postgres_db import fetch_data_auto

class Base(DeclarativeBase):
    """
    Base class for all database tables.
    """
    pass


class CacheTable(Base):
    """
    Cache table class for SQLAlchemy database.
    
    Attributes:
    id (int): Unique identifier for the cache entry.
    key (str): Unique key for the cache entry.
    value (str): Value associated with the cache entry.
    inserted_at (datetime.datetime): Timestamp when the cache entry was inserted.
    """
    __tablename__ = "cache"
    __table_args__ = {"prefixes": ["UNLOGGED"]}
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    key: Mapped[str] = mapped_column(String, index=True, unique=True)
    value = mapped_column(String)
    inserted_at: Mapped[datetime.datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now())


class PostgresCache(Cache):
    """
    Postgres cache class for SQLAlchemy database.
    
    Attributes:
    thread_count (int): Number of threads to use for caching.
    trace_file_name (str): Name of the trace file.
    log_dir_path (str): Path to the log directory.
    table_name (str): Name of the cache table.
    """
    def __init__(self, thread_count, trace_file_name, log_dir_path, table_name):
        """
        Initializes the Postgres cache instance.
        
        Parameters:
        thread_count (int): Number of threads to use for caching.
        trace_file_name (str): Name of the trace file.
        log_dir_path (str): Path to the log directory.
        table_name (str): Name of the cache table.
        """
        super().__init__(thread_count, trace_file_name, log_dir_path, table_name)
        self.cache_type = CacheType.SQLALCHEMY

        self.prep_cache()

        self.worker_threads()

    def create_connection(self):
        """
        Creates a connection to the database.
        
        Returns:
        Session: A SQLAlchemy session object.
        """
        return self.Session

    def prep_cache(self):
        """
        Prepares the cache table for use.
        
        Drops all existing tables, creates the cache table, and sets up a cron job to clean up the cache.
        """
        Base.metadata.drop_all(self.engine)
        Base.metadata.create_all(self.engine)

        # older versions (13) of pgcron seconds and minute inputs didn't work.
        # stmt = "SELECT cron.schedule('cache-delete-old', '* * * * *', 'DELETE FROM cache WHERE inserted_at < NOW() - ''1 minute''::interval;');"

        # uncomment to control cache size
        # stmt = "SELECT cron.schedule('cache-delete-old', '*/1 * * * *', 'DELETE FROM cache WHERE inserted_at < NOW() - ''300 seconds''::interval;');"

        session = self.Session()
        session.begin()

        # session.query(CacheTable).delete()

        # res = session.execute(text(stmt)).all()
        # print('res', res)

        # res = session.execute(text("select * from cron.job;")).all()
        # print('res', res)

        session.commit()

        session.close()

    def postres_cache_get(self, key, session):
        """
        Retrieves a cache entry by key.
        
        Parameters:
        key (str): Key to retrieve.
        session (Session): SQLAlchemy session object.
        
        Returns:
        CacheTable: The cache entry if found, otherwise None.
        """
        cacheRes = session.query(CacheTable).where(CacheTable.key == key).all()
        if len(cacheRes) > 1:
            raise Exception(
                "Exception: cache table keys are unique constraint. This shouldn't be possible")
        if len(cacheRes) == 1:
            return cacheRes.pop()

        return None

    def process_key(self, Session, key, count, threadNumber):
        """
        Processes a cache key.
        
        Parameters:
        Session (Session): SQLAlchemy session object.
        key (str): Key to process.
        count (int): Count to process.
        threadNumber (int): Thread number.
        """
        stime = time.time()
        session = Session()
        session.begin()
        try:
            cacheRes = self.postres_cache_get(key, session)
            if cacheRes:
                self.log_cache(threadNumber, count, stime,
                               cacheRes.key, cacheRes.value, True, False)
            else:
                # there is a case when no key
                value = fetch_data_auto(self.SourceTable, key, None, session)
                if value is None:
                    raise Exception("Excepting existing key!")
                
                cache = CacheTable(
                    key=key, value=value)
                session.add(cache)
                session.commit()
                self.log_cache(threadNumber, count, stime,
                               key, value, False, False)
            
            # value = fetch_data_auto(self.SourceTable, key, None, session)
            # self.log_cache(threadNumber, count, stime,
                            #    key, value, False, False)
                
        except IntegrityError as error:
            # Either a key was written to the cache right before writing here or a different issue occured that needs a rollback. So just rollback and put value back on the queue. In this application only performance is being tested so ignoring the error will suffice

            # or the key could be thrown back on the queue
            self.keyQueue.put((key, count))

            session.rollback()
            print(error)
        except Exception as ex:
            session.rollback()
            print(ex)
            traceback.print_exc()

        session.close()
