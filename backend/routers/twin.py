import sys, os
from fastapi import APIRouter, HTTPException

sys.path.append(os.path.join(os.path.dirname(__file__), "..", "..", "digital_twin"))
from state import get_all_state, get_room_state

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