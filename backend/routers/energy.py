from fastapi import APIRouter
from database import get_connection

router = APIRouter()

@router.get("/energy")
def get_energy_summary():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        SELECT r.name AS room_id, b.name AS building_id,
               ROUND(AVG(sr.power_kw)::numeric, 2) AS avg_power_kw,
               MAX(sr.timestamp) AS last_updated
        FROM sensor_reading sr
        JOIN room r ON sr.room_id = r.id
        JOIN building b ON r.building_id = b.id
        GROUP BY r.name, b.name
        ORDER BY b.name, r.name
    """)
    result = cur.fetchall()
    cur.close()
    conn.close()
    return result