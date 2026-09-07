import sys, os
sys.path.append(os.path.join(os.path.dirname(__file__), "..", "db"))
import psycopg2
from psycopg2.extras import RealDictCursor
from dotenv import load_dotenv

load_dotenv()

def get_test_connection():
    return psycopg2.connect(
        host=os.getenv("DB_HOST"), port=os.getenv("DB_PORT"), dbname=os.getenv("DB_NAME"),
        user=os.getenv("DB_USER"), password=os.getenv("DB_PASSWORD"), cursor_factory=RealDictCursor,
    )

def test_database_connects():
    conn = get_test_connection()
    assert conn is not None
    conn.close()

def test_buildings_table_populated():
    conn = get_test_connection()
    cur = conn.cursor()
    cur.execute("SELECT COUNT(*) AS count FROM building")
    result = cur.fetchone()
    cur.close()
    conn.close()
    assert result["count"] == 3

def test_rooms_table_populated():
    conn = get_test_connection()
    cur = conn.cursor()
    cur.execute("SELECT COUNT(*) AS count FROM room")
    result = cur.fetchone()
    cur.close()
    conn.close()
    assert result["count"] == 30

def test_sensor_reading_has_data():
    conn = get_test_connection()
    cur = conn.cursor()
    cur.execute("SELECT COUNT(*) AS count FROM sensor_reading")
    result = cur.fetchone()
    cur.close()
    conn.close()
    assert result["count"] > 0

def test_room_capacities_are_positive():
    conn = get_test_connection()
    cur = conn.cursor()
    cur.execute("SELECT capacity FROM room")
    rows = cur.fetchall()
    cur.close()
    conn.close()
    assert all(r["capacity"] > 0 for r in rows)

def test_every_room_has_a_building():
    conn = get_test_connection()
    cur = conn.cursor()
    cur.execute("SELECT COUNT(*) AS count FROM room WHERE building_id IS NULL")
    result = cur.fetchone()
    cur.close()
    conn.close()
    assert result["count"] == 0