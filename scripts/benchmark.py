"""
scripts/benchmark.py

Responsibility:
    - Measures latency of the pipeline components: SIFT, Quantization, SVM.
    - Ensures the system is real-time compatible.
"""

import time
import os
import sys
import numpy as np
import cv2
import joblib

# Add project root to sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.vision_logic import extract_sift_features, build_histogram, normalize_histogram
from core.image_utils import load_image
from core.config import MOD_DIR, CODEBOOK_PATH, SCALER_PATH, SVM_PATH, CLASS_LABELS
# Note: core.config might define MODELS_DIR instead of MOD_DIR, checking import below.
from core.config import MODELS_DIR

def run_benchmark(dataset_path, num_samples=50):
    print("Loading models...")
    try:
        kmeans = joblib.load(CODEBOOK_PATH)
        scaler = joblib.load(SCALER_PATH)
        svm = joblib.load(SVM_PATH)
    except FileNotFoundError:
        print("Models not found. Run training/tuning first.")
        return

    print(f"Benchmarking on {num_samples} random images from {dataset_path}...")
    
    # Collect sample images
    image_paths = []
    for root, dirs, files in os.walk(dataset_path):
        for file in files:
            if file.lower().endswith(('.png', '.jpg', '.jpeg')):
                image_paths.append(os.path.join(root, file))
                
    if not image_paths:
        print("No images found.")
        return
        
    np.random.shuffle(image_paths)
    samples = image_paths[:num_samples]
    
    sift_times = []
    quant_times = []
    svm_times = []
    
    for path in samples:
        img = load_image(path)
        
        # 1. SIFT Extraction
        start = time.perf_counter()
        descriptors = extract_sift_features(img)
        end = time.perf_counter()
        sift_duration = end - start
        sift_times.append(sift_duration)
        
        if descriptors is None or len(descriptors) == 0:
            continue
            
        # 2. Quantization
        # Convert for KMeans
        des_float = descriptors.astype(np.float32)
        start = time.perf_counter()
        hist = build_histogram(des_float, kmeans)
        end = time.perf_counter()
        quant_duration = end - start
        quant_times.append(quant_duration)
        
        # Normalization (fast, but part of loop)
        hist_norm = normalize_histogram(hist).reshape(1, -1)
        
        # 3. SVM Inference
        start = time.perf_counter()
        hist_scaled = scaler.transform(hist_norm)
        _ = svm.predict_proba(hist_scaled)
        end = time.perf_counter()
        svm_duration = end - start
        svm_times.append(svm_duration)

    avg_sift = np.mean(sift_times)
    avg_quant = np.mean(quant_times)
    avg_svm = np.mean(svm_times)
    
    print("\n--- Benchmark Results ---")
    print(f"Average SIFT Extraction Time: {avg_sift*1000:.2f} ms")
    print(f"Average Quantization Time:    {avg_quant*1000:.2f} ms")
    print(f"Average SVM Inference Time:   {avg_svm*1000:.2f} ms")
    print(f"Total Pipeline Latency:       {(avg_sift + avg_quant + avg_svm)*1000:.2f} ms")
    
    # Optimization Suggestion
    if avg_sift > 1.0:
        print("\n[WARNING] SIFT extraction is slow (> 1s).")
        print("Suggestion: Limit keypoints using cv2.SIFT_create(nfeatures=500)")
    else:
        print("\n[OK] Performance is within acceptable limits.")

if __name__ == "__main__":
    # Default path
    default_path = 'data/raw/train/Car_Brand_Logos/Train'
    run_benchmark(default_path)
