import sys, os
sys.path.append(os.path.join(os.path.dirname(__file__), "..", "energy"))
sys.path.append(os.path.join(os.path.dirname(__file__), "..", "occupancy"))
sys.path.append(os.path.join(os.path.dirname(__file__), "..", "maintenance"))
import agent as energy_agent
import agent as occupancy_agent  # noqa: overwritten below via importlib to avoid name clash
import importlib.util

def _load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod

BASE = os.path.dirname(os.path.abspath(__file__))
energy_agent = _load("energy_agent", os.path.join(BASE, "..", "energy", "agent.py"))
occupancy_agent = _load("occupancy_agent", os.path.join(BASE, "..", "occupancy", "agent.py"))
maintenance_agent = _load("maintenance_agent", os.path.join(BASE, "..", "maintenance", "agent.py"))


def run_all_agents(room_id, row, row_time, historical_avg_occupancy=None):
    recs = []
    recs += energy_agent.evaluate(room_id, row, row_time)
    recs += occupancy_agent.evaluate(room_id, row, row_time, historical_avg_occupancy)
    recs += maintenance_agent.evaluate(room_id, row, row_time)

    # Conflict resolution: if MAINTENANCE is flagged, it takes priority - drop ENERGY_SAVING
    # for the same room (don't recommend turning off AC on a room that might be malfunctioning).
    has_maintenance = any(r["type"] == "MAINTENANCE" for r in recs)
    if has_maintenance:
        recs = [r for r in recs if r["type"] != "ENERGY_SAVING"]

    return recs