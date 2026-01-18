"""
core/active_learning.py

Responsibility:
    - Handles user feedback (saving correct/incorrect images).
    - Triggers model retraining.
    - (Future) Scrapes new brand images.
"""

import os
import shutil
import uuid
import asyncio
from pathlib import Path
from core.config import BASE_DIR, CLASS_LABELS
from train.train_model import run_training

# Directory to save feedback images
FEEDBACK_DIR = BASE_DIR / "data" / "feedback"
os.makedirs(FEEDBACK_DIR, exist_ok=True)

def save_feedback_image(image_bytes: bytes, label: str, brand_new: bool = False):
    """
    Saves the image to the training dataset structure.
    """
    # Define target directory
    # If it's a new brand, we might need to create the directory in the raw data buffer
    # taking a simplified approach: save to 'data/raw/train/Car_Brand_Logos/Train/<label>'
    # We assume the directory structure exists or we create it.
    
    target_dir = BASE_DIR / "data" / "raw" / "train" / "Car_Brand_Logos" / "Train" / label
    
    if not target_dir.exists():
        if brand_new:
            target_dir.mkdir(parents=True, exist_ok=True)
            # Also add to CLASS_LABELS in config? 
            # modifying code at runtime is risky. 
            # For now, we just save the file. The next training run needs to pick it up.
            # ideally we should append to a dynamic config or database.
        else:
            # If label is known but folder invalid (metric learning?), just create it
            target_dir.mkdir(parents=True, exist_ok=True)
            
    filename = f"feedback_{uuid.uuid4().hex}.jpg"
    file_path = target_dir / filename
    
    with open(file_path, "wb") as f:
        f.write(image_bytes)
        
    return str(file_path)

async def trigger_retraining_task():
    """
    Background task to run training.
    """
    print("Triggering background retraining...")
    # Run in a separate thread/process so it doesn't block
    # We can call the run_training function directly if it's thread-safe enough
    # run_training reloads data from disk, so it should pick up the new file.
    
    # HARDCODED PATHS matching main.py logic for now
    train_path = [
        str(BASE_DIR / 'data' / 'raw' / 'train' / 'Car_Brand_Logos' / 'Train'), 
        str(BASE_DIR / 'data' / 'raw' / 'train' / 'Car_Brand_Logos' / 'Test')
    ]
    
    # We need to run this in an executor because it's CPU bound and blocking
    loop = asyncio.get_event_loop()
    await loop.run_in_executor(None, run_training, train_path, CLASS_LABELS, 500)
    print("Background retraining complete.")
