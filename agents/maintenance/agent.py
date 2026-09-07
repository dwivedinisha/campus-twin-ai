import sys, os
sys.path.append(os.path.join(os.path.dirname(__file__), "..", "..", "ml", "inference"))
from detect_anomaly import detect_anomaly

def evaluate(room_id, row, row_time):
    occupancy = row["occupancy"]
    temperature_c = float(row["temperature_c"])
    humidity_pct = float(row["humidity_pct"])
    ac_on = row["ac_status"] == "ON"
    lights_on = row["lighting_status"] == "ON"
    power_kw = float(row["power_kw"])

    anomaly = detect_anomaly(room_id, row_time.hour, row_time.weekday(), occupancy,
                              temperature_c, humidity_pct, ac_on, lights_on, power_kw)

    if anomaly["is_anomaly"]:
        return [{
            "type": "MAINTENANCE",
            "reason": f"{room_id} showing abnormal energy pattern (residual {anomaly['power_residual']} kW).",
            "proposed_action": "Schedule maintenance check", "estimated_impact_kw": None,
            "confidence": 0.6, "agent_source": "MAINTENANCE_AGENT",
        }]
    return []