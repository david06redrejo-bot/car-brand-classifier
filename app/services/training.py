"""
app/services/training.py

Responsibility:
    - Thread-safe singleton for managing training jobs.
    - Queues or locks training to prevent race conditions.
"""

import threading
import asyncio
from train.train_model import run_training
from core.config import BASE_DIR, CLASS_LABELS, MODELS_DIR

class TrainingService:
    _instance = None
    _lock = threading.Lock()
    _is_training = False

    def __new__(cls):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super(TrainingService, cls).__new__(cls)
                    cls._instance.training_lock = threading.Lock()
        return cls._instance

    def run_training_job(self, domain="cars"):
        """
        Runs the training process in a thread-safe manner for a specific domain.
        Returns True if started, False if already running.
        """
        if self._is_training:
            return False
            
        with self.training_lock:
            try:
                self._is_training = True
                print(f"Starting thread-safe training job for {domain}...")
                
                # Paths - dynamically determined based on domain
                # data/raw/{domain}
                data_path = BASE_DIR / "data" / "raw" / domain
                
                if not data_path.exists():
                    print(f"Data path not found: {data_path}")
                    return False

                # We can either pass the class dirs or just the parent
                # run_training logic was updated to take [parent_path] 
                
                # Get labels from config or directory
                from core.config import DOMAINS
                labels = DOMAINS.get(domain, [])
                
                # Run training
                run_training([str(data_path)], labels, num_clusters=500, domain_name=domain)
                
            except Exception as e:
                print(f"Training failed: {e}")
            finally:
                self._is_training = False
                print("Training job finished.")
                return True

    async def run_async(self, domain="cars"):
        """
        Async wrapper to be called from FastAPI BackgroundTasks.
        """
        loop = asyncio.get_event_loop()
        await loop.run_in_executor(None, self.run_training_job, domain)
