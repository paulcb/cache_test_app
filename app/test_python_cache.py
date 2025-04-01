from python_cache import PythonCache

# t1 = PythonCache()
t1 = PythonCache(1, None, None, None, max_size=100, init_workers=False)
t1.set_cache("abc1", "12345678901234567")
t1.set_cache("abc2", "12345678901234567")
t1.set_cache("abc3", "12345678901234567")
t1.set_cache("abc4", "12345678901234567")

print(t1.get_from_cache("abc1"))
print(t1.get_from_cache("abc2"))
print(t1.get_from_cache("abc3"))
print(t1.get_from_cache("abc4"))
print(t1.lru_queue)

t1.set_cache("abc5", "12345678901234567")
print(t1)
print(t1.lru_queue)

t1.set_cache("abc6", "12345678901234567")
t1.set_cache("abc7", "12345678901234567")
t1.set_cache("abc8", "12345678901234567")
t1.set_cache("abc9", "12345678901234567")
t1.set_cache("abc9", "12345678901234567")
t1.set_cache("abc9", "12345678901234567")
t1.set_cache("abc9", "12345678901234567")
t1.set_cache("abc9", "12345678901234567")

print(t1.lru_queue)
