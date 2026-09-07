STATE = {}
OVERRIDES = {}

def update_room_state(room_id, data):
    if room_id in OVERRIDES:
        data.update(OVERRIDES[room_id])
    STATE[room_id] = data

def get_room_state(room_id):
    return STATE.get(room_id)

def get_all_state():
    return list(STATE.values())

def set_override(room_id, key, value):
    OVERRIDES.setdefault(room_id, {})[key] = value

def clear_override(room_id, key):
    if room_id in OVERRIDES and key in OVERRIDES[room_id]:
        del OVERRIDES[room_id][key]