"""
app/services/scraper.py

Responsibility:
    - Handles automated image scraping for new brands using DuckDuckGo Search.
    - Downloads, sanitizes, and deduplicates images.
"""

import os
import requests
import hashlib
from duckduckgo_search import DDGS
from concurrent.futures import ThreadPoolExecutor
from core.config import BASE_DIR

class ScraperService:
    def __init__(self):
        self.ddgs = DDGS()
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        }

    def scrape_brand(self, brand_name: str, domain: str = "cars", limit: int = 30):
        """
        Scrapes images for a new brand and saves them to the dataset.
        """
        print(f"Scraping images for: {brand_name} in domain {domain}")
        
        # Create directory: data/raw/{domain}/{brand_name}
        # Note: We assume flat structure for domain or use 'train' subfolder?
        # data_seeder uses data/raw/{domain}/{class}
        # Let's match data_seeder
        target_dir = BASE_DIR / "data" / "raw" / domain / brand_name.lower()
        target_dir.mkdir(parents=True, exist_ok=True)
        
        # Search for images
        query = f"{brand_name} logo {domain}"
        results = self.ddgs.images(query, max_results=limit * 2) 
        
        count = 0
        existing_hashes = set()
        
        # Pre-load existing hashes
        if target_dir.exists():
            for f in os.listdir(target_dir):
                path = target_dir / f
                if path.is_file():
                    try:
                        with open(path, 'rb') as img_f:
                            existing_hashes.add(hashlib.md5(img_f.read()).hexdigest())
                    except: pass

        for res in results:
            if count >= limit:
                break
                
            img_url = res.get('image')
            if not img_url:
                continue
                
            try:
                # Download with timeout
                response = requests.get(img_url, headers=self.headers, timeout=5)
                if response.status_code == 200:
                    content = response.content
                    
                    # Verify it's an image
                    if not content.startswith(b'\xff\xd8') and not content.startswith(b'\x89PNG'):
                        continue # Not JPG or PNG
                        
                    # Hash check
                    img_hash = hashlib.md5(content).hexdigest()
                    if img_hash in existing_hashes:
                        continue
                        
                    existing_hashes.add(img_hash)
                    
                    # Save
                    ext = "jpg" if content.startswith(b'\xff\xd8') else "png"
                    filename = f"{brand_name}_{count}.{ext}"
                    with open(target_dir / filename, "wb") as f:
                        f.write(content)
                        
                    count += 1
                    
            except Exception as e:
                print(f"Failed to download {img_url}: {e}")
                continue
                
        print(f"Successfully scraped {count} images for {brand_name}")
        return count
