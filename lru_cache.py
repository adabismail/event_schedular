class Node:

    def __init__(self, key: int, value: int):
        self.key   = key    # Stored so eviction can clean the hashmap
        self.value = value
        self.prev  = None
        self.next  = None

    def __repr__(self):
        return f"Node(key={self.key}, value={self.value})"


class LRUCache:
    def __init__(self, capacity: int):
        if capacity <= 0:
            raise ValueError("Capacity must be a positive integer.")

        self.capacity = capacity
        self.cache: dict[int, Node] = {}

        # Sentinel (dummy) nodes, eliminate all None-checks in _remove/_add
        self.head = Node(0, 0)   # LRU side
        self.tail = Node(0, 0)   # MRU side
        self.head.next = self.tail
        self.tail.prev = self.head

    def _remove(self, node: Node) -> None:
        """Detach a node from wherever it currently sits in the list."""
        prev, nxt   = node.prev, node.next
        prev.next   = nxt
        nxt.prev    = prev
        node.prev = node.next = None

    def _add_to_tail(self, node: Node) -> None:
        """Insert a node just before the dummy tail (= mark as MRU)."""
        prev        = self.tail.prev
        prev.next   = node
        node.prev   = prev
        node.next   = self.tail
        self.tail.prev = node

    def get(self, key: int) -> int:
        """
        Return the value for key, or -1 if not present.
        Marks the key as most recently used.
        """
        if key not in self.cache:
            return -1

        node = self.cache[key]
        self._remove(node)         # Pull out of current position
        self._add_to_tail(node)    # Re-insert as MRU
        return node.value

    def put(self, key: int, value: int) -> None:
        """
        Insert or update key-value pair.
        Evicts the LRU item if over capacity.
        """
        if key in self.cache:
            # Update in place, no size change, no eviction needed
            node       = self.cache[key]
            node.value = value
            self._remove(node)
            self._add_to_tail(node)
            return

        node = Node(key, value)
        self._add_to_tail(node)
        self.cache[key] = node

        # Evict LRU if over capacity
        if len(self.cache) > self.capacity:
            lru = self.head.next          # First real node after dummy head
            self._remove(lru)
            del self.cache[lru.key]

    def __len__(self) -> int:
        return len(self.cache)

    def __repr__(self) -> str:
        items = []
        cur = self.head.next
        while cur is not self.tail:
            items.append(f"{cur.key}:{cur.value}")
            cur = cur.next
        return f"LRUCache([{' → '.join(items)}], capacity={self.capacity})"