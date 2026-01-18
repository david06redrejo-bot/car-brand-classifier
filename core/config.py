"""
core/config.py

Responsibility:
    - Centralizes application configuration and constants.
    - Stores file paths for the persisted models (`MODEL_PATH`, `CODEBOOK_PATH`, `SCALER_PATH`).
    - Uses pathlib for robust path handling.
"""

import os
from pathlib import Path

# Base directory relative to this file
BASE_DIR = Path(__file__).resolve().parent.parent

# Models Directory
MODELS_DIR = BASE_DIR / "models"

# Artifact Paths
CODEBOOK_PATH = MODELS_DIR / "vocabulary.pkl"
SCALER_PATH = MODELS_DIR / "scaler.pkl"
SVM_PATH = MODELS_DIR / "classifier.joblib"


# Model Configuration
# Ensure these match strictly with what was used in training
NUM_CLUSTERS = 500

CLASS_LABELS = [
    'hyundai',
    'lexus',
    'mazda',
    'mercedes',
    'opel',
    'skoda',
    'toyota',
    'volkswagen'
]

# Domain Configuration for ModelManager
DOMAINS = {
    "cars": CLASS_LABELS
}

def get_model_paths(domain):
    """
    Returns the paths for a specific domain's models.
    """
    if domain == "cars":
        return {
            "kmeans": CODEBOOK_PATH,
            "scaler": SCALER_PATH,
            "svm": SVM_PATH
        }
    raise ValueError(f"Unknown domain: {domain}")

