import sys, os
sys.path.append(os.path.join(os.path.dirname(__file__), "..", "ml", "inference"))
from predict_occupancy import predict_occupancy
from predict_energy import predict_energy
from detect_anomaly import detect_anomaly

def test_occupancy_prediction_in_valid_range():
    pred = predict_occupancy("A101", 9, 1, False, 24.0, 50.0, 20, True, 40)
    assert 0 <= pred <= 40

def test_occupancy_prediction_never_negative():
    pred = predict_occupancy("A101", 3, 6, True, 20.0, 60.0, 0, False, 40)
    assert pred >= 0

def test_energy_prediction_never_negative():
    pred = predict_energy("A101", 9, 1, 20, 24.0, 50.0, True, True)
    assert pred >= 0

def test_energy_prediction_higher_with_ac_on():
    off = predict_energy("A101", 9, 1, 20, 28.0, 50.0, False, True)
    on = predict_energy("A101", 9, 1, 20, 28.0, 50.0, True, True)
    assert on > off

def test_anomaly_detects_extreme_case():
    result = detect_anomaly("A101", 14, 2, 0, 30, 40, True, False, 9.0)
    assert result["is_anomaly"] is True

def test_anomaly_normal_case():
    result = detect_anomaly("A101", 14, 2, 25, 24, 50, True, True, 4.5)
    assert result["is_anomaly"] is False

def test_anomaly_returns_expected_keys():
    result = detect_anomaly("A101", 14, 2, 25, 24, 50, True, True, 4.5)
    assert "is_anomaly" in result
    assert "anomaly_score" in result
    assert "power_residual" in result