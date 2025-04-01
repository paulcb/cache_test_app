import random
import sys

from make_sql_dump import makesqlfile

key_range = 100
limit = 100
test_name = 'test1'
test_filename = f"{test_name}.txt"
f1 = open(test_filename, 'w')
for i in range(limit):
    f1.write(f"{random.randint(0, key_range)}\n")
f1.close()

makesqlfile('.', test_filename, test_name)

# key_range = 10000
# limit = 100000
# test_name = 'test2'
# test_filename = f"{test_name}.txt"
# f1 = open(test_filename, 'w')
# for i in range(limit):
#     f1.write(f"{random.randint(0, key_range)}\n")
# f1.close()

# makesqlfile('.', test_filename, test_name)

# key_range = 100000
# limit = 100000
# test_name = 'test3'
# test_filename = f"{test_name}.txt"
# f1 = open(test_filename, 'w')
# for i in range(limit):
#     f1.write(f"{random.randint(0, key_range)}\n")
# f1.close()

# makesqlfile('.', test_filename, test_name)