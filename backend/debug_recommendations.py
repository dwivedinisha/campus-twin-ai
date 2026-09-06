import sys, os
BASE = os.path.dirname(os.path.abspath(__file__))
sys.path.append(BASE)
sys.path.append(os.path.join(BASE, "..", "ml", "inference"))

from database import get_connection
from predict_occupancy import predict_occupancy

conn = get_connection()
cur = conn.cursor()
cur.execute("""
    SELECT r.name AS room_id, r.capacity, sr.occupancy, sr.temperature_c,
           sr.humidity_pct, sr.ac_status, sr.class_scheduled, sr.timestamp
    FROM sensor_reading sr
    JOIN room r ON sr.room_id = r.id
    WHERE sr.id IN (SELECT MAX(id) FROM sensor_reading GROUP BY room_id)
    ORDER BY r.name
""")
rows = cur.fetchall()
cur.close()
conn.close()

for row in rows:
    row_time = row["timestamp"]
    predicted = predict_occupancy(
        row["room_id"], row_time.hour, row_time.weekday(), row_time.weekday() >= 5,
        float(row["temperature_c"]), float(row["humidity_pct"]),
        row["occupancy"], row["class_scheduled"], row["capacity"]
    )
    occ_ratio_now = row["occupancy"] / row["capacity"]
    occ_ratio_pred = predicted / row["capacity"]
    qualifies = occ_ratio_now <= 0.15 and occ_ratio_pred <= 0.15 and row["ac_status"] == "ON"
    print(f"{row['room_id']:6} | occ={row['occupancy']:3} ({occ_ratio_now:.2f}) | pred={predicted:3} ({occ_ratio_pred:.2f}) | "
          f"ac={row['ac_status']:3} | QUALIFIES={qualifies}")