import random
import time
from collections import OrderedDict

def make_queries(n, q, hot_pool=30, p_hot=0.95, p_update=0.03):
    hot = [(random.randint(0, n//2), random.randint(n//2, n-1))
           for _ in range(hot_pool)]
    queries = []
    for _ in range(q):
        if random.random() < p_update:
            idx = random.randint(0, n-1)
            val = random.randint(1, 100)
            queries.append(("Update", idx, val))
        else:                                 
            if random.random() < p_hot:       
                left, right = random.choice(hot)
            else:                            
                left = random.randint(0, n-1)
                right = random.randint(left, n-1)
            queries.append(("Range", left, right))
    return queries


class LRUCache:
    def __init__(self, capacity: int):
        self.capacity = capacity
        self._od = OrderedDict()

    def get(self, key):
        if key not in self._od:
            return -1
        self._od.move_to_end(key)
        return self._od[key]

    def put(self, key, value):
        if key in self._od:
            self._od.move_to_end(key)
        self._od[key] = value
        if len(self._od) > self.capacity:
            self._od.popitem(last=False)

    def keys(self):
        return self._od.keys()

    def delete(self, key):
        if key in self._od:
            del self._od[key]


def range_sum_no_cache(array, left, right):
    return int(array[left:right+1].sum()) if hasattr(array, "sum") else sum(array[left:right+1])

def update_no_cache(array, index, value):
    array[index] = value


K = 1000
cache = LRUCache(K)

def range_sum_with_cache(array, left, right):
    key = (left, right)
    cached = cache.get(key)
    if cached != -1:
        return cached
    s = range_sum_no_cache(array, left, right)
    cache.put(key, s)
    return s

def update_with_cache(array, index, value):
    array[index] = value

    keys_snapshot = list(cache.keys())
    for (l, r) in keys_snapshot:
        if l <= index <= r:
            cache.delete((l, r))


def run_queries(array, queries, use_cache: bool):
    acc = 0
    for q in queries:
        if q[0] == "Range":
            _, l, r = q
            if use_cache:
                acc += range_sum_with_cache(array, l, r)
            else:
                acc += range_sum_no_cache(array, l, r)
        else:
            _, idx, val = q
            if use_cache:
                update_with_cache(array, idx, val)
            else:
                update_no_cache(array, idx, val)
    return acc


def main():
    random.seed(42)

    n = 100_000
    q = 50_000

    try:
        import numpy as np
        base_array = np.random.randint(1, 101, size=n, dtype=np.int64)
        array_type = "numpy"
    except Exception:
        base_array = [random.randint(1, 100) for _ in range(n)]
        array_type = "python_list"

    queries = make_queries(n, q)

    if array_type == "numpy":
        arr1 = base_array.copy()
    else:
        arr1 = base_array[:]

    t0 = time.perf_counter()
    acc1 = run_queries(arr1, queries, use_cache=False)
    t1 = time.perf_counter()
    no_cache_time = t1 - t0

    global cache
    cache = LRUCache(K)

    if array_type == "numpy":
        arr2 = base_array.copy()
    else:
        arr2 = base_array[:]

    t2 = time.perf_counter()
    acc2 = run_queries(arr2, queries, use_cache=True)
    t3 = time.perf_counter()
    cache_time = t3 - t2

    assert acc1 == acc2, "Результати без кешу і з кешем не збігаються — перевірте логіку!"

    speedup = no_cache_time / cache_time if cache_time > 0 else float("inf")

    print(f"Масив: n={n}, запити: q={q}, тип даних: {array_type}")
    print(f"Без кешу : {no_cache_time:8.2f} c")
    print(f"LRU-кеш  : {cache_time:8.2f} c  (прискорення ×{speedup:.2f})")


if __name__ == "__main__":
    main()
