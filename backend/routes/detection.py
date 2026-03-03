from fastapi import APIRouter, HTTPException
from schemas.detection_schema import DetectionRequest
from services.csi_service import analyze_signal

router = APIRouter()

@router.post("/detect")
def detect_animal(request: DetectionRequest):
    try:
        result = analyze_signal(request.features)

        return {
            "status": "success",
            "prediction": result
        }

    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))