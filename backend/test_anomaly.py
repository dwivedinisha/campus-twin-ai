import sys
sys.path.append('ml/inference')
from detect_anomaly import detect_anomaly

print('Should likely be anomaly:', detect_anomaly('A101', 14, 2, 0, 30, 40, True, False, 9.0))
print('Should likely be normal:', detect_anomaly('A101', 14, 2, 25, 24, 50, True, True, 4.5))