import sys, os
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from datetime import datetime
from typing import Optional
from database import get_connection

sys.path.append(os.path.join(os.path.dirname(__file__), "..", "..", "ml", "inference"))
from predict_energy import predict_energy

router = APIRouter()

class WhatIfRequest(BaseModel):
    room_id: str
    ac_on: Optional[bool] = None
    lights_on: Optional[bool] = None
    occupancy: Optional[int] = None
    temperature_c: Optional[float] = None

@router.post("/simulation")
def run_what_if(req: WhatIfRequest):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        SELECT sr.occupancy, sr.temperature_c, sr.humidity_pct, sr.ac_status, sr.lighting_status, sr.power_kw
        FROM sensor_reading sr JOIN room r ON sr.room_id = r.id
        WHERE r.name = %s ORDER BY sr.timestamp DESC LIMIT 1
    """, (req.room_id,))
    row = cur.fetchone()
    cur.close()
    conn.close()

    if not row:
        raise HTTPException(status_code=404, detail="Room not found")

    now = datetime.now()
    current_ac = row["ac_status"] == "ON"
    current_lights = row["lighting_status"] == "ON"

    current_predicted = predict_energy(
        room_id=req.room_id, hour=now.hour, day_of_week=now.weekday(),
        occupancy=row["occupancy"], temperature_c=float(row["temperature_c"]),
        humidity_pct=float(row["humidity_pct"]), ac_on=current_ac, lights_on=current_lights,
    )

    sim_ac = req.ac_on if req.ac_on is not None else current_ac
    sim_lights = req.lights_on if req.lights_on is not None else current_lights
    sim_occupancy = req.occupancy if req.occupancy is not None else row["occupancy"]
    sim_temp = req.temperature_c if req.temperature_c is not None else float(row["temperature_c"])

    simulated_predicted = predict_energy(
        room_id=req.room_id, hour=now.hour, day_of_week=now.weekday(),
        occupancy=sim_occupancy, temperature_c=sim_temp,
        humidity_pct=float(row["humidity_pct"]), ac_on=sim_ac, lights_on=sim_lights,
    )

    return {
        "room_id": req.room_id,
        "current": {"power_kw": current_predicted, "ac_on": current_ac, "lights_on": current_lights,
                    "occupancy": row["occupancy"], "temperature_c": float(row["temperature_c"])},
        "simulated": {"power_kw": simulated_predicted, "ac_on": sim_ac, "lights_on": sim_lights,
                      "occupancy": sim_occupancy, "temperature_c": sim_temp},
        "estimated_difference_kw": round(current_predicted - simulated_predicted, 2),
        "data_source": "SIMULATION_ESTIMATE",
    }