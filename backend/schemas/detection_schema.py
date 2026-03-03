from pydantic import BaseModel

class DetectionRequest(BaseModel):
    signal_strength: float
    frequency: float
    movement_speed: float