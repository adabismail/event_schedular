import threading
import pytest
from thread_safe_lru import ThreadSafeLRUCache


class TestBasicCorrectness:

    def test_get_missing_returns_minus_one(self):
        cache = ThreadSafeLRUCache(2)
        assert cache.get(99) == -1

    def test_put_and_get(self):
        cache = ThreadSafeLRUCache(2)
        cache.put(1, 10)
        assert cache.get(1) == 10

    def test_eviction(self):
        cache = ThreadSafeLRUCache(2)
        cache.put(1, 1)
        cache.put(2, 2)
        cache.put(3, 3)   # evicts 1
        assert cache.get(1) == -1
        assert cache.get(2) == 2
        assert cache.get(3) == 3

    def test_get_refreshes_order(self):
        cache = ThreadSafeLRUCache(2)
        cache.put(1, 1)
        cache.put(2, 2)
        cache.get(1)      # 1 → MRU; 2 → LRU
        cache.put(3, 3)   # evicts 2
        assert cache.get(2) == -1
        assert cache.get(1) == 1

    def test_update_in_place(self):
        cache = ThreadSafeLRUCache(2)
        cache.put(1, 1)
        cache.put(1, 999)
        assert cache.get(1) == 999
        assert len(cache) == 1


class TestConcurrency:

    def _run_threads(self, fns: list) -> list:
        errors = []
        threads = []

        for fn in fns:
            def make_target(f):
                def target():
                    try:
                        f()
                    except Exception as exc:
                        errors.append(exc)
                return target
            threads.append(threading.Thread(target=make_target(fn)))

        for t in threads:
            t.start()
        for t in threads:
            t.join()

        return errors

    def test_concurrent_puts_no_crash(self):
        cache  = ThreadSafeLRUCache(100)
        errors = self._run_threads([
            (lambda tid: lambda: [cache.put(tid * 100 + i, i) for i in range(30)])(t)
            for t in range(10)
        ])
        assert errors == [], f"Exceptions: {errors}"

    def test_capacity_never_exceeded_under_concurrency(self):
        capacity = 10
        cache    = ThreadSafeLRUCache(capacity)
        errors   = []

        def writer(start):
            for i in range(start, start + 50):
                cache.put(i, i)
                size = len(cache)
                if size > capacity:
                    errors.append(AssertionError(f"size={size} > capacity={capacity}"))

        threads = [threading.Thread(target=writer, args=(t * 50,)) for t in range(5)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()

        assert errors == []
        assert len(cache) <= capacity

    def test_concurrent_reads_and_writes(self):
        cache  = ThreadSafeLRUCache(20)
        errors = []
        for i in range(10):
            cache.put(i, i * 10)

        def reader():
            for i in range(10):
                val = cache.get(i)
                assert isinstance(val, int)

        def writer(start):
            for i in range(start, start + 10):
                cache.put(i, i * 99)

        fns = [reader for _ in range(5)] + [
            (lambda s: lambda: writer(s))(s * 10) for s in range(5)
        ]
        errors = self._run_threads(fns)
        assert errors == [], f"Exceptions: {errors}"

    def test_single_key_contention(self):
        cache   = ThreadSafeLRUCache(5)
        results = {}
        lock    = threading.Lock()

        def worker(val):
            cache.put(42, val)
            read_back = cache.get(42)
            with lock:
                results[val] = read_back

        threads = [threading.Thread(target=worker, args=(v,)) for v in range(50)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()

        final = cache.get(42)
        assert 0 <= final < 50, f"Unexpected value: {final}"