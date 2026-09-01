import os
import pandas as pd
from connection import get_connection

csv_path = os.path.join(os.path.dirname(__file__), "..", "data", "generated", "historical_data.csv")
df = pd.read_csv(csv_path)

conn = get_connection()
cur = conn.cursor()

buildings = df["building_id"].unique()
building_ids = {}
for b in buildings:
    cur.execute("INSERT INTO building (name) VALUES (%s) RETURNING id", (b,))
    building_ids[b] = cur.fetchone()[0]

rooms = df[["room_id", "building_id", "room_capacity"]].drop_duplicates()
room_ids = {}
for _, r in rooms.iterrows():
    cur.execute(
        "INSERT INTO room (building_id, name, capacity) VALUES (%s, %s, %s) RETURNING id",
        (building_ids[r["building_id"]], r["room_id"], int(r["room_capacity"]))
    )
    room_ids[r["room_id"]] = cur.fetchone()[0]

conn.commit()
print(f"Inserted {len(buildings)} buildings, {len(rooms)} rooms.")

rows = [
    (
        room_ids[r["room_id"]], r["timestamp"], int(r["occupancy"]), r["temperature_c"], r["humidity_pct"],
        r["ac_status"], r["lighting_status"], bool(r["class_scheduled"]), r["power_kw"],
        bool(r["is_weekend"]), bool(r["is_anomaly"]),
        None if pd.isna(r["anomaly_type"]) else r["anomaly_type"], r["data_source"]
    )
    for _, r in df.iterrows()
]

from psycopg2.extras import execute_values
execute_values(
    cur,
    """INSERT INTO sensor_reading
       (room_id, timestamp, occupancy, temperature_c, humidity_pct, ac_status, lighting_status,
        class_scheduled, power_kw, is_weekend, is_anomaly, anomaly_type, data_source)
       VALUES %s""",
    rows,
    page_size=5000
)

conn.commit()
cur.close()
conn.close()
print(f"Inserted {len(rows)} sensor readings.")