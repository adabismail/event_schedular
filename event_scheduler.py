import heapq
from typing import List, Tuple

def can_attend_all(events: List[Tuple[int, int]]) -> bool:
    if len(events) <= 1:
        return True

    sorted_events = sorted(events, key=lambda e: e[0])

    for i in range(1, len(sorted_events)):
        # strict '<' so that end == start (adjacent) passes
        if sorted_events[i][0] < sorted_events[i - 1][1]:
            return False

    return True


def min_rooms_required(events: List[Tuple[int, int]]) -> int:
    if not events:
        return 0

    sorted_events = sorted(events, key=lambda e: e[0])
    heap: List[int] = []          # min-heap of end times

    for start, end in sorted_events:
        if heap and heap[0] <= start:
            heapq.heappop(heap)   # earliest room freed up, reuse it
        heapq.heappush(heap, end) # mark a room as busy until `end`

    return len(heap)


def assign_rooms(events: List[Tuple[int, int]]) -> List[str]:
    if not events:
        return []

    # Sort original indices by start time so results map back to input order
    order = sorted(range(len(events)), key=lambda i: events[i][0])

    heap: List[Tuple[int, str]] = []   # (end_time, room_label)
    room_counter = 0
    assignments: List[str] = [""] * len(events)

    for orig_idx in order:
        start, end = events[orig_idx]

        if heap and heap[0][0] <= start:
            # Reclaim the room that finishes earliest
            _, room = heapq.heappop(heap)
        else:
            # No room free — allocate a new one
            room = _room_label(room_counter)
            room_counter += 1

        heapq.heappush(heap, (end, room))
        assignments[orig_idx] = room

    return assignments


def _room_label(n: int) -> str:
    label, n = "", n + 1
    while n > 0:
        n -= 1
        label = chr(ord("A") + n % 26) + label
        n //= 26
    return f"Room {label}"