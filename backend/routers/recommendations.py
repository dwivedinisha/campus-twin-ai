import sys, os
from fastapi import APIRouter, HTTPException
from datetime import datetime
from database import get_connection

sys.path.append(os.path.join(os.path.dirname(__file__), "..", "..", "ml", "inference"))
from predict_occupancy import predict_occupancy
from predict_energy import predict_energy
from detect_anomaly import detect_anomaly

router = APIRouter()

def evaluate_room(room_id, row, row_time):
    occupancy = row["occupancy"]
    temperature_c = float(row["temperature_c"])
    humidity_pct = float(row["humidity_pct"])
    ac_on = row["ac_status"] == "ON"
    lights_on = row["lighting_status"] == "ON"
    power_kw = float(row["power_kw"])
    capacity = row["capacity"]
    class_scheduled = row["class_scheduled"]

    predicted_occ = predict_occupancy(
        room_id, row_time.hour, row_time.weekday(), row_time.weekday() >= 5,
        temperature_c, humidity_pct, occupancy, class_scheduled, capacity
    )

    anomaly = detect_anomaly(room_id, row_time.hour, row_time.weekday(), occupancy,
                              temperature_c, humidity_pct, ac_on, lights_on, power_kw)

    recs = []

    occupancy_ratio_now = occupancy / capacity
    occupancy_ratio_pred = predicted_occ / capacity

    if occupancy_ratio_now <= 0.15 and occupancy_ratio_pred <= 0.15 and ac_on and not class_scheduled:
        expected_savings = predict_energy(room_id, row_time.hour, row_time.weekday(), occupancy,
                                           temperature_c, humidity_pct, ac_on, lights_on) - \
                            predict_energy(room_id, row_time.hour, row_time.weekday(), 0,
                                           temperature_c, humidity_pct, False, lights_on)
        expected_savings = float(expected_savings)
        recs.append({
            "type": "ENERGY_SAVING", "reason": f"{room_id} occupancy is low ({occupancy}/{capacity}) and predicted to remain low, with AC still ON.",
            "proposed_action": "Turn AC OFF", "estimated_impact_kw": round(expected_savings, 2), "confidence": 0.8,
        })

    if anomaly["is_anomaly"]:
        recs.append({
            "type": "MAINTENANCE", "reason": f"{room_id} showing abnormal energy pattern (residual {anomaly['power_residual']} kW).",
            "proposed_action": "Schedule maintenance check", "estimated_impact_kw": None, "confidence": 0.6,
        })

    return recs


@router.post("/recommendations/generate")
def generate_recommendations():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        SELECT r.id AS room_pk, r.name AS room_id, r.capacity, sr.occupancy, sr.temperature_c,
               sr.humidity_pct, sr.ac_status, sr.lighting_status, sr.power_kw, sr.class_scheduled,
               sr.timestamp
        FROM sensor_reading sr
        JOIN room r ON sr.room_id = r.id
        WHERE sr.id IN (SELECT MAX(id) FROM sensor_reading GROUP BY room_id)
    """)
    rows = cur.fetchall()

    
    inserted = 0
    for row in rows:
        row_time = row["timestamp"]
        recs = evaluate_room(row["room_id"], row, row_time)
        for rec in recs:
            cur.execute("""
                INSERT INTO recommendation (room_id, type, reason, proposed_action, estimated_impact_kw, confidence, status)
                VALUES (%s, %s, %s, %s, %s, %s, 'PENDING')
            """, (row["room_pk"], rec["type"], rec["reason"], rec["proposed_action"],
                  rec["estimated_impact_kw"], rec["confidence"]))
            inserted += 1

    conn.commit()
    cur.close()
    conn.close()
    return {"generated": inserted}


@router.get("/recommendations")
def get_recommendations(status: str = None):
    conn = get_connection()
    cur = conn.cursor()
    query = """
        SELECT rec.id, r.name AS room_id, rec.type, rec.reason, rec.proposed_action,
               rec.estimated_impact_kw, rec.confidence, rec.status, rec.created_at
        FROM recommendation rec JOIN room r ON rec.room_id = r.id
    """
    params = ()
    if status:
        query += " WHERE rec.status = %s"
        params = (status,)
    query += " ORDER BY rec.created_at DESC"
    cur.execute(query, params)
    result = cur.fetchall()
    cur.close()
    conn.close()
    return result


@router.post("/recommendations/{rec_id}/approve")
def approve_recommendation(rec_id: int):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("UPDATE recommendation SET status = 'APPROVED' WHERE id = %s RETURNING id", (rec_id,))
    result = cur.fetchone()
    conn.commit()
    cur.close()
    conn.close()
    if not result:
        raise HTTPException(status_code=404, detail="Recommendation not found")
    return {"id": rec_id, "status": "APPROVED"}


@router.post("/recommendations/{rec_id}/reject")
def reject_recommendation(rec_id: int):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("UPDATE recommendation SET status = 'REJECTED' WHERE id = %s RETURNING id", (rec_id,))
    result = cur.fetchone()
    conn.commit()
    cur.close()
    conn.close()
    if not result:
        raise HTTPException(status_code=404, detail="Recommendation not found")
    return {"id": rec_id, "status": "REJECTED"}