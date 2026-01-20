
import sys
import os

# Add project root to sys.path
sys.path.append(os.getcwd())

from app.services.model_manager import ModelManager
from core.config import DOMAINS

def verify():
    manager = ModelManager()
    
    print("Verifying Model Loading...")
    
    # Verify Cars
    print("\n--- Testing CARS ---")
    try:
        models = manager.load_domain("cars")
        if models:
            print("SUCCESS: Cars models loaded.")
        else:
            print("FAILURE: Cars models returned None.")
    except Exception as e:
        print(f"FAILURE: Cars crashed: {e}")

    # Verify Laliga
    print("\n--- Testing LALIGA ---")
    try:
        models = manager.load_domain("laliga")
        if models:
            print("SUCCESS: Laliga models loaded.")
        else:
            print("FAILURE: Laliga models returned None.")
    except Exception as e:
        print(f"FAILURE: Laliga crashed: {e}")

if __name__ == "__main__":
    verify()
