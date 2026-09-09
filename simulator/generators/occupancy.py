import sys, os
sys.path.append(os.path.join(os.path.dirname(__file__), "..", "configs"))
from campus_config import WEEKDAY_SCHEDULE, WEEKEND_SCHEDULE

def get_expected_occupancy_ratio(hour_float, is_weekend):
    schedule = WEEKEND_SCHEDULE if is_weekend else WEEKDAY_SCHEDULE
    for start, end, ratio in schedule:
        if start <= hour_float < end:
            return ratio
    return 0.0

def generate_occupancy(hour_float, is_weekend, capacity, rng):
    ratio = get_expected_occupancy_ratio(hour_float, is_weekend)
    expected = ratio * capacity
    noise = rng.normal(0, max(1.0, capacity * 0.05))
    actual = max(0, min(capacity, round(expected + noise)))
    class_scheduled = ratio >= 0.4
    return int(actual), class_scheduled