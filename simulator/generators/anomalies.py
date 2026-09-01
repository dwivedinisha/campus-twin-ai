AC_FAILURE = "AC_FAILURE"
UNEXPECTED_OCCUPANCY = "UNEXPECTED_OCCUPANCY"

def maybe_start_anomaly(rng, start_rate, ac_range, occ_range):
    if rng.random() < start_rate:
        if rng.random() < 0.5:
            return AC_FAILURE, int(rng.integers(ac_range[0], ac_range[1] + 1))
        return UNEXPECTED_OCCUPANCY, int(rng.integers(occ_range[0], occ_range[1] + 1))
    return None, 0

def apply_ac_failure(temperature, power_kw):
    return temperature + 4.0, round(power_kw * 2.0, 2)

def apply_unexpected_occupancy(capacity, rng):
    return int(rng.integers(int(capacity * 0.5), capacity + 1))