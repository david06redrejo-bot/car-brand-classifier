"""
core/locks.py

Global lock definitions to prevent race conditions.
"""
import threading

# Lock to coordinate between prediction (read) and model reloading/saving (write)
# Used in app/routes.py (predict) and app/services/training.py (retrain/save)
PREDICTION_LOCK = threading.Lock()
