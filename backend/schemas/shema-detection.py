from pydantic import BaseModel
from typing import List

class DetectionRequest(BaseModel):
    features: List[float]