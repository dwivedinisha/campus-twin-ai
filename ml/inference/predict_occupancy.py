import os, joblib
import pandas as pd

MODEL_PATH = os.path.join(os.path.dirname(__file__), "..", "models", "occupancy_model.pkl")
_bundle = joblib.load(MODEL_PATH)
_model = _bundle["model"]
_features = _bundle["features"]
_room_categories = list(_bundle["room_categories"])

def predict_occupancy(room_id, hour, day_of_week, is_weekend, temperature_c,
                       humidity_pct, prev_occupancy, class_scheduled, capacity):
    room_code = _room_categories.index(room_id) if room_id in _room_categories else -1
    row = pd.DataFrame([{
        "hour": hour, "day_of_week": day_of_week, "is_weekend": is_weekend,
        "temperature_c": temperature_c, "humidity_pct": humidity_pct,
        "prev_occupancy": prev_occupancy, "class_scheduled": class_scheduled,
        "room_id_code": room_code, "capacity": capacity,
    }])[_features]
    pred = _model.predict(row)[0]
    return max(0, round(pred))