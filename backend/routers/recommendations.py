import sys, os
import json
from decimal import Decimal
sys.path.append(os.path.join(os.path.dirname(__file__), "..", "..", "digital_twin"))
from state import set_override
sys.path.append(os.path.join(os.path.dirname(__file__), "..", "..", "agents", "orchestrator"))
from orchestrator import run_all_agents

from fastapi import APIRouter, HTTPException
from datetime import datetime
from database import get_connection

sys.path.append(os.path.join(os.path.dirname(__file__), "..", "..", "ml", "inference"))
from predict_occupancy import predict_occupancy
from predict_energy import predict_energy
from detect_anomaly import detect_anomaly

router = APIRouter()



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

        cur.execute("SELECT AVG(occupancy) AS avg_occ FROM sensor_reading WHERE room_id = %s", (row["room_pk"],))
        hist = cur.fetchone()
        historical_avg = float(hist["avg_occ"]) if hist["avg_occ"] is not None else None

        recs = run_all_agents(row["room_id"], row, row_time, historical_avg)
        for rec in recs:
            cur.execute("""
                SELECT id FROM recommendation
                WHERE room_id = %s AND type = %s AND status = 'PENDING'
            """, (row["room_pk"], rec["type"]))
            existing = cur.fetchone()
            if existing:
                continue

            cur.execute("""
                INSERT INTO recommendation (room_id, type, reason, proposed_action, estimated_impact_kw, confidence, status, agent_source)
                VALUES (%s, %s, %s, %s, %s, %s, 'PENDING', %s)
            """, (row["room_pk"], rec["type"], rec["reason"], rec["proposed_action"],
                  rec["estimated_impact_kw"], rec["confidence"], rec["agent_source"]))
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
               rec.estimated_impact_kw, rec.confidence, rec.status, rec.agent_source, rec.created_at
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
    cur.execute("""
        SELECT rec.id, rec.room_id, rec.proposed_action, r.name AS room_name
        FROM recommendation rec JOIN room r ON rec.room_id = r.id
        WHERE rec.id = %s
    """, (rec_id,))
    rec = cur.fetchone()

    if not rec:
        cur.close()
        conn.close()
        raise HTTPException(status_code=404, detail="Recommendation not found")

    cur.execute("""
        SELECT occupancy, temperature_c, humidity_pct, ac_status, lighting_status, power_kw
        FROM sensor_reading WHERE room_id = %s ORDER BY timestamp DESC LIMIT 1
    """, (rec["room_id"],))
    before = cur.fetchone()

    
    previous_state = {k: (float(v) if isinstance(v, (int, float, Decimal)) else v) for k, v in before.items()}
    action_taken = rec["proposed_action"]
    new_state = dict(previous_state)

    if action_taken == "Turn AC OFF":
        set_override(rec["room_name"], "ac_status", "OFF")
        new_state["ac_status"] = "OFF"
    elif action_taken == "Schedule maintenance check":
        pass  # No state mutation - this is an informational/maintenance recommendation, not actuation

    cur.execute("UPDATE recommendation SET status = 'EXECUTED' WHERE id = %s", (rec_id,))
    cur.execute("""
        INSERT INTO action_log (recommendation_id, room_id, action, previous_state, new_state)
        VALUES (%s, %s, %s, %s, %s)
    """, (rec_id, rec["room_id"], action_taken, json.dumps(previous_state), json.dumps(new_state)))

    conn.commit()
    cur.close()
    conn.close()
    return {"id": rec_id, "status": "EXECUTED", "action": action_taken, "previous_state": previous_state, "new_state": new_state}


@router.get("/actions")
def get_action_log():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        SELECT al.id, r.name AS room_id, al.action, al.previous_state, al.new_state, al.executed_at
        FROM action_log al JOIN room r ON al.room_id = r.id
        ORDER BY al.executed_at DESC
    """)
    result = cur.fetchall()
    cur.close()
    conn.close()
    return result


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