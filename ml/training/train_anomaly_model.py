import sys, os, joblib
import pandas as pd
from sklearn.ensemble import IsolationForest
from sklearn.metrics import precision_score, recall_score, f1_score

sys.path.append(os.path.join(os.path.dirname(__file__), "..", "..", "db"))
from connection import get_plain_connection

conn = get_plain_connection()
df = pd.read_sql("""
    SELECT sr.timestamp, r.name AS room_id, sr.occupancy, sr.temperature_c, sr.humidity_pct,
           sr.ac_status, sr.lighting_status, sr.power_kw, sr.is_anomaly
    FROM sensor_reading sr JOIN room r ON sr.room_id = r.id
    ORDER BY r.name, sr.timestamp
""", conn)
conn.close()

df["timestamp"] = pd.to_datetime(df["timestamp"])
df["hour"] = df["timestamp"].dt.hour
df["day_of_week"] = df["timestamp"].dt.dayofweek
df["ac_on"] = (df["ac_status"] == "ON").astype(int)
df["lights_on"] = (df["lighting_status"] == "ON").astype(int)

# Load the energy model directly and predict in one batched call (fast, vectorized)
energy_bundle = joblib.load(os.path.join(os.path.dirname(__file__), "..", "models", "energy_model.pkl"))
energy_model = energy_bundle["model"]
energy_features = energy_bundle["features"]
room_categories = list(energy_bundle["room_categories"])

df["room_id_code"] = df["room_id"].apply(lambda r: room_categories.index(r) if r in room_categories else -1)

print("Computing expected power for all rows (batched)...")
X_energy = df[energy_features]
df["expected_power"] = energy_model.predict(X_energy)
df["power_residual"] = df["power_kw"] - df["expected_power"]

features = ["occupancy", "temperature_c", "power_kw", "power_residual"]
X = df[features]

model = IsolationForest(contamination=0.012, random_state=42, n_estimators=150)
model.fit(X)

raw_preds = model.predict(X)
df["predicted_anomaly"] = (raw_preds == -1)

precision = precision_score(df["is_anomaly"], df["predicted_anomaly"])
recall = recall_score(df["is_anomaly"], df["predicted_anomaly"])
f1 = f1_score(df["is_anomaly"], df["predicted_anomaly"])

print(f"Precision: {precision:.3f}")
print(f"Recall: {recall:.3f}")
print(f"F1: {f1:.3f}")

out_dir = os.path.join(os.path.dirname(__file__), "..", "models")
joblib.dump({"model": model, "features": features}, os.path.join(out_dir, "anomaly_model.pkl"))
print("Model saved.")