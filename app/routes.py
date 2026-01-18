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
async def predict(request: Request, domain: str = "cars", file: UploadFile = File(...)):
    """
    Endpoint to predict image class for a specific domain.
    """
    from app.services.model_manager import ModelManager
    from core.config import DOMAINS
    
    if domain not in DOMAINS:
        raise HTTPException(status_code=400, detail="Invalid domain")
        
    manager = ModelManager()
    models = manager.load_domain(domain)
    
    if not models:
        raise HTTPException(status_code=503, detail=f"Models for {domain} not available (or not trained).")

    # 1. Read and Decode Image
    try:
        contents = await file.read()
        image = read_image_file(contents)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Invalid image file: {str(e)}")

    # 2. Prediction Pipeline
    try:
        prediction_index, confidence = predict_pipeline(
            image, 
            models['kmeans'], 
            models['scaler'], 
            models['svm']
        )
        
        # Check for Unknown (>35% usually 0.35, but let's check format)
        # predict_pipeline returns probability 0-1
        
        # Map index to label
        try:
            # We must use the class list for this specific domain
            labels = DOMAINS[domain]
            label_str = labels[int(prediction_index)]
        except (IndexError, ValueError):
            label_str = f"Unknown ({prediction_index})"
        
        if confidence < 0.35:
            label_str = "Unrecognized Entity"
        
        return PredictionResponse(label=label_str.title(), confidence=float(confidence))
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Prediction failed: {str(e)}")

@router.post("/feedback")
async def feedback_loop(feedback: FeedbackRequest, background_tasks: BackgroundTasks, domain: str = "cars"):
    """
    Endpoint to receive user feedback, scrape images (if new), and trigger retraining.
    """
    try:
        import base64
        from core.active_learning import save_feedback_image
        from app.services.training import TrainingService
        from app.services.scraper import ScraperService
        
        # 1. Decode User Image
        if "," in feedback.image_base64:
            header, encoded = feedback.image_base64.split(",", 1)
        else:
            encoded = feedback.image_base64
            
        image_bytes = base64.b64decode(encoded)
        
        # 2. Determine Logic
        label_to_save = feedback.label.lower()
        is_new_brand = False
        
        if feedback.new_brand_name:
            label_to_save = feedback.new_brand_name.lower().strip()
            is_new_brand = True
            
        print(f"Received feedback: {label_to_save} (New: {is_new_brand})")
        
        # 3. Save the single feedback image
        save_feedback_image(image_bytes, label_to_save, domain=domain, brand_new=is_new_brand)
        
        # 4. If New Brand -> Trigger Scraper
        if is_new_brand:
            # We add a background task to scrape MORE images to make the class robust
            scraper = ScraperService()
            # Run blocking scrape in thread pool
            background_tasks.add_task(scraper.scrape_brand, label_to_save, domain=domain)
        
        # 5. Trigger Retraining (Thread-Safe)
        trainer = TrainingService()
        background_tasks.add_task(trainer.run_async, domain=domain)
        
        return {"status": "success", "message": "Feedback received. System updating in background."}
        
    except Exception as e:
        print(f"Feedback error: {e}")
        raise HTTPException(status_code=500, detail=str(e))
