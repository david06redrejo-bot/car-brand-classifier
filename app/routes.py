"""
app/routes.py

Responsibility:
    - Defines the HTTP API endpoints.
    - POST /predict: Orchestrates image reading, feature extraction, and prediction.
"""

from fastapi import APIRouter, File, UploadFile, HTTPException, Request
from app.schemas import PredictionResponse
from core.image_utils import read_image_file
from core.vision_logic import predict_pipeline
from core.config import CLASS_LABELS

router = APIRouter()



# Root endpoint handled in app/main.py to serve static frontend


@router.get("/health")
async def health_check():
    return {"status": "ok"}


@router.post("/predict", response_model=PredictionResponse)
async def predict(request: Request, file: UploadFile = File(...)):
    """
    Endpoint to predict image class.
    
    Args:
        request: The FastAPI request object (to access app.state).
        file: Uploaded image file.
    """
    if not request.app.state.kmeans or not request.app.state.svm:
        raise HTTPException(status_code=503, detail="Models not loaded")

    # 1. Read and Decode Image
    try:
        contents = await file.read()
        image = read_image_file(contents)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Invalid image file: {str(e)}")

    # 2. Prediction Pipeline
    try:
        # Pass models from app.state
        prediction_index = predict_pipeline(
            image, 
            request.app.state.kmeans, 
            request.app.state.scaler, 
            request.app.state.svm
        )
        
        # Map index to label
        try:
            label_str = CLASS_LABELS[int(prediction_index)]
        except (IndexError, ValueError):
            label_str = f"Unknown ({prediction_index})"
        
        return PredictionResponse(label=label_str.title(), confidence=1.0)
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Prediction failed: {str(e)}")
