"""
core/vision_logic.py

Responsibility:
    - Encapsulates the Bag of Visual Words (BoVW) algorithm logic.
    - `extract_sift_features(image)`: Detects and computes local descriptors (SIFT).
    - `build_histogram(descriptors, codebook)`: Maps local descriptors to visual words in the codebook and forms a frequency histogram.
    - `normalize_histogram(histogram)`: Normalizes a single histogram to make the descriptor independent of image size.
    - `predict_pipeline(image, kmeans, scaler, svm)`: Full pipeline for inference: Image -> Label.
"""

import cv2
import numpy as np

def extract_sift_features(image):
    """
    Extracts SIFT descriptors from a single grayscale image.
    Scale and rotation invariance are handled by SIFT's internal logic.
    """
    sift = cv2.SIFT_create()
    # image already comes as grayscale from utils.py
    # cv2.SIFT_create().detectAndCompute returns (keypoints, descriptors)
    # descriptors is (n_keypoints, 128) for SIFT
    keypoints, descriptors = sift.detectAndCompute(image, None)
    return descriptors

def build_histogram(descriptors, kmeans):
    """
    Quantizes local descriptors into a single global histogram using the loaded codebook.
    This corresponds to the vector quantization step in BoVW.
    """
    num_clusters = kmeans.n_clusters
    histogram = np.zeros(num_clusters, dtype=np.float32)
    
    if descriptors is not None and len(descriptors) > 0:
        # KMeans.predict expects float data for some implementations, but ORB is binary (uint8).
        # Standard sklearn KMeans expects float. We must convert descriptors.
        descriptors = descriptors.astype(np.float32)

        # Assign each descriptor to the closest visual word (centroid)
        predictions = kmeans.predict(descriptors)
        for pred in predictions:
            histogram[pred] += 1
            
    return histogram

def normalize_histogram(histogram):
    """
    Normalizes a single histogram to make the descriptor independent of image size.
    """
    norm = np.linalg.norm(histogram)
    if norm > 0:
        return histogram / norm
    return histogram

def predict_pipeline(image, kmeans, scaler, svm):
    """
    Full pipeline for inference: Image -> Label.
    Used by the FastAPI routes.
    """
    # 1. Extraction
    des = extract_sift_features(image)
    
    # 2. Quantization
    hist = build_histogram(des, kmeans)
    
    # 3. Normalization
    hist_norm = normalize_histogram(hist).reshape(1, -1)
    
    # 4. Scaling & SVM Inference
    hist_scaled = scaler.transform(hist_norm)
    
    # Predict using probability
    # classes_ is usually ordered lexicographically, but let's assume standard behavior
    probabilities = svm.predict_proba(hist_scaled)[0]
    prediction_idx = np.argmax(probabilities)
    confidence = probabilities[prediction_idx]
    
    # We return the index. The label mapping happens outside or we can do it here if we pass labels.
    # Currently it returns prediction[0] which is the index/label.
    # Let's keep returning the index but also the confidence.
    return prediction_idx, confidence
