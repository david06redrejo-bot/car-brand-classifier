"""
app/services/model_manager.py

Responsibility:
    - Singleton class to manage the lifecycle of the Deep Learning model.
    - Loads the model on startup.
    - Provides access to the model for the application.
"""

import os
import sys
from core.dl_loader import load_trained_model

class ModelManager:
    _instance = None
    _model = None
    _classes = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(ModelManager, cls).__new__(cls)
            cls._instance.load_model()
        return cls._instance

    def load_model(self):
        """
        Loads the Keras model and class indices.
        """
        print("ModelManager: Loading Deep Learning Model...")
        self._model, self._classes = load_trained_model()
        
        if self._model:
            print(f"ModelManager: Model loaded successfully. Classes: {list(self._classes.keys())[:5]}...")
        else:
            print("ModelManager: Failed to load model.")

    def get_model(self):
        """
        Returns the loaded model and class indices.
        """
        if self._model is None:
            # Try reloading if not loaded
            self.load_model()
            
        return self._model, self._classes

    # Legacy method signature for compatibility during refactor, but essentially just returns the single model
    def load_domain(self, domain="cars"):
        return self.get_model()
