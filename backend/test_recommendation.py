import sys, os
BASE = os.path.dirname(os.path.abspath(__file__))
sys.path.append(BASE)
sys.path.append(os.path.join(BASE, "routers"))
sys.path.append(os.path.join(BASE, "..", "ml", "inference"))

from datetime import datetime
from predict_occupancy import predict_occupancy
from detect_anomaly import detect_anomaly

now = datetime.now()
print("Current time used for prediction:", now)

predicted_occ = predict_occupancy(
    "A101", now.hour, now.weekday(), now.weekday() >= 5,
    24.0, 50.0, 0, False, 40
)
print("Predicted occupancy:", predicted_occ)

anomaly = detect_anomaly("A101", now.hour, now.weekday(), 0, 24.0, 50.0, True, True, 4.0)
print("Anomaly result:", anomaly)