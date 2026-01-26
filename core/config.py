"""
core/config.py

Responsibility:
    - Centralizes application configuration and constants.
    - Stores file paths for the persisted models (`MODEL_PATH`).
    - Uses pathlib for robust path handling.
"""

import os
from pathlib import Path

# Base directory relative to this file
BASE_DIR = Path(__file__).resolve().parent.parent

# Models Directory
MODELS_DIR = BASE_DIR / "models"

# Artifact Paths
# Deep Learning Model (Keras/TensorFlow)
MODEL_PATH = MODELS_DIR / "car_brand_model.h5"
CLASS_INDICES_PATH = MODELS_DIR / "class_indices.json"

# Legacy Paths (Kept briefly to avoid immediate import errors, but will be phased out)
CODEBOOK_PATH = MODELS_DIR / "vocabulary.pkl"
SCALER_PATH = MODELS_DIR / "scaler.pkl"
SVM_PATH = MODELS_DIR / "classifier.joblib"


# Domain Class Definitions
# WE ARE FOCUSING ONLY ON CARS NOW
CLASS_LABELS = [
    'hyundai', 'lexus', 'mazda', 'mercedes', 'opel', 'skoda', 'toyota', 'volkswagen'
]

# For backward compatibility / safety, we treat "cars" as the only domain
DOMAINS = {
    "cars": CLASS_LABELS
}

# Image Configuration
IMG_SIZE = (224, 224)
BATCH_SIZE = 32

# Metrics Directory
METRICS_DIR = BASE_DIR / "static" / "metrics"

def get_model_paths(domain="cars"):
    """
    Returns the paths for the Deep Learning model.
    Domain argument is deprecated but kept for signature compatibility.
    """
    return {
        "model": MODEL_PATH,
        "classes": CLASS_INDICES_PATH
    }
