"""
scripts/refinery.py

Responsibility:
    - Data Cleaning: Deduplicates images using Perceptual Hashing (pHash).
    - Data Augmentation: Expands the dataset using synthetic transformations (Rotation, Brightness, Blur).
    - Ensures every class has at least 100 samples.

Usage:
    python scripts/refinery.py --dataset_path "data/raw/train/Car_Brand_Logos/Train"
"""

import os
import sys
import argparse
import cv2
import numpy as np
from PIL import Image
import imagehash
import shutil

# Add project root to sys.path to ensure we can import core if needed (though not strictly needed here)
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def compute_phash(image_path):
    """
    Computes Perceptual Hash for an image.
    """
    try:
        # ImageHash needs PIL Image
        img = Image.open(image_path)
        return imagehash.phash(img)
    except Exception as e:
        print(f"Error computing pHash for {image_path}: {e}")
        return None

def deduplicate_class(class_dir):
    """
    Removes duplicate images in a class directory based on pHash.
    """
    print(f"Deduplicating {class_dir}...")
    hashes = {}
    duplicates = []
    
    files = [f for f in os.listdir(class_dir) if f.lower().endswith(('.png', '.jpg', '.jpeg', '.bmp'))]
    
    for filename in files:
        file_path = os.path.join(class_dir, filename)
        h = compute_phash(file_path)
        
        if h is None:
            continue
            
        if h in hashes:
            # Found a duplicate
            duplicates.append(file_path)
        else:
            hashes[h] = file_path
            
    # Remove duplicates
    for dup in duplicates:
        print(f"Removing duplicate: {dup}")
        os.remove(dup)
        
    return len(hashes) # Return remaining count

def augment_image(image):
    """
    Generates an augmented version of the image.
    Applies random rotation, brightness/contrast, or blur.
    """
    rows, cols = image.shape[:2]
    
    # 1. Rotation (+- 15 degrees)
    angle = np.random.uniform(-15, 15)
    M = cv2.getRotationMatrix2D((cols/2, rows/2), angle, 1)
    aug_img = cv2.warpAffine(image, M, (cols, rows), borderMode=cv2.BORDER_REFLECT)
    
    # 2. Brightness/Contrast
    # alpha = contrast [0.8, 1.2], beta = brightness [-30, 30]
    alpha = np.random.uniform(0.8, 1.2)
    beta = np.random.uniform(-30, 30)
    aug_img = cv2.convertScaleAbs(aug_img, alpha=alpha, beta=beta)
    
    # 3. Gaussian Blur (slight) - 30% chance
    if np.random.rand() > 0.7:
        ksize = np.random.choice([3, 5])
        aug_img = cv2.GaussianBlur(aug_img, (ksize, ksize), 0)
        
    return aug_img

def augment_class(class_dir, target_count=100):
    """
    Augments images in a class directory to reach target_count.
    """
    files = [f for f in os.listdir(class_dir) if f.lower().endswith(('.png', '.jpg', '.jpeg', '.bmp'))]
    current_count = len(files)
    
    if current_count >= target_count:
        print(f"Class {os.path.basename(class_dir)} has {current_count} images. No augmentation needed.")
        return
        
    needed = target_count - current_count
    print(f"Augmenting {os.path.basename(class_dir)}: {current_count} -> {target_count} (Generating {needed} new images)")
    
    # Load all images to sample from
    images = []
    for f in files:
        path = os.path.join(class_dir, f)
        img = cv2.imread(path)
        if img is not None:
            images.append((f, img))
            
    if not images:
        print("No valid images to augment.")
        return

    generated = 0
    while generated < needed:
        # Pick a random image to augment
        base_filename, base_img = images[np.random.randint(len(images))]
        
        aug_img = augment_image(base_img)
        
        # Save
        new_filename = f"aug_{generated}_{base_filename}"
        cv2.imwrite(os.path.join(class_dir, new_filename), aug_img)
        generated += 1

def run_refinery(dataset_path):
    if not os.path.exists(dataset_path):
        print(f"Dataset path not found: {dataset_path}")
        return

    # Iterate over class directories
    for class_name in os.listdir(dataset_path):
        class_dir = os.path.join(dataset_path, class_name)
        if not os.path.isdir(class_dir):
            continue
            
        # 1. Deduplicate
        deduplicate_class(class_dir)
        
        # 2. Augment
        augment_class(class_dir, target_count=100)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="OmniVision Data Refinery")
    parser.add_argument("--dataset_path", type=str, required=True, help="Path to the dataset (e.g., data/raw/train/Car_Brand_Logos/Train)")
    
    args = parser.parse_args()
    
    run_refinery(args.dataset_path)
