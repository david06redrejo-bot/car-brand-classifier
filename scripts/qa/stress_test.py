import sys
import os
import cv2
import numpy as np
import joblib
import requests

# Add project root
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.append(PROJECT_ROOT)

from core.vision_logic import predict_pipeline
from core.image_utils import read_image_file
from core.config import CODEBOOK_PATH, SCALER_PATH, SVM_PATH, CLASS_LABELS

def add_noise(image):
    """Adds Salt and Pepper noise."""
    row, col = image.shape
    s_vs_p = 0.5
    amount = 0.05
    out = np.copy(image)
    
    # Salt mode
    num_salt = np.ceil(amount * image.size * s_vs_p)
    coords = [np.random.randint(0, i - 1, int(num_salt)) for i in image.shape]
    out[tuple(coords)] = 255

    # Pepper mode
    num_pepper = np.ceil(amount * image.size * (1. - s_vs_p))
    coords = [np.random.randint(0, i - 1, int(num_pepper)) for i in image.shape]
    out[tuple(coords)] = 0
    return out

def rotate_image(image, angle):
    """Rotates an image 90 degrees."""
    if angle == 90:
        return cv2.rotate(image, cv2.ROTATE_90_CLOCKWISE)
    elif angle == 180:
        return cv2.rotate(image, cv2.ROTATE_180)
    elif angle == 270:
        return cv2.rotate(image, cv2.ROTATE_90_COUNTERCLOCKWISE)
    return image

def run_stress_test():
    print("--- QA Adversarial Stress Test ---")
    
    # 1. Load Models
    if not os.path.exists(CODEBOOK_PATH):
        print("!!! Models not found. Please train the model first.")
        return

    print("Loading models...")
    kmeans = joblib.load(CODEBOOK_PATH)
    scaler = joblib.load(SCALER_PATH)
    svm = joblib.load(SVM_PATH)
    
    # 2. Get Golden Sample (BMW)
    img_url = "https://upload.wikimedia.org/wikipedia/commons/thumb/4/44/BMW.svg/2048px-BMW.svg.png"
    print("Downloading 'Golden Sample' (BMW)...")
    try:
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'}
        resp = requests.get(img_url, headers=headers, stream=True)
        resp.raise_for_status()
        img_array = np.asarray(bytearray(resp.content), dtype=np.uint8)
        # Decode and resize/grayscale using our core util
        # read_image_file expects bytes, but we can just use cv2.imdecode directly here
        # Actually core/image_utils.read_image_file calls standard cv2 logic logic.
        # Let's verify what read_image_file expects. It expects `file` object usually from FastAPI UploadFile.
        # We'll just replicate the loading:
        image = cv2.imdecode(img_array, cv2.IMREAD_GRAYSCALE)
        image = cv2.resize(image, (256, 256))
    except Exception as e:
        print(f"Failed to download sample: {e}")
        return

    # Check "background" class index if it exists in current model
    # Note: CLASS_LABELS in config might not match the trained model if we patched it.
    # We should trust the prediction index.
    # Let's assume BMW is in the list.
    target_label = "bmw" # lowercase in config
    if target_label not in CLASS_LABELS:
        print(f"Warning: {target_label} not in config CLASS_LABELS. Might be hard to map.")

    # 3. Baseline Prediction
    idx, conf = predict_pipeline(image, kmeans, scaler, svm)
    
    # We need to map index to label. The trained SVM might have different classes than config
    # if we used the patch.
    # But usually classes are sorted alphabetically.
    # Let's print the raw index and confidence for now.
    print(f"Baseline Prediction: Index {idx} | Conf: {conf:.2f}")

    # 4. Noise Test
    print("\n[Test 1] Noise Injection (Salt & Pepper)...")
    noisy_img = add_noise(image)
    idx_noise, conf_noise = predict_pipeline(noisy_img, kmeans, scaler, svm)
    print(f"Noisy Prediction: Index {idx_noise} | Conf: {conf_noise:.2f}")
    
    if idx == idx_noise:
        print(">>> PASSED: Prediction Stable")
    else:
        print("!!! FAILED: Prediction Flipped!")

    # 5. Rotation Test
    print("\n[Test 2] Rotation Invariance (90 deg)...")
    rot_img = rotate_image(image, 90)
    idx_rot, conf_rot = predict_pipeline(rot_img, kmeans, scaler, svm)
    print(f"Rotated Prediction: Index {idx_rot} | Conf: {conf_rot:.2f}")

    if idx == idx_rot:
        print(">>> PASSED: Prediction Stable")
    else:
        print("!!! FAILED: Prediction Flipped!")

if __name__ == "__main__":
    run_stress_test()
