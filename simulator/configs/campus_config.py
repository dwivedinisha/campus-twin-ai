NUM_BUILDINGS = 10
ROOMS_PER_BUILDING = 10

BUILDINGS = {
    f"Building_{chr(64 + b)}": [f"{chr(64 + b)}{100 + r}" for r in range(1, ROOMS_PER_BUILDING + 1)]
    for b in range(1, NUM_BUILDINGS + 1)
}

CAPACITY_CYCLE = [40, 35, 45, 30, 50, 38, 42, 33, 48, 36]

ROOM_CAPACITY = {}
for _building, _rooms in BUILDINGS.items():
    for _i, _room in enumerate(_rooms):
        ROOM_CAPACITY[_room] = CAPACITY_CYCLE[_i % len(CAPACITY_CYCLE)]

ENERGY_PARAMS = {
    "base_load_kw": 0.6,
    "ac_power_kw": 3.0,
    "lighting_power_kw": 0.4,
    "equipment_power_kw": 0.3,
    "occupancy_effect_kw": 0.02,
    "temp_sensitivity": 0.15,
    "comfort_temp_c": 22.0,
    "noise_std_kw": 0.15,
}

SIMULATION_DAYS = 180
INTERVAL_MINUTES = 15
INTERVALS_PER_DAY = (24 * 60) // INTERVAL_MINUTES

RANDOM_SEED = 42

SEASONAL_AMPLITUDE_C = 3.0
SEASONAL_PERIOD_DAYS = 180

AC_QUADRATIC_COEFF = 0.01

NOISE_AR_PHI = 0.6

ANOMALY_START_RATE = 0.003
AC_FAILURE_DURATION_INTERVALS = (4, 8)
UNEXPECTED_OCCUPANCY_DURATION_INTERVALS = (1, 3)

WEEKDAY_SCHEDULE = [
    (0.0, 6.0, 0.0), (6.0, 7.0, 0.05), (7.0, 8.0, 0.15), (8.0, 9.0, 0.55),
    (9.0, 9.83, 0.90), (9.83, 10.0, 0.20),
    (10.0, 10.83, 0.90), (10.83, 11.0, 0.20),
    (11.0, 11.83, 0.85), (11.83, 12.0, 0.20),
    (12.0, 13.0, 0.40),
    (13.0, 13.83, 0.80), (13.83, 14.0, 0.20),
    (14.0, 14.83, 0.80), (14.83, 15.0, 0.20),
    (15.0, 15.83, 0.75), (15.83, 16.0, 0.15),
    (16.0, 17.0, 0.35), (17.0, 18.0, 0.15),
    (18.0, 22.0, 0.05), (22.0, 24.0, 0.0),
]
WEEKEND_SCHEDULE = [
    (0.0, 8.0, 0.0), (8.0, 12.0, 0.15), (12.0, 18.0, 0.10), (18.0, 24.0, 0.0),
]