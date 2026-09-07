import sys, os
sys.path.append(os.path.join(os.path.dirname(__file__), "..", "..", "ml", "inference"))
from predict_occupancy import predict_occupancy
from predict_energy import predict_energy

def evaluate(room_id, row, row_time):
    occupancy = row["occupancy"]
    temperature_c = float(row["temperature_c"])
    humidity_pct = float(row["humidity_pct"])
    ac_on = row["ac_status"] == "ON"
    lights_on = row["lighting_status"] == "ON"
    capacity = row["capacity"]
    class_scheduled = row["class_scheduled"]

    predicted_occ = predict_occupancy(
        room_id, row_time.hour, row_time.weekday(), row_time.weekday() >= 5,
        temperature_c, humidity_pct, occupancy, class_scheduled, capacity
    )

    occ_ratio_now = occupancy / capacity
    occ_ratio_pred = predicted_occ / capacity

    if occ_ratio_now <= 0.15 and occ_ratio_pred <= 0.15 and ac_on and not class_scheduled:
        savings = predict_energy(room_id, row_time.hour, row_time.weekday(), occupancy,
                                  temperature_c, humidity_pct, ac_on, lights_on) - \
                  predict_energy(room_id, row_time.hour, row_time.weekday(), 0,
                                 temperature_c, humidity_pct, False, lights_on)
        return [{
            "type": "ENERGY_SAVING",
            "reason": f"{room_id} occupancy is low ({occupancy}/{capacity}) and predicted to remain low, with AC still ON.",
            "proposed_action": "Turn AC OFF", "estimated_impact_kw": round(float(savings), 2),
            "confidence": 0.8, "agent_source": "ENERGY_AGENT",
        }]
    return []