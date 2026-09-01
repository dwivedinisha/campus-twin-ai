import numpy as np

WEEKDAY_PROFILE = [
    0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.05, 0.15,
    0.75, 0.85, 0.90, 0.85, 0.45, 0.55, 0.80, 0.85,
    0.75, 0.40, 0.20, 0.10, 0.05, 0.05, 0.0, 0.0,
]

WEEKEND_PROFILE = [
    0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.02,
    0.08, 0.12, 0.15, 0.15, 0.10, 0.10, 0.12, 0.12,
    0.08, 0.05, 0.03, 0.02, 0.0, 0.0, 0.0, 0.0,
]

def _interpolate(profile, hour_float):
    return float(np.interp(hour_float, range(25), list(profile) + [profile[0]]))

def get_expected_occupancy_ratio(hour_float, is_weekend):
    profile = WEEKEND_PROFILE if is_weekend else WEEKDAY_PROFILE
    return _interpolate(profile, hour_float)

def generate_occupancy(hour_float, is_weekend, capacity, rng):
    expected_ratio = get_expected_occupancy_ratio(hour_float, is_weekend)
    expected_count = expected_ratio * capacity
    noise = rng.normal(0, max(1.0, capacity * 0.08))
    actual_count = max(0, min(capacity, round(expected_count + noise)))
    class_scheduled = expected_ratio >= 0.4
    return int(actual_count), class_scheduled