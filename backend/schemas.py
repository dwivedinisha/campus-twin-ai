from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class Building(BaseModel):
    id: int
    name: str

class Room(BaseModel):
    id: int
    building_id: int
    name: str
    capacity: int

class SensorReading(BaseModel):
    timestamp: datetime
    occupancy: int
    temperature_c: float
    humidity_pct: float
    ac_status: str
    lighting_status: str
    class_scheduled: bool
    power_kw: float
    is_weekend: bool
    is_anomaly: bool
    anomaly_type: Optional[str]