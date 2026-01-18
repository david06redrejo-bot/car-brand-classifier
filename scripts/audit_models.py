"""
scripts/audit_models.py

Responsibility:
    - Forensics check for model integrity.
    - Iterates through all defined DOMAINS in config.
    - Verifies that expected artifacts (kmeans, scaler, svm) exist.
    - Returns exit code 1 if critical files are missing (CI/CD failure signal).
"""

import sys
import os
from pathlib import Path

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.config import DOMAINS, get_model_paths

def audit_system():
    print("--- OMNIVISION SYSTEM AUDIT ---")
    
    missing_critical = False
    
    for domain in DOMAINS.keys():
        print(f"\n[AUDIT] Checking Domain: {domain.upper()}")
        
        try:
            paths = get_model_paths(domain)
        except Exception as e:
            print(f"  [ERROR] Configuration failure: {e}")
            missing_critical = True
            continue
            
        domain_missing = False
        for artifact_name, artifact_path in paths.items():
            path_obj = Path(artifact_path)
            if path_obj.exists():
                print(f"  [OK] {artifact_name}: {path_obj.name}")
            else:
                print(f"  [MISSING] {artifact_name}: {path_obj} (CRITICAL)")
                domain_missing = True
        
        if domain_missing:
            print(f"  >>> STATUS: FAILED")
            missing_critical = True
        else:
            print(f"  >>> STATUS: OPERATIONAL")

    print("\n-------------------------------")
    if missing_critical:
        print("CRITICAL ERROR: System Integrity Compromised. Retraining Required.")
        sys.exit(1)
    else:
        print("SYSTEM HEALTHY. All modules online.")
        sys.exit(0)

if __name__ == "__main__":
    audit_system()
