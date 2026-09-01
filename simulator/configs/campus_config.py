NUM_BUILDINGS = 3
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