import random
import pytest

from python_cache import LRUCache

@pytest.fixture
def demo1_setup():
    t1 = LRUCache(10)
    return t1

def test_empty(demo1_setup):
    t1 = demo1_setup
    assert(t1.size == 0)
    assert(len(t1.cache_d) == 0)
    assert(t1.lru_queue.size == 0)

def test_fail_oversized(demo1_setup):
    t1 = demo1_setup
    with pytest.raises(Exception, match=LRUCache.OVERSIZED_EX_MSG):
        t1.set_cache("imtoobig", random.randbytes(11))

def test_add_max(demo1_setup):
    t1 = demo1_setup
    key = "imjustbigenough"
    value = random.randbytes(10)
    t1.set_cache(key, value)
    assert (t1.get_from_cache(key) == value)


def test_fail_nonbyte(demo1_setup):
    t1 = demo1_setup
    with pytest.raises(Exception, match=LRUCache.VALUE_TYPE_EX_MSG):
        t1.set_cache("addint", 123)

@pytest.fixture
def demo1_setup_seed():
    key1 = "abc1"
    couple_bytes = random.randbytes(2)
    t1 = LRUCache(10)
    t1.set_cache(key1, couple_bytes)
    return (t1, key1, couple_bytes)


def test_fixture_item(demo1_setup_seed):
    t1, key1, couple_bytes = demo1_setup_seed
    assert (t1.get_from_cache(key1) == couple_bytes)
    assert (t1.size == 2)


def test_add_cache_item(demo1_setup_seed):
    t1, key1, couple_bytes = demo1_setup_seed

    key2 = "abc2"
    couple_new_bytes = random.randbytes(4)
    t1.set_cache(key2, couple_new_bytes)

    assert (t1.get_from_cache(key2) == couple_new_bytes)

    assert (t1.get_from_cache(key1) == couple_bytes)
    assert (t1.size == 6)

def test_add_no_key(demo1_setup_seed):
    t1, key1, couple_bytes = demo1_setup_seed
    assert (t1.get_from_cache("acb2") == None)

@pytest.fixture
def demo1_setup_full():
    t1 = LRUCache(10)
    keys = [i for i in range(5)]
    kvs = list(map(lambda x: ("k_" + str(x), random.randbytes(2)), keys))
    for key, value in kvs:
        t1.set_cache(key, value)
    return (t1, kvs)

def test_full_ejects(demo1_setup_full):
    t1, kvs = demo1_setup_full
    assert (len(t1.cache_d) == len(kvs))

    recent_key = "recent_key"
    t1.set_cache(recent_key, random.randbytes(2))

    # first least recently used key removed
    assert (t1.get_from_cache(kvs[0][0]) == None)
    assert (t1.get_from_cache(recent_key))

    t1.set_cache(recent_key + "2", random.randbytes(2))

    # second least recently used key removed
    assert (t1.get_from_cache(kvs[1][0]) == None)
    
