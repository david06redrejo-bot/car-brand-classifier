
import tensorflow as tf
import os
import json
from core.config import MODEL_PATH, CLASS_INDICES_PATH

def load_trained_model():
    """
    Loads the trained Keras model and class indices.
    """
    if not os.path.exists(MODEL_PATH):
        print(f"Error: Model not found at {MODEL_PATH}")
        return None, None

    if not os.path.exists(CLASS_INDICES_PATH):
        print(f"Error: Class indices not found at {CLASS_INDICES_PATH}")
        return None, None

    print(f"Loading model from {MODEL_PATH}...")
    try:
        model = tf.keras.models.load_model(MODEL_PATH)
        
        with open(CLASS_INDICES_PATH, 'r') as f:
            class_indices = json.load(f)
            
        print("Model loaded successfully.")
        return model, class_indices
    except Exception as e:
        print(f"Failed to load model: {e}")
        return None, None
