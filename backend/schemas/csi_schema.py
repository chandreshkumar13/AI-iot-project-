from pydantic import BaseModel
from typing import List

class CSIRequest(BaseModel):
    csi_matrix: List[List[float]]