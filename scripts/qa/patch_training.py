import sys
import os

# Add project root to path
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.append(PROJECT_ROOT)

from core.config import CLASS_LABELS
from train import train_model

def run_patched_training():
    print("--- Patched Training for QA (Background Class Injection) ---")
    
    # 1. Inject 'background' class
    # We use 'background' (lowercase) to match the folder name in data/raw/background
    patched_classes = CLASS_LABELS + ['background']
    print(f"Classes: {patched_classes}")
    
    # 2. Inject 'data/raw' path
    # The load_dataset function joins path + class.
    # So 'data/raw' + 'background' -> 'data/raw/background' which contains our images.
    # We also keep the original paths for the car logos.
    original_paths = [
        os.path.join('data', 'raw', 'train', 'Car_Brand_Logos', 'Train'),
        os.path.join('data', 'raw', 'train', 'Car_Brand_Logos', 'Test')
    ]
    
    # Construct absolute paths to be safe, or relative from CWD (project root)
    # Assuming script is run from project root, relative paths work.
    patched_paths = original_paths + [os.path.join('data', 'raw')]
    
    print(f"Dataset Paths: {patched_paths}")
    
    # 3. Trigger Training
    # We use a smaller number of clusters for quick QA testing if needed, or keeping default.
    # The prompt implies we should just include the class.
    try:
        train_model.run_training(patched_paths, patched_classes, domain='cars')
        print(">>> Training Complete with Background Class!")
    except Exception as e:
        print(f"!!! Training Failed: {e}")

if __name__ == "__main__":
    run_patched_training()
