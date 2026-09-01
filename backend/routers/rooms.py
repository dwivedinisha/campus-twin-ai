from fastapi import APIRouter
from database import get_connection

router = APIRouter()

@router.get("/rooms")
def get_rooms():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM room ORDER BY name")
    result = cur.fetchall()
    cur.close()
    conn.close()
    return result

@router.get("/rooms/{room_id}")
def get_room(room_id: int):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM room WHERE id = %s", (room_id,))
    result = cur.fetchone()
    cur.close()
    conn.close()
    return result

@router.get("/rooms/{room_id}/history")
def get_room_history(room_id: int, limit: int = 100):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        "SELECT * FROM sensor_reading WHERE room_id = %s ORDER BY timestamp DESC LIMIT %s",
        (room_id, limit)
    )
    result = cur.fetchall()
    cur.close()
    conn.close()
    return result