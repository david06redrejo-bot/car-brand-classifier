
import os
import sys
import numpy as np
import tensorflow as tf
from tensorflow.keras.preprocessing.image import load_img, img_to_array

# Add project root to sys.path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from core.config import DATA_DIR, IMG_SIZE, CLASS_INDICES_PATH, MODELS_DIR
from app.services.model_manager import ModelManager

def verify_model():
    print("Verifying Model...")
    
    # 1. Load Model
    manager = ModelManager()
    model, classes = manager.get_model()
    
    if not model:
        print("FAIL: Model not loaded.")
        return
    
    print(f"Model loaded. Classes: {list(classes.keys())}")
    
    # 2. Pick a sample image (Toyota if exists, else first available)
    cars_dir = os.path.join(DATA_DIR, "cars") # Assuming config.DATA_DIR points correctly or we hardcode
    # DATA_DIR in config.py wasn't explicitly defined in my update, let's look for known path
    # Actually config.py imports BASE_DIR. 
    base_dir = os.path.dirname(os.path.abspath(__file__))
    raw_dir = os.path.join(base_dir, "data", "raw", "cars")
    
    if not os.path.exists(raw_dir):
        print(f"FAIL: Data dir not found at {raw_dir}")
        return

    # Try to find a Toyota folder
    target_brand = "toyota"
    brand_dir = os.path.join(raw_dir, target_brand)
    if not os.path.exists(brand_dir):
        # Just pick first available
        subdirs = [d for d in os.listdir(raw_dir) if os.path.isdir(os.path.join(raw_dir, d))]
        if not subdirs:
            print("FAIL: No class directories found.")
            return
        target_brand = subdirs[0]
        brand_dir = os.path.join(raw_dir, target_brand)
    
    # Pick an image
    images = [f for f in os.listdir(brand_dir) if f.lower().endswith(('.jpg', '.png'))]
    if not images:
        print(f"FAIL: No images in {brand_dir}")
        return
        
    img_path = os.path.join(brand_dir, images[0])
    print(f"Testing on image: {img_path} (Expected: {target_brand})")
    
    # 3. Predict
    img = load_img(img_path, target_size=IMG_SIZE)
    img_array = img_to_array(img)
    img_array = np.expand_dims(img_array, axis=0)
    img_array = img_array / 255.0
    
    predictions = model.predict(img_array)
    pred_idx = np.argmax(predictions)
    confidence = np.max(predictions)
    
    pred_label = classes.get(str(pred_idx))
    
    print(f"Prediction: {pred_label} ({confidence:.2f})")
    
    if pred_label.lower() == target_brand.lower():
        print("PASS: Prediction matches expected label.")
    else:
        print(f"WARNING: Prediction mismatch. Expected {target_brand}, got {pred_label}.")

if __name__ == "__main__":
    verify_model()
