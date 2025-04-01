from enum import Enum


class CacheType(Enum):
    NONE = 0
    SQLALCHEMY = 1
    REDIS = 2
    MEMCACHE = 3
    PYTHON_DICT = 4
