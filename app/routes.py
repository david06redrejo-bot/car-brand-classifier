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
    
    # Harden domain input
    domain = domain.lower().strip()
    
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
    except ValueError as e:
        # read_image_file raises ValueError for bad images
        print(f"Image Error: {e}")
        raise HTTPException(status_code=400, detail=f"Invalid image format: {str(e)}")
    except Exception as e:
        print(f"Upload Error: {e}")
        raise HTTPException(status_code=422, detail=f"Could not read file: {str(e)}")

    # 2. Prediction Pipeline
    try:
        with PREDICTION_LOCK:
            prediction_index, confidence = predict_pipeline(
                image, 
                models['kmeans'], 
                models['scaler'], 
                models['svm']
            )
        
        # Map index to label
        try:
            # We must use the class list for this specific domain
            labels = models.get('classes', DOMAINS.get(domain, []))
            if int(prediction_index) < len(labels):
                label_str = labels[int(prediction_index)]
            else:
                print(f"Warning: Index {prediction_index} out of bounds for {domain}")
                label_str = f"Unknown ({prediction_index})"
        except (IndexError, ValueError) as e:
            print(f"Label Mapping Error: {e}")
            label_str = f"Processing Error ({prediction_index})"
        
        if confidence < 0.35:
            label_str = "Unrecognized Entity"
        
        return PredictionResponse(label=label_str.title(), confidence=float(confidence))
        
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Prediction Internal Error: {str(e)}")

# GLOBAL LOCK to prevent race conditions during model swapping/prediction
from core.locks import PREDICTION_LOCK

@router.post("/feedback")
async def feedback_loop(feedback: FeedbackRequest, background_tasks: BackgroundTasks, domain: str = "cars"):
    """
    Endpoint to receive user feedback, scrape images (if new), and trigger retraining.
    Implements Self-Healing Data Loop via Orchestrator.
    """
    try:
        import base64
        from core.active_learning import save_feedback_image
        import app.services.orchestrator as orchestrator
        from core.config import BASE_DIR
        
        # 1. Decode & Save Image
        if "," in feedback.image_base64:
            header, encoded = feedback.image_base64.split(",", 1)
        else:
            encoded = feedback.image_base64
            
        image_bytes = base64.b64decode(encoded)
        
        # Determine Logic
        label_to_save = feedback.label.lower()
        if feedback.new_brand_name:
            label_to_save = feedback.new_brand_name.lower().strip()
            
        print(f"Received feedback: {label_to_save}")
        
        # save_feedback_image returns path
        save_feedback_image(image_bytes, label_to_save, domain=domain, brand_new=bool(feedback.new_brand_name))
        
        # 2. Check for STARVATION (New or rare class)
        target_dir = BASE_DIR / "data" / "raw" / domain / label_to_save
        file_count = len([f for f in target_dir.iterdir() if f.is_file()])
        # If we have very few images (e.g. just the one we saved), we need expansion.
        is_starved = file_count < 5
        
        # 3. Trigger Orchestrator
        if is_starved:
            # CASE B: STARVATION -> Expand then Retrain
            background_tasks.add_task(orchestrator.expand_and_retrain, domain=domain, label=label_to_save)
            action = "expanding_and_retraining"
        else:
            # CASE A: REFINEMENT -> Just Retrain
            import app.services.training_services as training_services
            background_tasks.add_task(training_services.retrain_domain, domain=domain)
            action = "retraining"

        return {"status": "accepted", "action": action}
        
    except Exception as e:
        print(f"Feedback error: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))
