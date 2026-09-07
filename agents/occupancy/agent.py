def evaluate(room_id, row, row_time, historical_avg_occupancy=None):
    capacity = row["capacity"]
    occupancy = row["occupancy"]

    if historical_avg_occupancy is not None:
        utilization = historical_avg_occupancy / capacity
        if utilization < 0.10:
            return [{
                "type": "UTILIZATION", "reason": f"{room_id} has historically averaged only {historical_avg_occupancy:.1f}/{capacity} occupancy ({utilization*100:.0f}% utilization).",
                "proposed_action": "Flag room for scheduling review", "estimated_impact_kw": None,
                "confidence": 0.7, "agent_source": "OCCUPANCY_AGENT",
            }]
    return []