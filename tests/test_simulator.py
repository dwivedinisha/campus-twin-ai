import sys, os
sys.path.append(os.path.join(os.path.dirname(__file__), "..", "simulator"))
from generators.occupancy import generate_occupancy, get_expected_occupancy_ratio
from generators.environment import generate_temperature, generate_humidity
from generators.energy import decide_ac_status, decide_lighting_status, calculate_energy
import numpy as np

rng = np.random.default_rng(42)

def test_occupancy_zero_at_night_weekday():
    ratio = get_expected_occupancy_ratio(2.0, is_weekend=False)
    assert ratio < 0.05

def test_occupancy_high_midday_weekday():
    ratio = get_expected_occupancy_ratio(9.0, is_weekend=False)
    assert ratio > 0.6

def test_occupancy_lower_on_weekend():
    weekday_ratio = get_expected_occupancy_ratio(9.0, is_weekend=False)
    weekend_ratio = get_expected_occupancy_ratio(9.0, is_weekend=True)
    assert weekend_ratio < weekday_ratio

def test_occupancy_never_exceeds_capacity():
    for _ in range(50):
        occ, _ = generate_occupancy(9.0, False, 40, rng)
        assert 0 <= occ <= 40

def test_ac_off_when_empty():
    assert decide_ac_status(occupancy=0, temperature=30, comfort_temp=22) is False

def test_ac_on_when_occupied_and_hot():
    assert decide_ac_status(occupancy=10, temperature=28, comfort_temp=22) is True

def test_lights_follow_occupancy():
    assert decide_lighting_status(occupancy=0) is False
    assert decide_lighting_status(occupancy=5) is True

def test_energy_never_negative():
    params = {
        "base_load_kw": 0.6, "ac_power_kw": 3.0, "lighting_power_kw": 0.4,
        "equipment_power_kw": 0.3, "occupancy_effect_kw": 0.02,
        "temp_sensitivity": 0.15, "comfort_temp_c": 22.0, "noise_std_kw": 0.15,
        "AC_QUADRATIC_COEFF": 0.01,
    }
    power, _ = calculate_energy(0, 18, False, False, params, 0.0, 0.6, rng)
    assert power >= 0

def test_energy_higher_when_occupied():
    params = {
        "base_load_kw": 0.6, "ac_power_kw": 3.0, "lighting_power_kw": 0.4,
        "equipment_power_kw": 0.3, "occupancy_effect_kw": 0.02,
        "temp_sensitivity": 0.15, "comfort_temp_c": 22.0, "noise_std_kw": 0.0,
        "AC_QUADRATIC_COEFF": 0.01,
    }
    empty_power, _ = calculate_energy(0, 22, False, False, params, 0.0, 0.0, rng)
    occupied_power, _ = calculate_energy(30, 28, True, True, params, 0.0, 0.0, rng)
    assert occupied_power > empty_power

def test_temperature_within_realistic_bounds():
    for hour in range(0, 24, 3):
        temp, _ = generate_temperature(float(hour), 0, 3.0, 180, 0.0, 0.6, 0.4, rng)
        assert -5 < temp < 45

def test_humidity_within_valid_range():
    for hour in range(0, 24, 3):
        h = generate_humidity(float(hour), rng)
        assert 30 <= h <= 90