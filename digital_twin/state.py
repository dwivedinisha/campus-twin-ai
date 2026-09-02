STATE = {}

def update_room_state(room_id, data):
    STATE[room_id] = data

def get_room_state(room_id):
    return STATE.get(room_id)

def get_all_state():
    return list(STATE.values())