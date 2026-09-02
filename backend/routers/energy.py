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
    return list(reversed(result))
    
@router.get("/energy/hourly")
def get_hourly_energy():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        SELECT EXTRACT(HOUR FROM timestamp)::int AS hour,
               ROUND(AVG(power_kw)::numeric, 2) AS avg_power_kw
        FROM sensor_reading
        GROUP BY hour ORDER BY hour
    """)
    result = cur.fetchall()
    cur.close()
    conn.close()
    return result

@router.get("/energy/daily")
def get_daily_energy():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        SELECT DATE(timestamp) AS date,
               ROUND(SUM(power_kw)::numeric, 2) AS total_power_kw
        FROM sensor_reading
        GROUP BY date ORDER BY date
    """)
    result = cur.fetchall()
    cur.close()
    conn.close()
    return result

@router.get("/energy/by-building")
def get_energy_by_building():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        SELECT b.name AS building_id,
               ROUND(AVG(sr.power_kw)::numeric, 2) AS avg_power_kw
        FROM sensor_reading sr
        JOIN room r ON sr.room_id = r.id
        JOIN building b ON r.building_id = b.id
        GROUP BY b.name ORDER BY b.name
    """)
    result = cur.fetchall()
    cur.close()
    conn.close()
    return result

@router.get("/energy/by-room/{room_id}")
def get_energy_timeseries(room_id: str, limit: int = 200):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        SELECT sr.timestamp, sr.power_kw
        FROM sensor_reading sr
        JOIN room r ON sr.room_id = r.id
        WHERE r.name = %s
        ORDER BY sr.timestamp DESC LIMIT %s
    """, (room_id, limit))
    
    result = cur.fetchall()
    cur.close()
    conn.close()
    return result