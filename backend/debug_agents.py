import sys, os
BASE = os.path.dirname(os.path.abspath(__file__))
sys.path.append(BASE)
sys.path.append(os.path.join(BASE, "..", "agents", "orchestrator"))
from database import get_connection
from orchestrator import run_all_agents

conn = get_connection()
cur = conn.cursor()
cur.execute("""
    SELECT r.id AS room_pk, r.name AS room_id, r.capacity, sr.occupancy, sr.temperature_c,
           sr.humidity_pct, sr.ac_status, sr.lighting_status, sr.power_kw, sr.class_scheduled,
           sr.timestamp
    FROM sensor_reading sr
    JOIN room r ON sr.room_id = r.id
    WHERE sr.id IN (SELECT MAX(id) FROM sensor_reading GROUP BY room_id)
    ORDER BY r.name
""")
rows = cur.fetchall()

total = 0
for row in rows:
    row_time = row["timestamp"]
    cur.execute("SELECT AVG(occupancy) AS avg_occ FROM sensor_reading WHERE room_id = %s", (row["room_pk"],))
    hist = cur.fetchone()
    historical_avg = float(hist["avg_occ"]) if hist["avg_occ"] is not None else None

    recs = run_all_agents(row["room_id"], row, row_time, historical_avg)
    if recs:
        for r in recs:
            print(f"{row['room_id']:6} -> {r['agent_source']:18} {r['type']:14} {r['proposed_action']}")
            total += 1
    else:
        print(f"{row['room_id']:6} -> (no recommendation) occ={row['occupancy']}/{row['capacity']} ac={row['ac_status']}")

cur.close()
conn.close()
print(f"\nTotal: {total}")