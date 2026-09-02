import sys, os
from fastapi import APIRouter, HTTPException
from datetime import datetime
from database import get_connection

sys.path.append(os.path.join(os.path.dirname(__file__), "..", "..", "ml", "inference"))
from predict_occupancy import predict_occupancy

router = APIRouter()

@router.get("/predictions/occupancy/{room_id}")
def get_occupancy_prediction(room_id: str):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        SELECT sr.occupancy, sr.temperature_c, sr.humidity_pct, sr.class_scheduled, r.capacity
        FROM sensor_reading sr JOIN room r ON sr.room_id = r.id
        WHERE r.name = %s ORDER BY sr.timestamp DESC LIMIT 1
    """, (room_id,))
    row = cur.fetchone()
    cur.close()
    conn.close()

    if not row:
        raise HTTPException(status_code=404, detail="Room not found")

    now = datetime.now()
    predicted = predict_occupancy(
        room_id=room_id, hour=now.hour, day_of_week=now.weekday(),
        is_weekend=now.weekday() >= 5, temperature_c=row["temperature_c"],
        humidity_pct=row["humidity_pct"], prev_occupancy=row["occupancy"],
        class_scheduled=row["class_scheduled"], capacity=row["capacity"],
    )
    return {"room_id": room_id, "predicted_occupancy": predicted, "current_occupancy": row["occupancy"]}