import pytest
from event_scheduler import can_attend_all, min_rooms_required, assign_rooms


class TestCanAttendAll:

    def test_empty_list(self):
        assert can_attend_all([]) is True

    def test_single_event(self):
        assert can_attend_all([(9, 10)]) is True

    def test_adjacent_events_not_overlap(self):
        assert can_attend_all([(9, 10), (10, 11), (11, 12)]) is True

    def test_clear_overlap(self):
        assert can_attend_all([(9, 11), (10, 12)]) is False

    def test_unsorted_no_overlap(self):
        assert can_attend_all([(10, 11), (9, 10)]) is True

    def test_unsorted_with_overlap(self):
        assert can_attend_all([(10, 12), (9, 11)]) is False

    def test_contained_event_is_overlap(self):
        assert can_attend_all([(9, 15), (10, 12)]) is False

    def test_just_touching_is_ok(self):
        assert can_attend_all([(0, 5), (5, 10), (10, 15)]) is True

    def test_one_minute_overlap(self):
        assert can_attend_all([(9, 10), (9, 11)]) is False


class TestMinRoomsRequired:

    def test_empty_list(self):
        assert min_rooms_required([]) == 0

    def test_single_event(self):
        assert min_rooms_required([(9, 10)]) == 1

    def test_sequential_one_room(self):
        assert min_rooms_required([(9, 10), (10, 11), (11, 12)]) == 1

    def test_all_concurrent_n_rooms(self):
        assert min_rooms_required([(9, 12), (9, 11), (9, 10)]) == 3

    def test_two_rooms_needed(self):
        assert min_rooms_required([(9, 11), (10, 12), (11, 13)]) == 2

    def test_leetcode_classic(self):
        assert min_rooms_required([(0, 30), (5, 10), (15, 20)]) == 2

    def test_unsorted_input(self):
        assert min_rooms_required([(15, 20), (0, 30), (5, 10)]) == 2

    def test_peak_concurrency_four(self):
        events = [(1, 10), (2, 7), (3, 19), (8, 12), (10, 20), (11, 30)]
        assert min_rooms_required(events) == 4

    def test_rooms_never_exceed_event_count(self):
        events = [(i, i + 5) for i in range(0, 50, 2)]
        rooms = min_rooms_required(events)
        assert rooms >= 1
        assert rooms <= len(events)


class TestAssignRooms:

    def test_empty(self):
        assert assign_rooms([]) == []

    def test_single_event_is_room_a(self):
        assert assign_rooms([(9, 10)]) == ["Room A"]

    def test_sequential_reuses_same_room(self):
        result = assign_rooms([(9, 10), (10, 11), (11, 12)])
        assert all(r == "Room A" for r in result)

    def test_overlapping_uses_distinct_rooms(self):
        result = assign_rooms([(9, 11), (10, 12)])
        assert len(set(result)) == 2
        assert all(r.startswith("Room ") for r in result)

    def test_room_count_matches_min_rooms(self):
        events = [(0, 30), (5, 10), (15, 20)]
        result = assign_rooms(events)
        assert len(set(result)) == min_rooms_required(events)

    def test_output_length_matches_input(self):
        events = [(1, 5), (2, 6), (4, 8), (7, 9)]
        result = assign_rooms(events)
        assert len(result) == len(events)

    def test_unsorted_input_preserves_original_order(self):
        events = [(10, 11), (9, 10), (11, 12)]
        result = assign_rooms(events)
        assert len(result) == 3
        assert all(r == "Room A" for r in result)

    def test_three_concurrent_events_three_rooms(self):
        events = [(9, 11), (9, 11), (9, 11)]
        result = assign_rooms(events)
        assert len(set(result)) == 3

    def test_room_reuse_after_gap(self):
        events = [(9, 10), (9, 10), (11, 12)]
        result = assign_rooms(events)
        rooms_used = set(result)
        assert len(rooms_used) == 2

    def test_large_input_room_count_is_correct(self):
        events = [(0, 100)] * 10
        result = assign_rooms(events)
        assert len(set(result)) == 10