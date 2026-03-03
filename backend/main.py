from fastapi import FastAPI
from routes.detection import router as detection_router

app = FastAPI()

app.include_router(detection_router)

@app.get("/")
def home():
    return {"message": "CSI Animal Detection Backend 🚀"}
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)