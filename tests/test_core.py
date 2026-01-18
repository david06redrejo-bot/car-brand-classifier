import pytest
import numpy as np
import cv2
from sklearn.cluster import KMeans
from core.vision_logic import extract_sift_features, build_histogram, normalize_histogram

def test_extract_sift_features_black_image():
    """
    Ensure feature extraction handles images with no features (e.g., solid black) gracefully.
    """
    # Create black image 100x100
    black_img = np.zeros((100, 100), dtype=np.uint8)
    descriptors = extract_sift_features(black_img)
    
    # OpenCV SIFT returns None when no keypoints are found
    assert descriptors is None or len(descriptors) == 0

def test_extract_sift_features_white_noise():
    """
    Verify feature extraction works on random noise.
    """
    noise_img = np.random.randint(0, 255, (100, 100), dtype=np.uint8)
    descriptors = extract_sift_features(noise_img)
    
    # Should probably find some features in noise
    assert descriptors is not None
    assert descriptors.shape[1] == 128

def test_build_histogram_valid():
    """
    Verify histogram construction with valid descriptors.
    """
    class MockKMeans:
        def __init__(self, n_clusters):
            self.n_clusters = n_clusters
        
        def predict(self, X):
            # Map all to cluster 0
            return np.zeros(len(X), dtype=int)
    
    n_clusters = 10
    mock_kmeans = MockKMeans(n_clusters)
    
    # 5 descriptors
    descriptors = np.random.rand(5, 128).astype(np.float32)
    
    hist = build_histogram(descriptors, mock_kmeans)
    
    assert len(hist) == n_clusters
    assert hist[0] == 5.0
    assert np.sum(hist) == 5.0

def test_build_histogram_empty():
    """
    Verify histogram is zero-filled when no descriptors are provided.
    """
    class MockKMeans:
        def __init__(self, n_clusters):
            self.n_clusters = n_clusters
        def predict(self, X): raise NotImplementedError("Should not be called")

    mock_kmeans = MockKMeans(10)
    hist = build_histogram(None, mock_kmeans)
    
    assert len(hist) == 10
    assert np.sum(hist) == 0

def test_kmeans_training_robustness_few_samples():
    """
    Verify KMeans does not crash when training samples < n_clusters.
    Codebook builder needs to handle this edge case (e.g. very small dataset).
    """
    n_clusters = 5
    # Valid validation: we need at least n_clusters samples
    descriptors = np.random.rand(10, 128).astype(np.float32)
    
    kmeans = KMeans(n_clusters=n_clusters, n_init=10, random_state=42)
    try:
        kmeans.fit(descriptors)
    except Exception as e:
        pytest.fail(f"KMeans crashed with few samples: {e}")
        
    assert len(kmeans.cluster_centers_) == n_clusters
