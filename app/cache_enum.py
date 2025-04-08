"""
Module containing an enumeration of cache types.
"""

from enum import Enum


class CacheType(Enum):
    """
    Enumerates the different types of caches that can be used.

    Each cache type is assigned a unique integer value.
    """

    # No cache is used, no data is stored or retrieved.
    NONE = 0

    # A cache that uses SQLALCHEMY
    SQLALCHEMY = 1

    # A cache that uses REDIS
    REDIS = 2

    # A cache that uses MEMCACHE
    MEMCACHE = 3

    # A cache that uses a Python dictionary
    PYTHON_DICT = 4
