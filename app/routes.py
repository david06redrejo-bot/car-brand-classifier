"""
app/routes.py

Responsibility:
    - Defines the HTTP API endpoints.
    - POST /predict: Orchestrates image reading, feature extraction, and prediction.
"""

from fastapi import APIRouter, File, UploadFile, HTTPException, Request, BackgroundTasks
from app.schemas import PredictionResponse, FeedbackRequest
from core.image_utils import read_image_file
from core.vision_logic import predict_pipeline
from core.config import CLASS_LABELS

router = APIRouter()



# Root endpoint handled in app/main.py to serve static frontend


@router.get("/health")
async def health_check():
    return {"status": "ok"}

@router.get("/classes")
async def get_classes():
    return {"classes": CLASS_LABELS}


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
        prediction_index, confidence = predict_pipeline(
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
        
        return PredictionResponse(label=label_str.title(), confidence=float(confidence))
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Prediction failed: {str(e)}")

@router.post("/feedback")
async def feedback_loop(feedback: FeedbackRequest, background_tasks: BackgroundTasks):
    """
    Endpoint to receive user feedback and trigger retraining.
    """
    try:
        import base64
        from core.active_learning import save_feedback_image, trigger_retraining_task
        
        # Decode image
        # Expecting data:image/jpeg;base64,.....
        if "," in feedback.image_base64:
            header, encoded = feedback.image_base64.split(",", 1)
        else:
            encoded = feedback.image_base64
            
        image_bytes = base64.b64decode(encoded)
        
        # Determine label
        label_to_save = feedback.label.lower()
        if feedback.new_brand_name:
            label_to_save = feedback.new_brand_name.lower()
            
        print(f"Received feedback: {label_to_save}")
        
        # Save image
        save_feedback_image(image_bytes, label_to_save, brand_new=bool(feedback.new_brand_name))
        
        # Trigger retraining in background
        background_tasks.add_task(trigger_retraining_task)
        
        return {"status": "success", "message": "Feedback received. Retraining started."}
        
    except Exception as e:
        print(f"Feedback error: {e}")
        raise HTTPException(status_code=500, detail=str(e))
