import sys, os
from fastapi import APIRouter
from datetime import datetime
from database import get_connection

sys.path.append(os.path.join(os.path.dirname(__file__), "..", "..", "ml", "inference"))
from detect_anomaly import detect_anomaly

router = APIRouter()

@router.get("/alerts")
def get_active_alerts():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        SELECT DISTINCT ON (r.name) r.name AS room_id, b.name AS building_id,
               sr.occupancy, sr.temperature_c, sr.humidity_pct, sr.ac_status, sr.lighting_status,
               sr.power_kw, sr.timestamp
        FROM sensor_reading sr
        JOIN room r ON sr.room_id = r.id
        JOIN building b ON r.building_id = b.id
        ORDER BY r.name, sr.timestamp DESC
    """)
    rows = cur.fetchall()
    cur.close()
    conn.close()

    now = datetime.now()
    alerts = []
    for row in rows:
        result = detect_anomaly(
            room_id=row["room_id"], hour=now.hour, day_of_week=now.weekday(),
            occupancy=row["occupancy"], temperature_c=row["temperature_c"], humidity_pct=row["humidity_pct"],
            ac_on=row["ac_status"] == "ON", lights_on=row["lighting_status"] == "ON", power_kw=row["power_kw"],
        )
        if result["is_anomaly"]:
            alerts.append({**row, **result})
    return alerts