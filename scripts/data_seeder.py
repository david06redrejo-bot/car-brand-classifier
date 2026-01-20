"""
scripts/data_seeder.py

Responsibility:
    - Automated data acquisition for multi-domain system.
    - Uses duckduckgo_search to download images.
    - Sanitizes and resizes images.
"""

import argparse
import os
import sys
import shutil
import hashlib
import cv2
import numpy as np
import requests
from pathlib import Path
from duckduckgo_search import DDGS

# Fix path to import core.config
sys.path.append(str(Path(__file__).parent.parent))
from core.config import BASE_DIR, DOMAINS
from core.image_utils import sanitize_image

DATA_ROOT = BASE_DIR / "data" / "raw"

def seed_domain(domain, limit=40):
    print(f"--- Seeding Domain: {domain.upper()} ---")
    ddgs = DDGS()
    classes = DOMAINS[domain]
    
    domain_dir = DATA_ROOT / domain
    os.makedirs(domain_dir, exist_ok=True)
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }
    
    for cls in classes:
        print(f"Processing Class: {cls}")
        class_dir = domain_dir / cls
        os.makedirs(class_dir, exist_ok=True)
        
        # Check if already populated
        if len(os.listdir(class_dir)) >= limit:
            print(f"  Skipping {cls} (Already has data)")
            continue
            
        query = f"{cls} logo white background"
        
        # Retry logic for rate limits
        import time
        max_retries = 3
        results = []
        for attempt in range(max_retries):
            try:
                # Sleep to respect rate limits
                time.sleep(2 * (attempt + 1)) 
                results = ddgs.images(query, max_results=limit * 2) 
                break
            except Exception as e:
                print(f"  Search error (Attempt {attempt+1}/{max_retries}): {e}")
                time.sleep(5)
 
        
        count = 0
        existing_hashes = set()
        
        # Load existing hashes
        for f in os.listdir(class_dir):
            path = class_dir / f
            if path.is_file():
                try:
                    with open(path, 'rb') as img_f:
                        existing_hashes.add(hashlib.md5(img_f.read()).hexdigest())
                except:
                    pass

        downloaded_this_run = 0
        for res in results:
            if len(os.listdir(class_dir)) >= limit:
                break
                
            img_url = res.get('image')
            if not img_url:
                continue
                
            try:
                response = requests.get(img_url, headers=headers, timeout=5)
                if response.status_code == 200:
                    content = response.content
                    
                    if not content.startswith(b'\xff\xd8') and not content.startswith(b'\x89PNG'):
                        continue
                        
                    img_hash = hashlib.md5(content).hexdigest()
                    if img_hash in existing_hashes:
                        continue
                        
                    ext = "jpg" if content.startswith(b'\xff\xd8') else "png"
                    filename = f"{cls.replace(' ', '_')}_{hashlib.md5(img_url.encode()).hexdigest()[:8]}.{ext}"
                    save_path = class_dir / filename
                    
                    with open(save_path, "wb") as f:
                        f.write(content)
                    
                    # Post-process
                    if sanitize_image(save_path):
                        existing_hashes.add(img_hash)
                        downloaded_this_run += 1
                        print(f"  Downloaded: {filename}", end='\r')
                    
            except Exception:
                pass
                
        print(f"\n  Finished {cls}: Added {downloaded_this_run} images.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Seed data for OmniVision")
    parser.add_argument("--domain", type=str, default="all", help="Target domain (cars, fashion, laliga, tech, food) or 'all'")
    args = parser.parse_args()
    
    if args.domain == "all":
        for d in DOMAINS.keys():
            seed_domain(d)
    elif args.domain in DOMAINS:
        seed_domain(args.domain)
    else:
        print(f"Invalid domain. Available: {list(DOMAINS.keys())}")
