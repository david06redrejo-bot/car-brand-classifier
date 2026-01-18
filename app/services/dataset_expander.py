"""
app/services/dataset_expander.py

Responsibility:
    - Autonomous service to expand the dataset for a specific domain/label.
    - Scrapes new images using DuckDuckGo.
    - Sanitizes images using core utilities.
    - Triggers full model retraining upon completion.
"""

import os
import requests
import hashlib
from duckduckgo_search import DDGS
from core.config import BASE_DIR
from core.image_utils import sanitize_image
from app.services.training import TrainingService

def expand_dataset(domain: str, label: str):
    """
    1. SCRAPE: Use duckduckgo_search to download 40 images of '{label} logo'.
       - Save to data/raw/{domain}/{label}/
       - Uses core.image_utils.sanitize_image.
    
    2. RETRAIN: Once scraping is done, trigger the training pipeline.
    """
    print(f"AUTOMATION: Expansion requested for {domain}/{label}")
    
    # 1. Setup Logic
    target_dir = BASE_DIR / "data" / "raw" / domain / label
    target_dir.mkdir(parents=True, exist_ok=True)
    
    query = f"{label} logo {domain} white background"
    limit = 60 # Download budget
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }
    
    ddgs = DDGS()
    print(f"Searching for: {query}")
    try:
        results = ddgs.images(query, max_results=limit*2)
    except Exception as e:
        print(f"Search failed: {e}")
        return

    # 2. Download & Sanitize
    count = 0
    existing_hashes = set()
    
    # Load existing to avoid dupes
    if target_dir.exists():
        for f in os.listdir(target_dir):
            path = target_dir / f
            if path.is_file():
                try:
                    with open(path, 'rb') as img_f:
                        existing_hashes.add(hashlib.md5(img_f.read()).hexdigest())
                except: pass
                
    current_files = len(os.listdir(target_dir))
    target_count = current_files + 40 # Aim for +40 new images
    
    for res in results:
        if count >= 40: # Stop after adding 40 new ones
            break
            
        img_url = res.get('image')
        if not img_url: continue
        
        try:
            response = requests.get(img_url, headers=headers, timeout=5)
            if response.status_code == 200:
                content = response.content
                
                # Basic check
                if not content.startswith(b'\xff\xd8') and not content.startswith(b'\x89PNG'):
                    continue
                    
                img_hash = hashlib.md5(content).hexdigest()
                if img_hash in existing_hashes:
                    continue
                    
                ext = "jpg" if content.startswith(b'\xff\xd8') else "png"
                filename = f"{label.replace(' ', '_')}_{img_hash[:8]}.{ext}"
                save_path = target_dir / filename
                
                with open(save_path, "wb") as f:
                    f.write(content)
                
                # Sanitize
                if sanitize_image(save_path, max_size=500):
                    existing_hashes.add(img_hash)
                    count += 1
                    print(f"  [+] Downloaded: {filename}", end='\r')
                
        except Exception:
            pass
            
    print(f"\ndataset_expander: Added {count} new images for {label}.")
    
    # 3. Retrain
    if count > 0:
        print("Triggering retraining pipeline...")
        success = TrainingService.run_sync(domain=domain)
        if success:
            print("Retraining started successfully.")
        else:
            print("Retraining skipped (already running).")
    else:
        print("No new images added. Retraining skipped.")

if __name__ == "__main__":
    # Test run
    import sys
    if len(sys.argv) > 2:
        expand_dataset(sys.argv[1], sys.argv[2])
    else:
        print("Usage: python -m app.services.dataset_expander <domain> <label>")
