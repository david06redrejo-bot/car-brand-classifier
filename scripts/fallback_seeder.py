import os
import requests
import hashlib
from pathlib import Path

# URLs for Laliga logos (Wikimedia/Public sources)
# DISCLAIMER: Using for educational/testing purposes only.
IMAGES = {
    "laliga": {
        "real madrid": [
            "https://upload.wikimedia.org/wikipedia/en/thumb/5/56/Real_Madrid_CF.svg/1200px-Real_Madrid_CF.svg.png",
            "https://logos-world.net/wp-content/uploads/2020/06/Real-Madrid-Logo.png",
            "https://i.pinimg.com/originals/f3/8c/6f/f38c6f1c4e7c7c0c9f1c7c0c9f1c7c0c.png",
            "https://upload.wikimedia.org/wikipedia/kw/thumb/5/56/Real_Madrid_CF.svg/1024px-Real_Madrid_CF.svg.png",
            "https://cdn.freebiesupply.com/logos/large/2x/real-madrid-c-f-logo-png-transparent.png"
        ],
        "barcelona": [
            "https://upload.wikimedia.org/wikipedia/en/thumb/4/47/FC_Barcelona_%28crest%29.svg/1200px-FC_Barcelona_%28crest%29.svg.png",
            "https://logos-world.net/wp-content/uploads/2020/04/Barcelona-Logo.png",
            "https://upload.wikimedia.org/wikipedia/commons/thumb/4/47/FC_Barcelona_%28crest%29.svg/1010px-FC_Barcelona_%28crest%29.svg.png",
             "https://cdn.freebiesupply.com/logos/large/2x/fc-barcelona-logo-png-transparent.png",
             "https://www.pngkit.com/png/full/1-11910_fc-barcelona-logo-png-barcelona-logo-transparent-background.png"
        ],
        "atletico madrid": [
             "https://upload.wikimedia.org/wikipedia/en/thumb/f/f4/Atletico_Madrid_2017_logo.svg/1200px-Atletico_Madrid_2017_logo.svg.png",
             "https://logos-world.net/wp-content/uploads/2020/06/Atletico-Madrid-Logo.png"
        ]
    },
    "fashion": {
        "gucci": [
            "https://upload.wikimedia.org/wikipedia/commons/thumb/7/79/1960s_Gucci_Logo.svg/1200px-1960s_Gucci_Logo.svg.png",
            "https://logos-world.net/wp-content/uploads/2020/04/Gucci-Logo.png"
        ],
        "prada": [
             "https://upload.wikimedia.org/wikipedia/commons/thumb/b/b8/Prada-Logo.svg/1200px-Prada-Logo.svg.png",
             "https://logos-world.net/wp-content/uploads/2020/04/Prada-Logo.png"
        ],
        "nike": [
            "https://upload.wikimedia.org/wikipedia/commons/thumb/a/a6/Logo_NIKE.svg/1200px-Logo_NIKE.svg.png"
        ],
        "chanel": [
            "https://upload.wikimedia.org/wikipedia/en/thumb/9/92/Chanel_logo_interlocking_cs.svg/1200px-Chanel_logo_interlocking_cs.svg.png"
        ]
    },
    "tech": {
        "apple": [
            "https://upload.wikimedia.org/wikipedia/commons/thumb/f/fa/Apple_logo_black.svg/833px-Apple_logo_black.svg.png"
        ],
        "google": [
            "https://upload.wikimedia.org/wikipedia/commons/thumb/2/2f/Google_2015_logo.svg/1200px-Google_2015_logo.svg.png"
        ],
        "microsoft": [
            "https://upload.wikimedia.org/wikipedia/commons/thumb/4/44/Microsoft_logo.svg/1200px-Microsoft_logo.svg.png"
        ]
    },
    "food": {
        "mcdonalds": [
            "https://upload.wikimedia.org/wikipedia/commons/thumb/3/36/McDonald%27s_Golden_Arches.svg/1200px-McDonald%27s_Golden_Arches.svg.png"
        ],
        "kfc": [
            "https://upload.wikimedia.org/wikipedia/commons/thumb/9/91/KFC_Logo.svg/1024px-KFC_Logo.svg.png", 
            "https://logos-world.net/wp-content/uploads/2020/04/KFC-Logo.png"
        ],
        "burger king": [
             "https://upload.wikimedia.org/wikipedia/commons/thumb/8/85/Burger_King_logo_%281999%29.svg/1200px-Burger_King_logo_%281999%29.svg.png",
             "https://logos-world.net/wp-content/uploads/2020/05/Burger-King-Logo.png"
        ]
    }
}

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data" / "raw"

def download_images():
    headers = {
        "User-Agent": "Mozilla/5.0"
    }
    
    for domain, classes in IMAGES.items():
        print(f"Seeding {domain}...")
        for cls, urls in classes.items():
            save_dir = DATA_DIR / domain / cls
            os.makedirs(save_dir, exist_ok=True)
            
            print(f"  Downloading {cls}...")
            count = 0
            for url in urls:
                try:
                    resp = requests.get(url, headers=headers, timeout=10)
                    if resp.status_code == 200:
                        content = resp.content
                        ext = "png" if "png" in url else "jpg"
                        filename = f"{cls.replace(' ', '_')}_{count}.{ext}"
                        with open(save_dir / filename, "wb") as f:
                            f.write(content)
                        count += 1
                        print(f"    Saved {filename}")
                except Exception as e:
                    print(f"    Failed {url}: {e}")
                    
if __name__ == "__main__":
    download_images()
