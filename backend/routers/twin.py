import sys, os, json
from decimal import Decimal
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional

sys.path.append(os.path.join(os.path.dirname(__file__), "..", "..", "digital_twin"))
from state import get_all_state, get_room_state, set_override, clear_override
from database import get_connection

router = APIRouter()

@router.get("/twin")
def get_twin():
    return get_all_state()

@router.get("/twin/{room_id}")
def get_twin_room(room_id: str):
    state = get_room_state(room_id)
    if not state:
        raise HTTPException(status_code=404, detail="Room not found in twin state")
    return state


class RoomControl(BaseModel):
    ac_on: Optional[bool] = None
    lights_on: Optional[bool] = None


@router.post("/twin/{room_id}/control")
def control_room(room_id: str, control: RoomControl):
    state = get_room_state(room_id)
    if not state:
        raise HTTPException(status_code=404, detail="Room not found in twin state")

    changes = {}
    if control.ac_on is not None:
        val = "ON" if control.ac_on else "OFF"
        set_override(room_id, "ac_status", val)
        changes["ac_status"] = val
    if control.lights_on is not None:
        val = "ON" if control.lights_on else "OFF"
        set_override(room_id, "lighting_status", val)
        changes["lighting_status"] = val
    if not changes:
        raise HTTPException(status_code=400, detail="No control values provided")

    previous_state = {k: (float(v) if isinstance(v, Decimal) else v) for k, v in state.items()}

    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT id FROM room WHERE name = %s", (room_id,))
    room_row = cur.fetchone()
    cur.execute("""
        INSERT INTO action_log (recommendation_id, room_id, action, previous_state, new_state)
        VALUES (NULL, %s, %s, %s, %s)
    """, (room_row["id"], f"Manual control: {changes}", json.dumps(previous_state), json.dumps({**previous_state, **changes})))
    conn.commit()
    cur.close()
    conn.close()

    return {"room_id": room_id, "changes": changes, "status": "APPLIED"}


@router.post("/twin/{room_id}/clear-override")
def clear_room_override(room_id: str):
    clear_override(room_id, "ac_status")
    clear_override(room_id, "lighting_status")
    return {"room_id": room_id, "status": "OVERRIDES_CLEARED"}