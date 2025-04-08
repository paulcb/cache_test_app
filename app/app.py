"""
Module containing script to create and populate a cache from a trace file.
"""

import sys
import os
import argparse

from cache_factory import create_cache, CacheType


def main():
    """
    Main function to parse command line arguments and create the cache.
    """

    # Create an ArgumentParser to parse command line arguments
    parser = argparse.ArgumentParser(
        description='Create and populate a cache from a trace file.')

    # Add arguments to the parser
    parser.add_argument('tracefile', type=str, help='Path to the trace file.')
    parser.add_argument('tablename', type=str,
                        help='Name of the table to use.')
    parser.add_argument('--cache_type', type=int, default=4,
                        help='Cache type to use. (1: SQLALCHEMY, 2: REDIS, 3: MEMCACHE)')
    parser.add_argument('--log_dir', type=str, default=".",
                        help='Directory to log cache operations to.')
    parser.add_argument('--thread_count', type=int,
                        default=1, help='Number of threads to use.')
    parser.add_argument('--limit', type=int, default=0,
                        help='Maximum number of entries to add to the cache.')

    # Parse the command line arguments
    args = parser.parse_args()

    # Print the parsed arguments
    print(args)

    # Check if the trace file exists
    tracefile = args.tracefile
    if not os.path.exists(tracefile):
        print("Error: Input file doesn't exist.")
        sys.exit(1)

    # Create the log directory if it doesn't exist
    log_dir_path = args.log_dir
    if not os.path.exists(log_dir_path):
        print("Error: Folder doesn't exist.")
        sys.exit(1)

    # Create a cache object with the specified type
    cache_type = CacheType(args.cache_type)
    cache = create_cache(cache_type, args.thread_count,
                         tracefile, log_dir_path, args.tablename)

    # Open the trace file and populate the cache
    with open(tracefile) as tracefile:
        count = 1
        for line in tracefile:
            lineSplit = line.split()
            key = lineSplit[0]
            cache.keyQueue.put((key, count))

            # Check if the limit is exceeded
            if args.limit > 0 and count >= args.limit:
                break

            count += 1

    # Close the cache
    cache.close()


if __name__ == "__main__":
    main()
