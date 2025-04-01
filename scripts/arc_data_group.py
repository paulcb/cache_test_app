import sys

from make_sql_dump import makesqlfile

folder = sys.argv[1]

test_names = ['S1', 'S2', 'S3', 'DS1', 'OLTP']
# test_names = ['OLTP', 'S1', 'DS1']
# test_names = ['DS1']
for test_name in test_names:
    makesqlfile(folder, test_name + '.lis', test_name)