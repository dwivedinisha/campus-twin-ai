import numpy as np
from generators.noise_utils import next_ar1_noise

BASE_TEMP_PROFILE = [
    22.0, 21.5, 21.0, 20.8, 20.6, 20.5, 20.8, 21.5,
    23.0, 24.5, 26.0, 27.2, 28.0, 28.5, 29.0, 28.8,
    28.2, 27.0, 25.8, 24.5, 23.8, 23.2, 22.8, 22.4,
]

def _interpolate(profile, hour_float):
    return float(np.interp(hour_float, range(25), list(profile) + [profile[0]]))

def seasonal_offset(day_offset, amplitude, period_days):
    return amplitude * np.cos(2 * np.pi * day_offset / period_days)

def generate_temperature(hour_float, day_offset, seasonal_amplitude, seasonal_period,
                          prev_noise, ar_phi, noise_std, rng):
    base = _interpolate(BASE_TEMP_PROFILE, hour_float)
    season = seasonal_offset(day_offset, seasonal_amplitude, seasonal_period)
    new_noise = next_ar1_noise(prev_noise, ar_phi, noise_std, rng)
    return round(base + season + new_noise, 1), new_noise

def generate_humidity(hour_float, rng):
    base_temp = _interpolate(BASE_TEMP_PROFILE, hour_float)
    humidity = 65 - (base_temp - 20.5) * 1.5 + rng.normal(0, 2.0)
    return round(max(30.0, min(90.0, humidity)), 1)