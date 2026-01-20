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

# Domain Class Definitions
CLASS_LABELS_CARS = [
    'hyundai', 'lexus', 'mazda', 'mercedes', 'opel', 'skoda', 'toyota', 'volkswagen', 'background'
]

CLASS_LABELS_FASHION = [
    'gucci', 'louis vuitton', 'chanel', 'prada', 'nike', 'adidas', 'zara', 'h&m'
]

CLASS_LABELS_LALIGA = [
    'real madrid', 'barcelona', 'atletico madrid', 'valencia', 'sevilla', 'betis'
]

CLASS_LABELS_TECH = [
    'apple', 'google', 'microsoft', 'amazon', 'tesla', 'samsung', 'sega'
]

CLASS_LABELS_FOOD = [
    'mcdonalds', 'burger king', 'kfc', 'starbucks', 'subway', 'pizza hut', 'dominos'
]

# Default for backward compatibility if imported directly
CLASS_LABELS = CLASS_LABELS_CARS

# Domain Configuration for ModelManager
DOMAINS = {
    "cars": CLASS_LABELS_CARS,
    "fashion": CLASS_LABELS_FASHION,
    "laliga": CLASS_LABELS_LALIGA,
    "tech": CLASS_LABELS_TECH,
    "food": CLASS_LABELS_FOOD
}

# Metrics Directory
METRICS_DIR = BASE_DIR / "static" / "metrics"

def get_model_paths(domain):
    """
    Returns the paths for a specific domain's models.
    """
    domain_model_dir = MODELS_DIR / domain
    return {
        "kmeans": domain_model_dir / "kmeans.pkl",
        "scaler": domain_model_dir / "scaler.pkl",
        "svm": domain_model_dir / "svm.pkl",
        "classes": domain_model_dir / "classes.pkl"
    }
