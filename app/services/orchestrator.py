"""
app/services/orchestrator.py

Orchestrates cross-service logic for the Self-Healing Data Loop.
"""

import app.services.dataset_services as dataset_services
import app.services.training_services as training_services

def expand_and_retrain(domain: str, label: str):
    """
    Orchestrates the Self-Healing Data Loop:
    1. Expand dataset (Scrape new images for the Label).
    2. Retrain the Domain Model (Update Knowledge).
    
    This ensures that when a new class is detected (Starvation Case),
    we first gather data, THEN retrain, maximizing the fix efficiency.
    """
    print(f"[Orchestrator] Self-Healing triggered for {domain} -> {label}")
    
    # 1. Expand (Scrape)
    print(f"[Orchestrator] Expanding dataset...")
    count = dataset_services.expand_dataset(domain=domain, label=label)
    print(f"[Orchestrator] Expansion complete. Added {count} images.")
    
    # 2. Retrain
    print(f"[Orchestrator] Retraining domain model...")
    training_services.retrain_domain(domain=domain)
    print(f"[Orchestrator] Retraining triggered.")
