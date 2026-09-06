import os, joblib
import pandas as pd

MODEL_PATH = os.path.join(os.path.dirname(__file__), "..", "models", "anomaly_model.pkl")
ENERGY_MODEL_PATH = os.path.join(os.path.dirname(__file__), "..", "models", "energy_model.pkl")

_bundle = joblib.load(MODEL_PATH)
_model = _bundle["model"]
_features = _bundle["features"]

_energy_bundle = joblib.load(ENERGY_MODEL_PATH)
_energy_model = _energy_bundle["model"]
_energy_features = _energy_bundle["features"]
_room_categories = list(_energy_bundle["room_categories"])

def detect_anomaly(room_id, hour, day_of_week, occupancy, temperature_c, humidity_pct, ac_on, lights_on, power_kw):
    power_kw = float(power_kw)
    temperature_c = float(temperature_c)
    humidity_pct = float(humidity_pct)

    room_code = _room_categories.index(room_id) if room_id in _room_categories else -1
    energy_row = pd.DataFrame([{
        "hour": hour, "day_of_week": day_of_week, "occupancy": occupancy,
        "temperature_c": temperature_c, "humidity_pct": humidity_pct,
        "ac_on": int(ac_on), "lights_on": int(lights_on), "room_id_code": room_code,
    }])[_energy_features]
    expected_power = _energy_model.predict(energy_row)[0]
    residual = power_kw - expected_power

    row = pd.DataFrame([{
        "occupancy": occupancy, "temperature_c": temperature_c,
        "power_kw": power_kw, "power_residual": residual,
    }])[_features]

    pred = _model.predict(row)[0]
    score = _model.decision_function(row)[0]
    return {"is_anomaly": bool(pred == -1), "anomaly_score": round(float(score), 3), "power_residual": round(residual, 2)}