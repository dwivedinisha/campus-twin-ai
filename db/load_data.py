import os
import pandas as pd
from connection import get_connection

csv_path = os.path.join(os.path.dirname(__file__), "..", "data", "generated", "historical_data.csv")
df = pd.read_csv(csv_path)

conn = get_connection()
cur = conn.cursor()

building_ids = {}
for b in df["building_id"].unique():
    cur.execute("SELECT id FROM building WHERE name = %s", (b,))
    row = cur.fetchone()
    if row:
        building_ids[b] = row["id"]
    else:
        cur.execute("INSERT INTO building (name) VALUES (%s) RETURNING id", (b,))
        building_ids[b] = cur.fetchone()["id"]

room_ids = {}
for _, r in df[["room_id", "building_id", "room_capacity"]].drop_duplicates().iterrows():
    cur.execute("SELECT id FROM room WHERE name = %s", (r["room_id"],))
    row = cur.fetchone()
    if row:
        room_ids[r["room_id"]] = row["id"]
    else:
        cur.execute("INSERT INTO room (building_id, name, capacity) VALUES (%s, %s, %s) RETURNING id",
                     (building_ids[r["building_id"]], r["room_id"], int(r["room_capacity"])))
        room_ids[r["room_id"]] = cur.fetchone()["id"]

conn.commit()
print(f"Buildings/rooms ready: {len(building_ids)} buildings, {len(room_ids)} rooms.")

cur.execute("SELECT COUNT(*) AS count FROM sensor_reading")
existing_count = cur.fetchone()["count"]

if existing_count >= len(df):
    print(f"sensor_reading already has {existing_count} rows (>= {len(df)} expected) — skipping data load.")
else:
    if existing_count > 0:
        print(f"Found {existing_count} stale rows, clearing before reload...")
        cur.execute("TRUNCATE sensor_reading RESTART IDENTITY CASCADE")
        conn.commit()

    from psycopg2.extras import execute_values
    rows = [
        (room_ids[r["room_id"]], r["timestamp"], int(r["occupancy"]), r["temperature_c"], r["humidity_pct"],
         r["ac_status"], r["lighting_status"], bool(r["class_scheduled"]), r["power_kw"],
         bool(r["is_weekend"]), bool(r["is_anomaly"]),
         None if pd.isna(r["anomaly_type"]) else r["anomaly_type"], r["data_source"])
        for _, r in df.iterrows()
    ]
    execute_values(cur, """INSERT INTO sensor_reading
        (room_id, timestamp, occupancy, temperature_c, humidity_pct, ac_status, lighting_status,
         class_scheduled, power_kw, is_weekend, is_anomaly, anomaly_type, data_source)
        VALUES %s""", rows, page_size=5000)
    conn.commit()
    print(f"Inserted {len(rows)} sensor readings.")

cur.close()
conn.close()