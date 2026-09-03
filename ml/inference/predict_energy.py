import os, joblib
import pandas as pd

MODEL_PATH = os.path.join(os.path.dirname(__file__), "..", "models", "energy_model.pkl")
_bundle = joblib.load(MODEL_PATH)
_model = _bundle["model"]
_features = _bundle["features"]
_room_categories = list(_bundle["room_categories"])

def predict_energy(room_id, hour, day_of_week, occupancy, temperature_c, humidity_pct, ac_on, lights_on):
    room_code = _room_categories.index(room_id) if room_id in _room_categories else -1
    row = pd.DataFrame([{
        "hour": hour, "day_of_week": day_of_week, "occupancy": occupancy,
        "temperature_c": temperature_c, "humidity_pct": humidity_pct,
        "ac_on": int(ac_on), "lights_on": int(lights_on), "room_id_code": room_code,
    }])[_features]
    pred = _model.predict(row)[0]
    return round(max(0, pred), 2)