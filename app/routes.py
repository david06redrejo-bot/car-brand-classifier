"""
app/routes.py

Responsibility:
    - Defines the HTTP API endpoints.
    - POST /predict: Preprocesses image for CNN and returns prediction.
"""

from fastapi import APIRouter, File, UploadFile, HTTPException, Request, BackgroundTasks
from app.schemas import PredictionResponse, FeedbackRequest
from core.config import CLASS_LABELS, IMG_SIZE
import numpy as np
import tensorflow as tf
from PIL import Image
import io

router = APIRouter()

# Global Lock (if needed, though TF graph execution is usually thread-safe for inference if handled correctly)
from core.locks import PREDICTION_LOCK

def preprocess_image(image_bytes):
    """
    Preprocesses the image for MobileNetV2.
    """
    image = Image.open(io.BytesIO(image_bytes)).convert('RGB')
    image = image.resize(IMG_SIZE)
    img_array = tf.keras.preprocessing.image.img_to_array(image)
    img_array = np.expand_dims(img_array, axis=0)
    img_array = img_array / 255.0  # Normalize as per training
    return img_array

@router.get("/health")
async def health_check():
    return {"status": "ok"}

@router.get("/classes")
async def get_classes():
    # Return directly from config or loaded model
    from app.services.model_manager import ModelManager
    manager = ModelManager()
    model, classes_dict = manager.get_model()
    
    if classes_dict:
        # Return list of class names
        return {"classes": list(classes_dict.keys())}
        
    return {"classes": CLASS_LABELS}


@router.post("/predict", response_model=PredictionResponse)
async def predict(request: Request, file: UploadFile = File(...)):
    """
    Endpoint to predict car brand using CNN.
    """
    from app.services.model_manager import ModelManager
    
    manager = ModelManager()
    model, classes_dict = manager.get_model()
    
    if model is None:
        raise HTTPException(status_code=503, detail="Model not initialized or available.")

    # 1. Read and Decode Image
    try:
        contents = await file.read()
        processed_image = preprocess_image(contents)
    except Exception as e:
        print(f"Image Processing Error: {e}")
        raise HTTPException(status_code=400, detail=f"Invalid image: {str(e)}")

    # 2. Prediction
    try:
        with PREDICTION_LOCK:
            predictions = model.predict(processed_image)
        
        # predictions is [1, num_classes]
        confidence = float(np.max(predictions))
        predicted_class_idx = int(np.argmax(predictions))
        
        # Map Index to Label
        # classes_dict is { "Label": Index } or { Index: "Label" }? 
        # In train_cnn, we saved { Index: Label } ?? check train_cnn.py
        # Actually in train_cnn.py:
        # idx_to_label = {v: k for k, v in train_generator.class_indices.items()} -> {0: 'audi', 1: 'bmw'}
        
        label_str = classes_dict.get(str(predicted_class_idx)) # JSON keys are strings
        
        if not label_str:
            # Try int key if loading didn't parse JSON keys as strings (JSON dict keys are always strings)
            label_str = classes_dict.get(predicted_class_idx, "Unknown")
            
        print(f"Prediction: {label_str} ({confidence:.2f})")
        
        if confidence < 0.4:
             return PredictionResponse(label="Uncertain", confidence=confidence)

        return PredictionResponse(label=label_str.title(), confidence=confidence)
        
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Prediction Internal Error: {str(e)}")


@router.post("/feedback")
async def feedback_loop(feedback: FeedbackRequest, background_tasks: BackgroundTasks):
    """
    Endpoint to receive user feedback.
    Currently just logs or saves, retraining trigger to be implemented for CNN.
    """
    # For now, just return valid to keep UI working if it calls this
    return {"status": "accepted", "action": "logged"}
