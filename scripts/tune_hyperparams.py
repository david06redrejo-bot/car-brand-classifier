"""
scripts/tune_hyperparams.py

Responsibility:
    - Runs a Grid Search on Vocabulary Size (k).
    - Suggests the optimal k.
    - Saves config/hyperparams.json.
"""

import os
import sys
import json
import argparse

# Add project root to sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from train.train_model import run_training
from core.config import CLASS_LABELS

def tune_k(dataset_paths, k_values=[50, 100, 200, 500]):
    best_k = k_values[0]
    best_acc = 0.0
    results = {}

    for k in k_values:
        print(f"\n[Auto-Tuner] Testing k={k}...")
        try:
            acc = run_training(dataset_paths, CLASS_LABELS, num_clusters=k, save_model=False)
            results[k] = acc
            print(f"[Auto-Tuner] k={k} => Accuracy: {acc*100:.2f}%")
            
            if acc > best_acc:
                best_acc = acc
                best_k = k
        except Exception as e:
            print(f"[Auto-Tuner] Error testing k={k}: {e}")
            
    print(f"\n[Auto-Tuner] Best k found: {best_k} with {best_acc*100:.2f}% accuracy.")
    
    # Save results
    config_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'config')
    os.makedirs(config_dir, exist_ok=True)
    
    config_path = os.path.join(config_dir, 'hyperparams.json')
    with open(config_path, 'w') as f:
        json.dump({
            "best_k": best_k,
            "best_accuracy": best_acc,
            "all_results": results
        }, f, indent=4)
        
    print(f"[Auto-Tuner] Results saved to {config_path}")
    
    # Retrain with best K
    print(f"[Auto-Tuner] Retraining final model with best k={best_k}...")
    run_training(dataset_paths, CLASS_LABELS, num_clusters=best_k, save_model=True)

if __name__ == "__main__":
    # Default paths (try to match train_model.py default or args)
    default_train_path = [
        'data/raw/train/Car_Brand_Logos/Train',
        'data/raw/train/Car_Brand_Logos/Test'
    ]
    
    tune_k(default_train_path)
