import threading
from lru_cache import LRUCache


class ThreadSafeLRUCache(LRUCache):
    def __init__(self, capacity: int):
        super().__init__(capacity)
        self._lock = threading.RLock()   

    def get(self, key: int) -> int:
        with self._lock:
            return super().get(key)

    def put(self, key: int, value: int) -> None:
        with self._lock:
            super().put(key, value)

    def __len__(self) -> int:
        with self._lock:
            return super().__len__()

    def __repr__(self) -> str:
        with self._lock:
            return super().__repr__()