import sys, os
sys.path.append(os.path.join(os.path.dirname(__file__), "..", "backend"))
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def test_root():
    r = client.get("/")
    assert r.status_code == 200
    assert "status" in r.json()

def test_buildings_returns_three():
    r = client.get("/buildings")
    assert r.status_code == 200
    assert len(r.json()) == 3

def test_rooms_returns_thirty():
    r = client.get("/rooms")
    assert r.status_code == 200
    assert len(r.json()) == 30

def test_room_history_returns_list():
    r = client.get("/rooms/1/history?limit=5")
    assert r.status_code == 200
    assert isinstance(r.json(), list)

def test_energy_summary():
    r = client.get("/energy")
    assert r.status_code == 200
    assert len(r.json()) == 30

def test_energy_hourly_returns_24_hours():
    r = client.get("/energy/hourly")
    assert r.status_code == 200
    assert len(r.json()) == 24

def test_twin_returns_all_rooms():
    r = client.get("/twin")
    assert r.status_code == 200

def test_twin_unknown_room_404():
    r = client.get("/twin/ZZZ999")
    assert r.status_code == 404

def test_prediction_occupancy_valid_room():
    r = client.get("/predictions/occupancy/A101")
    assert r.status_code == 200
    assert "predicted_occupancy" in r.json()

def test_prediction_energy_valid_room():
    r = client.get("/predictions/energy/A101")
    assert r.status_code == 200
    assert "predicted_power_kw" in r.json()

def test_alerts_returns_list():
    r = client.get("/alerts")
    assert r.status_code == 200
    assert isinstance(r.json(), list)

def test_simulation_endpoint():
    r = client.post("/simulation", json={"room_id": "A101", "ac_on": False})
    assert r.status_code == 200
    body = r.json()
    assert "estimated_difference_kw" in body

def test_recommendations_generate():
    r = client.post("/recommendations/generate")
    assert r.status_code == 200
    assert "generated" in r.json()

def test_recommendations_list():
    r = client.get("/recommendations")
    assert r.status_code == 200
    assert isinstance(r.json(), list)