# Project Title

Cache Service Testing App

## Description

* This project tests various cache services and mechanisms. The idea for this project came
after considering which cache service to use for a seperate project and being confused by
what a cache services performacen is really like.

Using Docker Compose to start instances

- app.py
  * application entry point
- cache_enum.py
  * cache enum types: PostgresCache, RedisCache, MemcacheCache, PythonCache
- cache_factory.py
  * a place for making Cache objects to test
- cache.py
  * base cache class for cache child classes
- memcache_cache.py
  * child Cache class
- postgres_cache.py
  * child Cache class
- postgres_db.py
  * a few helper methods for postgresql
- redis_cache.py
  * child Cache class


## Getting Started

### Dependencies

* Python3
* pip libraries: SQLAlchemy, psycopg2-binary, pymemcache ,redis, pandas
* Docker

### Installing

```
pip install -r requirments
```

### Executing program

```
usage: app.py [-h] [--cache_type CACHE_TYPE] [--log_dir LOG_DIR] [--thread_count THREAD_COUNT] [--limit LIMIT] tracefile tablename

positional arguments:
  tracefile
  tablename

options:
  -h, --help            show this help message and exit
  --cache_type CACHE_TYPE
                        1 (SQLALCHEMY), 3 (REDIS), 3 (MEMCACHE)
  --log_dir LOG_DIR
  --thread_count THREAD_COUNT
  --limit LIMIT
```
## Examples
```
source scripts/env.sh
cd container_config
docker compose up

python3 app/app.py scripts/test1.txt test1 --cache_type=1 --thread_count=2

python3 app/app.py scripts/test1.txt test1 --cache_type=2 --thread_count=2

python3 app/app.py scripts/test1.txt test1 --cache_type=3 --thread_count=2

python3 app/app.py scripts/test1.txt test1 --cache_type=4 --thread_count=2

python3 scripts/gen_test_stats.py .

csvtool readable stats.csv | view -

```

## Other scripts
scripts/arc_data_group.py - process arc trace files for making sql files for using in app
scripts/gen_test_stats.py - gen a csv table from app log data
scripts/make_sql_dump.py - generate table containing cache request origin data
scripts/rand_trace_data.py - gen random trace and sql file for using in app
## Authors

Paul Basinger  
https://github.com/paulcb


## License

This project is licensed under the License - see the LICENSE.md file for details

## Acknowledgments

Inspiration, code snippets, etc.
* here