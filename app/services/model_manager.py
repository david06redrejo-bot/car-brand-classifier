"""
app/services/model_manager.py

Responsibility:
    - Manages lazy loading of domain-specific models.
    - Implements LRU-like behavior to free memory.
"""

import joblib
import threading
from core.config import get_model_paths, DOMAINS

class ModelManager:
    _instance = None
    _lock = threading.Lock()
    
    def __new__(cls):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super(ModelManager, cls).__new__(cls)
                    cls._instance.loaded_models = {} # {domain: {kmeans, scaler, svm}}
                    cls._instance.active_domain = None
        return cls._instance

    def load_domain(self, domain):
        """
        Loads models for the specified domain. 
        Unloads previous domain to save RAM (MVP approach: keep only 1 active).
        """
        if domain not in DOMAINS:
            raise ValueError(f"Invalid domain: {domain}")
            
        if self.active_domain == domain and domain in self.loaded_models:
            return self.loaded_models[domain]
            
        with self._lock:
            # Check again inside lock
            if self.active_domain == domain and domain in self.loaded_models:
                return self.loaded_models[domain]
                
            print(f"Loading models for domain: {domain}...")
            
            # Unload previous to be safe on RAM
            if self.active_domain and self.active_domain != domain:
                print(f"Unloading domain: {self.active_domain}")
                self.loaded_models.pop(self.active_domain, None)
            
            paths = get_model_paths(domain)
            
            try:
                models = {
                    "kmeans": joblib.load(paths['kmeans']),
                    "scaler": joblib.load(paths['scaler']),
                    "svm": joblib.load(paths['svm'])
                }
                self.loaded_models[domain] = models
                self.active_domain = domain
                print(f"Models for {domain} loaded successfully.")
                return models
            except FileNotFoundError:
                print(f"Models for {domain} not found at {paths}.")
                return None
            except Exception as e:
                print(f"Error loading models for {domain}: {e}")
                return None

    def get_models(self, domain):
        return self.load_domain(domain)
