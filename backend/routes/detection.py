from fastapi import APIRouter, HTTPException
from schemas.csi_schema import CSIRequest
from services.csi_service import analyze_signal

router = APIRouter()

@router.post("/detect")
def detect(request: CSIRequest):
    try:
        result = analyze_signal(request.csi_matrix)
        return {
            "status": "success",
            "result": result
        }
    except ValueError as ve:
        raise HTTPException(status_code=400, detail=str(ve))
    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal server error")