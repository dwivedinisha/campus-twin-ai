import sys, os, asyncio
from datetime import datetime, timedelta
import numpy as np

sys.path.append(os.path.join(os.path.dirname(__file__), "..", "simulator"))
sys.path.append(os.path.join(os.path.dirname(__file__), "..", "db"))

from configs.campus_config import (
    BUILDINGS, ROOM_CAPACITY, ENERGY_PARAMS, INTERVAL_MINUTES,
    SEASONAL_AMPLITUDE_C, SEASONAL_PERIOD_DAYS, AC_QUADRATIC_COEFF,
    NOISE_AR_PHI, ANOMALY_START_RATE, AC_FAILURE_DURATION_INTERVALS,
    UNEXPECTED_OCCUPANCY_DURATION_INTERVALS, RANDOM_SEED,
)
from generators.occupancy import generate_occupancy
from generators.environment import generate_temperature, generate_humidity
from generators.energy import decide_ac_status, decide_lighting_status, calculate_energy
from generators.anomalies import maybe_start_anomaly, apply_ac_failure, apply_unexpected_occupancy, AC_FAILURE, UNEXPECTED_OCCUPANCY
from state import update_room_state
from connection import get_connection

ENERGY_PARAMS_Q = dict(ENERGY_PARAMS, AC_QUADRATIC_COEFF=AC_QUADRATIC_COEFF)
TICK_SECONDS = 10

rng = np.random.default_rng(RANDOM_SEED + 999)
room_to_building = {r: b for b, rooms in BUILDINGS.items() for r in rooms}
all_rooms = list(room_to_building.keys())

temp_noise = {r: 0.0 for r in all_rooms}
power_noise = {r: 0.0 for r in all_rooms}
anomaly_state = {r: {"type": None, "remaining": 0} for r in all_rooms}
sim_time = datetime.now()


def status_for(is_anomaly):
    return "ALERT" if is_anomaly else "NORMAL"


def tick():
    global sim_time
    hour_float = sim_time.hour + sim_time.minute / 60.0
    is_weekend = sim_time.weekday() >= 5
    day_offset = sim_time.timetuple().tm_yday

    conn = get_connection()
    cur = conn.cursor()

    for room in all_rooms:
        capacity = ROOM_CAPACITY[room]
        occupancy, class_scheduled = generate_occupancy(hour_float, is_weekend, capacity, rng)

        temperature, temp_noise[room] = generate_temperature(
            hour_float, day_offset, SEASONAL_AMPLITUDE_C, SEASONAL_PERIOD_DAYS,
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
            occupancy, temperature, ac_on, lights_on, ENERGY_PARAMS_Q, power_noise[room], NOISE_AR_PHI, rng
        )

        if a_type == AC_FAILURE:
            temperature, power_kw = apply_ac_failure(temperature, power_kw)
            ac_on = True

        if is_anomaly:
            state["remaining"] -= 1
            if state["remaining"] <= 0:
                state["type"] = None

        record = {
            "room_id": room, "building_id": room_to_building[room], "timestamp": sim_time.isoformat(),
            "occupancy": int(occupancy), "capacity": capacity, "temperature_c": round(float(temperature), 1),
            "humidity_pct": float(humidity), "ac_status": "ON" if ac_on else "OFF",
            "lighting_status": "ON" if lights_on else "OFF", "class_scheduled": bool(class_scheduled),
            "power_kw": float(power_kw), "is_anomaly": bool(is_anomaly), "anomaly_type": a_type,
            "status": status_for(is_anomaly), "data_source": "SIMULATION_LIVE",
        }
        update_room_state(room, record)

        cur.execute(
            """INSERT INTO sensor_reading (room_id, timestamp, occupancy, temperature_c, humidity_pct,
               ac_status, lighting_status, class_scheduled, power_kw, is_weekend, is_anomaly, anomaly_type, data_source)
               SELECT id, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s FROM room WHERE name = %s""",
            (sim_time, int(occupancy), float(temperature), float(humidity), "ON" if ac_on else "OFF",
             "ON" if lights_on else "OFF", bool(class_scheduled), float(power_kw), bool(is_weekend),
             bool(is_anomaly), a_type, "SIMULATION_LIVE", room)
        )

    conn.commit()
    cur.close()
    conn.close()
    sim_time += timedelta(minutes=INTERVAL_MINUTES)


async def run_engine():
    while True:
        tick()
        await asyncio.sleep(TICK_SECONDS)