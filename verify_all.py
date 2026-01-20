
import sys
import os
import time

sys.path.append(os.getcwd())
from app.services.model_manager import ModelManager
from core.config import DOMAINS

def verify_all():
    manager = ModelManager()
    print("--- VERIFICATION SUITE ---")
    
    success_count = 0
    total = len(DOMAINS)
    
    for domain in DOMAINS:
        print(f"\n[Testing {domain.upper()}]")
        try:
            # Force reload
            if manager.active_domain == domain:
                manager.loaded_models.pop(domain, None)
            
            models = manager.load_domain(domain)
            if models:
                print(f"[SUCCESS]: {domain} loaded.")
                success_count += 1
            else:
                print(f"[FAILURE]: {domain} check returned None.")
        except Exception as e:
            print(f"[CRASH]: {domain} - {e}")
            
    print(f"\nSUMMARY: {success_count}/{total} Domains Operational")
    if success_count == total:
        print("SYSTEM STATUS: GREEN")
    else:
        print("SYSTEM STATUS: RED")

if __name__ == "__main__":
    verify_all()
