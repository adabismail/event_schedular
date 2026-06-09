import threading
import time
import random
from event_scheduler import can_attend_all, min_rooms_required, assign_rooms
from thread_safe_lru import ThreadSafeLRUCache


# ANSI colours
RESET  = "\033[0m"
BOLD   = "\033[1m"
CYAN   = "\033[96m"
GREEN  = "\033[92m"
RED    = "\033[91m"
YELLOW = "\033[93m"
BLUE   = "\033[94m"
GREY   = "\033[90m"
MAGENTA= "\033[95m"

# Helpers

def header(title: str):
    bar = "─" * 58
    print(f"\n{BOLD}{CYAN}{bar}{RESET}")
    print(f"{BOLD}{CYAN}  {title}{RESET}")
    print(f"{BOLD}{CYAN}{bar}{RESET}\n")


def render_timeline(events: list[tuple], assignments: list[str]):
    # Find overall time span
    all_starts  = [s for s, _ in events]
    all_ends    = [e for _, e in events]
    t_min, t_max = min(all_starts), max(all_ends)
    span = t_max - t_min or 1

    # Group events by room
    room_events: dict[str, list] = {}
    for (s, e), room in zip(events, assignments):
        room_events.setdefault(room, []).append((s, e))

    WIDTH = 48          # chars for the timeline bar
    scale = WIDTH / span

    print(f"  {GREY}Timeline  {t_min}{'—' * (WIDTH - 4)}{t_max}{RESET}")

    for room in sorted(room_events):
        bar = [" "] * WIDTH
        for (s, e) in room_events[room]:
            left  = round((s - t_min) * scale)
            right = round((e - t_min) * scale)
            for i in range(left, min(right, WIDTH)):
                bar[i] = "█"
        bar_str = "".join(bar)
        print(f"  {YELLOW}{room:8}{RESET} │ {BLUE}{bar_str}{RESET}")
    print()


# Demo 1: can_attend_all

def demo_can_attend_all():
    header("can_attend_all — Overlap Detection")

    scenarios = [
        ("No overlap (sequential)",       [(9, 10), (10, 11), (11, 12)]),
        ("Adjacent events OK",            [(0, 5),  (5, 10), (10, 15)]),
        ("One overlap",                   [(9, 11), (10, 12)]),
        ("Contained event → overlap",     [(9, 15), (10, 12)]),
        ("Unsorted, no overlap",          [(11, 12), (9, 10), (10, 11)]),
        ("All at same time",              [(9, 10), (9, 10), (9, 10)]),
    ]

    col_w = 34
    for label, events in scenarios:
        result = can_attend_all(events)
        colour = GREEN if result else RED
        tick   = "✓" if result else "✗"
        ev_str = str(events)
        print(f"  {label:<{col_w}} {colour}{tick} {result}{RESET}")
        print(f"  {GREY}{ev_str}{RESET}\n")


# Demo 2: min_rooms_required

def demo_min_rooms():
    header("min_rooms_required — Heap Trace")

    scenarios = [
        ("Sequential (1 room)",   [(9, 10), (10, 11), (11, 12)]),
        ("LeetCode classic",      [(0, 30), (5, 10), (15, 20)]),
        ("All concurrent",        [(9, 12), (9, 11), (9, 10)]),
        ("Peak concurrency = 3",  [(1, 10), (2, 7), (3, 19), (8, 12), (10, 20), (11, 30)]),
    ]

    for label, events in scenarios:
        rooms = min_rooms_required(events)
        print(f"  {YELLOW}{label}{RESET}")
        print(f"  Events : {events}")
        print(f"  Rooms  : {BOLD}{GREEN}{rooms}{RESET}\n")


# Demo 3: assign_rooms (with timeline)

def demo_assign_rooms():
    header("assign_rooms — Named Room Assignment")

    scenarios = [
        ("Sequential — Room A reused throughout",
         [(9, 10), (10, 11), (11, 12)]),

        ("Two parallel tracks",
         [(9, 11), (9, 11), (11, 13), (11, 13)]),

        ("LeetCode classic",
         [(0, 30), (5, 10), (15, 20)]),

        ("Peak-3 example",
         [(1, 10), (2, 7), (3, 19), (8, 12), (10, 20), (11, 30)]),
    ]

    for label, events in scenarios:
        assignments = assign_rooms(events)
        print(f"  {YELLOW}{label}{RESET}")
        for (s, e), room in zip(events, assignments):
            print(f"    ({s:>2}, {e:>2})  →  {BLUE}{room}{RESET}")
        render_timeline(events, assignments)


# Demo 4: Thread-safe LRU stress test

def demo_thread_safe_lru():
    header("ThreadSafeLRUCache — Concurrent Stress Test")

    capacity  = 10
    cache     = ThreadSafeLRUCache(capacity)
    N_THREADS = 8
    OPS_EACH  = 500
    errors    = []
    op_counts = {"reads": 0, "writes": 0}
    counts_lock = threading.Lock()

    def worker(thread_id: int):
        rng = random.Random(thread_id)
        for _ in range(OPS_EACH):
            key = rng.randint(0, 19)
            if rng.random() < 0.5:
                cache.put(key, thread_id * 1000 + key)
                with counts_lock:
                    op_counts["writes"] += 1
            else:
                val = cache.get(key)
                with counts_lock:
                    op_counts["reads"] += 1

            size = len(cache)
            if size > capacity:
                errors.append(f"Thread {thread_id}: size={size} > capacity={capacity}")

    threads = [threading.Thread(target=worker, args=(t,)) for t in range(N_THREADS)]

    print(f"  Spawning {N_THREADS} threads × {OPS_EACH} ops each …")
    t0 = time.perf_counter()
    for t in threads:
        t.start()
    for t in threads:
        t.join()
    elapsed = time.perf_counter() - t0

    total_ops = N_THREADS * OPS_EACH
    print(f"  Total ops   : {total_ops:,}  "
          f"({op_counts['reads']:,} reads, {op_counts['writes']:,} writes)")
    print(f"  Elapsed     : {elapsed * 1000:.1f} ms")
    print(f"  Final size  : {len(cache)} / {capacity}")

    if errors:
        print(f"\n  {RED}ERRORS ({len(errors)}):{RESET}")
        for e in errors[:5]:
            print(f"    {e}")
    else:
        print(f"\n  {GREEN} No race conditions detected — all invariants held.{RESET}")
    print()



if __name__ == "__main__":
    demo_can_attend_all()
    demo_min_rooms()
    demo_assign_rooms()
    demo_thread_safe_lru()
    print(f"{BOLD}All demos complete.{RESET}\n")