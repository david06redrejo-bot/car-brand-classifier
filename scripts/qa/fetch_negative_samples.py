import os
import time
import requests
from duckduckgo_search import DDGS
from concurrent.futures import ThreadPoolExecutor

# Configuration
OUTPUT_DIR = os.path.join("data", "raw", "background")
MAX_IMAGES_PER_QUERY = 40
QUERIES = [
    "random street scene",
    "nature landscape",
    "office interior",
    "texture background",
    "crowd of people walking",
    "abstract geometric shapes",
    "forest trees",
    "city skyline daytime"
]

def download_image(url, save_path):
    """Downloads an image from a URL to the specified path."""
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        with open(save_path, 'wb') as f:
            f.write(response.content)
        # Verify it's actually an image
        if os.path.getsize(save_path) < 1024: # Skip tiny files
            os.remove(save_path)
            return False
        return True
    except Exception as e:
        if os.path.exists(save_path):
            os.remove(save_path)
        return False

def fetch_negative_samples():
    """Fetches negative samples from DuckDuckGo."""
    if not os.path.exists(OUTPUT_DIR):
        os.makedirs(OUTPUT_DIR)

    print(f"Starting download of negative samples (Background class) to {OUTPUT_DIR}...")
    
    total_downloaded = 0
    
    with DDGS() as ddgs:
        for query in QUERIES:
            print(f"Searching for: '{query}'...")
            try:
                # DuckDuckGo search
                results = ddgs.images(
                    query,
                    region="wt-wt",
                    safesearch="off",
                    max_results=MAX_IMAGES_PER_QUERY,
                )
                
                count = 0
                for i, result in enumerate(results):
                    image_url = result.get('image')
                    if not image_url:
                        continue
                        
                    filename = f"bg_{query.replace(' ', '_')}_{i}.jpg"
                    save_path = os.path.join(OUTPUT_DIR, filename)
                    
                    if download_image(image_url, save_path):
                        count += 1
                        total_downloaded += 1
                        print(f"  [+] Downloaded: {filename}")
                    
                    if count >= MAX_IMAGES_PER_QUERY:
                        break
                        
            except Exception as e:
                print(f"  [-] Error searching for '{query}': {e}")
            
            # Be nice to the API
            time.sleep(1)

    print(f"\nDownload complete. Total 'Background' images: {total_downloaded}")

if __name__ == "__main__":
    fetch_negative_samples()
