from fastapi import APIRouter
from database import get_connection

router = APIRouter()

@router.get("/buildings")
def get_buildings():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM building ORDER BY name")
    result = cur.fetchall()
    cur.close()
    conn.close()
    return result

@router.get("/buildings/{building_id}")
def get_building(building_id: int):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM building WHERE id = %s", (building_id,))
    result = cur.fetchone()
    cur.close()
    conn.close()
    return result