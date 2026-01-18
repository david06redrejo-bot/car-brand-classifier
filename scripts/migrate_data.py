
import os
import shutil
from pathlib import Path

# Paths
source_root = Path("data/raw/train/Car_Brand_Logos")
target_root = Path("data/raw/cars")
background_source = Path("data/raw/background")

target_root.mkdir(parents=True, exist_ok=True)

# 1. Move Train and Test folders
for split in ["Train", "Test"]:
    split_path = source_root / split
    if split_path.exists():
        for brand_dir in split_path.iterdir():
            if brand_dir.is_dir():
                # Target: data/raw/cars/{brand}
                # brand_dir.name e.g. 'hyundai'
                target_brand_dir = target_root / brand_dir.name.lower()
                target_brand_dir.mkdir(exist_ok=True)
                
                print(f"Moving {brand_dir} to {target_brand_dir}...")
                for img in brand_dir.iterdir():
                    if img.is_file():
                        shutil.move(str(img), str(target_brand_dir / img.name))

# 2. Move Background
target_bg = target_root / "background"
target_bg.mkdir(exist_ok=True)
if background_source.exists():
    print(f"Moving {background_source} to {target_bg}...")
    for img in background_source.iterdir():
        if img.is_file():
            shutil.move(str(img), str(target_bg / img.name))
            
print("Migration complete.")
