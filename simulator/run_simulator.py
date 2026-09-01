import sys, os
from datetime import datetime, timedelta
import numpy as np
import pandas as pd

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from configs.campus_config import (
    BUILDINGS, ROOM_CAPACITY, ENERGY_PARAMS, SIMULATION_DAYS, INTERVAL_MINUTES,
    INTERVALS_PER_DAY, RANDOM_SEED, SEASONAL_AMPLITUDE_C, SEASONAL_PERIOD_DAYS,
    AC_QUADRATIC_COEFF, NOISE_AR_PHI, ANOMALY_START_RATE,
    AC_FAILURE_DURATION_INTERVALS, UNEXPECTED_OCCUPANCY_DURATION_INTERVALS,
)
from generators.occupancy import generate_occupancy
from generators.environment import generate_temperature, generate_humidity
from generators.energy import decide_ac_status, decide_lighting_status, calculate_energy
from generators.anomalies import maybe_start_anomaly, apply_ac_failure, apply_unexpected_occupancy, AC_FAILURE, UNEXPECTED_OCCUPANCY

ENERGY_PARAMS_WITH_QUAD = dict(ENERGY_PARAMS, AC_QUADRATIC_COEFF=AC_QUADRATIC_COEFF)


def generate_historical_data():
    rng = np.random.default_rng(RANDOM_SEED)
    room_to_building = {r: b for b, rooms in BUILDINGS.items() for r in rooms}
    all_rooms = list(room_to_building.keys())

    temp_noise = {r: 0.0 for r in all_rooms}
    power_noise = {r: 0.0 for r in all_rooms}
    anomaly_state = {r: {"type": None, "remaining": 0} for r in all_rooms}

    start_date = datetime(2026, 1, 1)
    rows = []

    for day in range(SIMULATION_DAYS):
        date = start_date + timedelta(days=day)
        is_weekend = date.weekday() >= 5

        for i in range(INTERVALS_PER_DAY):
            hour_float = (i * INTERVAL_MINUTES) / 60.0
            timestamp = date + timedelta(minutes=i * INTERVAL_MINUTES)

            for room in all_rooms:
                capacity = ROOM_CAPACITY[room]
                occupancy, class_scheduled = generate_occupancy(hour_float, is_weekend, capacity, rng)

                temperature, temp_noise[room] = generate_temperature(
                    hour_float, day, SEASONAL_AMPLITUDE_C, SEASONAL_PERIOD_DAYS,
                    temp_noise[room], NOISE_AR_PHI, 0.4, rng
                )
                humidity = generate_humidity(hour_float, rng)

                state = anomaly_state[room]
                if state["remaining"] <= 0:
                    a_type, duration = maybe_start_anomaly(
                        rng, ANOMALY_START_RATE, AC_FAILURE_DURATION_INTERVALS, UNEXPECTED_OCCUPANCY_DURATION_INTERVALS
                    )
                    if a_type:
                        state["type"], state["remaining"] = a_type, duration

                is_anomaly = state["remaining"] > 0
                a_type = state["type"] if is_anomaly else None

                if a_type == UNEXPECTED_OCCUPANCY:
                    occupancy = apply_unexpected_occupancy(capacity, rng)

                ac_on = decide_ac_status(occupancy, temperature, ENERGY_PARAMS["comfort_temp_c"])
                lights_on = decide_lighting_status(occupancy)

                power_kw, power_noise[room] = calculate_energy(
                    occupancy, temperature, ac_on, lights_on, ENERGY_PARAMS_WITH_QUAD,
                    power_noise[room], NOISE_AR_PHI, rng
                )

                if a_type == AC_FAILURE:
                    temperature, power_kw = apply_ac_failure(temperature, power_kw)
                    ac_on = True

                if is_anomaly:
                    state["remaining"] -= 1
                    if state["remaining"] <= 0:
                        state["type"] = None

                rows.append({
                    "timestamp": timestamp, "building_id": room_to_building[room], "room_id": room,
                    "occupancy": occupancy, "room_capacity": capacity, "temperature_c": round(temperature, 1),
                    "humidity_pct": humidity, "ac_status": "ON" if ac_on else "OFF",
                    "lighting_status": "ON" if lights_on else "OFF", "class_scheduled": class_scheduled,
                    "power_kw": power_kw, "is_weekend": is_weekend, "is_anomaly": is_anomaly,
                    "anomaly_type": a_type, "data_source": "SIMULATION",
                })

    return pd.DataFrame(rows)


def main():
    total_rooms = sum(len(r) for r in BUILDINGS.values())
    print(f"Generating {SIMULATION_DAYS}d x {total_rooms} rooms x {INTERVALS_PER_DAY} intervals/day...")

    df = generate_historical_data()

    out_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "data", "generated")
    os.makedirs(out_dir, exist_ok=True)
    out_path = os.path.join(out_dir, "historical_data.csv")
    df.to_csv(out_path, index=False)

    print(f"Done. {len(df)} rows -> {os.path.abspath(out_path)}")
    print(f"Anomalies: {df['is_anomaly'].sum()} ({df['is_anomaly'].mean()*100:.2f}%)")
    print(df['anomaly_type'].value_counts(dropna=True))
    print(df.head(5).to_string(index=False))


if __name__ == "__main__":
    main()