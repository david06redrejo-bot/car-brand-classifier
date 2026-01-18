"""
core/visualizer.py

Responsibility:
    - Visual Debugging: Generates images to explain model decisions.
    - Keypoint Rendering: Visualizes SIFT keypoints on an image.
    - Visual Word Montage: Visualizes what the "Visual Words" (clusters) represent.
"""

import cv2
import numpy as np
import os
import joblib
from core.vision_logic import extract_sift_features
from core.image_utils import load_image
from core.config import MODELS_DIR, CODEBOOK_PATH

def visualize_keypoints(image_path, save_path=None):
    """
    Draws SIFT keypoints on the image and saves/returns it.
    """
    image = cv2.imread(image_path) # Read as BGR for drawing
    if image is None:
        print(f"Error: Could not read {image_path}")
        return None
        
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    sift = cv2.SIFT_create()
    keypoints = sift.detect(gray, None)
    
    # Draw keypoints
    img_with_keypoints = cv2.drawKeypoints(image, keypoints, None, flags=cv2.DRAW_MATCHES_FLAGS_DRAW_RICH_KEYPOINTS)
    
    if save_path:
        cv2.imwrite(save_path, img_with_keypoints)
        print(f"Saved keypoint visualization to {save_path}")
        
    return img_with_keypoints

def generate_visual_word_montage(dataset_paths, save_path="static/vocab_montage.png", num_words=10, patch_size=20):
    """
    Generates a montage of the top `num_words` visual words (cluster centers).
    For each word, it finds the top 9 patches from the dataset that are closest to the center.
    """
    print("Generating Visual Word Montage...")
    
    # Load KMeans
    if not os.path.exists(CODEBOOK_PATH):
        print("Model not trained yet. Cannot generate montage.")
        return

    kmeans = joblib.load(CODEBOOK_PATH)
    centers = kmeans.cluster_centers_
    
    # We want to find patches for the first `num_words` clusters (or random ones)
    # Let's pick the most populated ones? Or just the first k.
    # KMeans labels are arbitrary, so 0..k-1.
    target_clusters = range(num_words)
    
    # Store patches: {cluster_idx: [(distance, patch), ...]}
    cluster_patches = {i: [] for i in target_clusters}
    
    # Collect patches from dataset
    # We need to traverse a subset of images to find good matches
    from train.train_model import load_dataset
    from core.config import CLASS_LABELS
    
    # Load a subset of images to save time
    image_paths, _ = load_dataset(dataset_paths, CLASS_LABELS)
    np.random.shuffle(image_paths)
    subset_paths = image_paths[:200]  # Check 200 images
    
    sift = cv2.SIFT_create()
    
    print(f"Scanning {len(subset_paths)} images for visual words...")
    
    for path in subset_paths:
        img = cv2.imread(path)
        if img is None: continue
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        
        kp, des = sift.detectAndCompute(gray, None)
        if des is None: continue
        
        # Predict clusters for these descriptors
        des = des.astype(np.float32)
        predictions = kmeans.predict(des)
        
        # Calculate distance to center
        # transform() returns distance to all centers, we pick the one for the prediction
        dists = kmeans.transform(des)
        
        for i, (pred, kpoint) in enumerate(zip(predictions, kp)):
            if pred in target_clusters:
                dist = dists[i][pred]
                
                # Extract patch
                x, y = int(kpoint.pt[0]), int(kpoint.pt[1])
                r = int(kpoint.size / 2)
                # Ensure meaningful patch size
                r = max(r, patch_size // 2)
                
                # Crop patch
                y1, y2 = max(0, y-r), min(gray.shape[0], y+r)
                x1, x2 = max(0, x-r), min(gray.shape[1], x+r)
                patch = img[y1:y2, x1:x2]
                
                if patch.size > 0:
                    patch = cv2.resize(patch, (patch_size, patch_size))
                    cluster_patches[pred].append((dist, patch))
                    
    # Sort and pick top 9 for each cluster
    montage_rows = []
    
    for cluster_id in target_clusters:
        patches = cluster_patches[cluster_id]
        patches.sort(key=lambda x: x[0]) # Sort by distance (ascending)
        top_patches = [p[1] for p in patches[:9]]
        
        # Pad if not enough
        while len(top_patches) < 9:
            top_patches.append(np.zeros((patch_size, patch_size, 3), dtype=np.uint8))
            
        # Create a 3x3 grid for this cluster
        row1 = np.hstack(top_patches[0:3])
        row2 = np.hstack(top_patches[3:6])
        row3 = np.hstack(top_patches[6:9])
        cluster_grid = np.vstack([row1, row2, row3])
        
        # Add a border or label?
        # Let's just stack them horizontally with others
        montage_rows.append(cluster_grid)
        
    # Stack all cluster grids horizontally
    if montage_rows:
        full_montage = np.hstack(montage_rows)
        cv2.imwrite(save_path, full_montage)
        print(f"Saved montage to {save_path}")
    else:
        print("Could not generate montage (no patches found).")

if __name__ == "__main__":
    # Test run
    # Assume we run from root
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--image", type=str, help="Image to visualize keypoints")
    parser.add_argument("--dataset", type=str, help="Dataset path for montage")
    args = parser.parse_args()
    
    if args.image:
        visualize_keypoints(args.image, "static/keypoints_debug.jpg")
        
    if args.dataset:
        generate_visual_word_montage([args.dataset], "static/vocab_montage.png")
