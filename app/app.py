import sys, os, argparse

from cache_factory import create_cache, CacheType


import argparse
parser = argparse.ArgumentParser()

parser.add_argument('tracefile', type=str)
parser.add_argument('tablename', type=str)
parser.add_argument('--cache_type', type=int, default=4, help="1 (SQLALCHEMY), 3 (REDIS), 3 (MEMCACHE)")
parser.add_argument('--log_dir', type=str, default=".")
parser.add_argument('--thread_count',type=int, default=1)
parser.add_argument('--limit', type=int, default=0)

args = parser.parse_args()
print(args)
tracefile = args.tracefile

if not os.path.exists(tracefile):
    print("Input file doesn't exists")
    exit(1)

log_dir_path = args.log_dir

if not os.path.exists(log_dir_path):
    print("Folder doesn't exists")
    exit(1)

cache_type = CacheType(args.cache_type)

thread_count = args.thread_count

tablename = args.tablename
limit = args.limit

cache = create_cache(cache_type, thread_count, tracefile, log_dir_path, tablename)

with open(tracefile) as tracefile:
    count = 1
    for line in tracefile:
        lineSplit = line.split()
        key = lineSplit[0]
        cache.keyQueue.put((key, count))

        if limit > 0:
            if count >= limit:
                break

        count += 1

cache.close()
