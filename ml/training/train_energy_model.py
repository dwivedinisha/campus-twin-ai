import sys, os, joblib
import pandas as pd
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score

sys.path.append(os.path.join(os.path.dirname(__file__), "..", "..", "db"))
from connection import get_connection

conn = get_connection()
df = pd.read_sql("""
    SELECT sr.timestamp, r.name AS room_id, sr.occupancy, sr.temperature_c, sr.humidity_pct,
           sr.ac_status, sr.lighting_status, sr.power_kw
    FROM sensor_reading sr JOIN room r ON sr.room_id = r.id
    ORDER BY r.name, sr.timestamp
""", conn)
conn.close()

df["timestamp"] = pd.to_datetime(df["timestamp"])
df["hour"] = df["timestamp"].dt.hour
df["day_of_week"] = df["timestamp"].dt.dayofweek
df["ac_on"] = (df["ac_status"] == "ON").astype(int)
df["lights_on"] = (df["lighting_status"] == "ON").astype(int)
df["room_id_code"] = df["room_id"].astype("category").cat.codes

features = ["hour", "day_of_week", "occupancy", "temperature_c", "humidity_pct",
            "ac_on", "lights_on", "room_id_code"]
X = df[features]
y = df["power_kw"]

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

model = RandomForestRegressor(n_estimators=100, max_depth=12, random_state=42, n_jobs=-1)
model.fit(X_train, y_train)

preds = model.predict(X_test)
print(f"MAE: {mean_absolute_error(y_test, preds):.3f}")
print(f"RMSE: {mean_squared_error(y_test, preds) ** 0.5:.3f}")
print(f"R2: {r2_score(y_test, preds):.3f}")

out_dir = os.path.join(os.path.dirname(__file__), "..", "models")
joblib.dump({"model": model, "features": features, "room_categories": df["room_id"].astype("category").cat.categories},
            os.path.join(out_dir, "energy_model.pkl"))
print("Model saved.")