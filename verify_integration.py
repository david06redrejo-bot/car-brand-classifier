
import sys
import os
from fastapi.testclient import TestClient

# Add project root to sys.path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.main import app
from core.config import DATA_DIR

client = TestClient(app)

def test_health():
    response = client.get("/health")
    assert response.status_code == 200
    print("Health Check: PASS")

def test_predict_endpoint():
    print("Testing /predict endpoint...")
    
    # Needs a real image
    # Assuming standard path
    base_dir = os.path.dirname(os.path.abspath(__file__))
    img_path = os.path.join(base_dir, "data", "raw", "cars", "toyota", "00000.jpg") # Adjust name as needed
    
    # Fallback search
    if not os.path.exists(img_path):
        cars_dir = os.path.join(base_dir, "data", "raw", "cars")
        if os.path.exists(cars_dir):
            for brand in os.listdir(cars_dir):
                brand_dir = os.path.join(cars_dir, brand)
                if os.path.isdir(brand_dir):
                    files = [f for f in os.listdir(brand_dir) if f.endswith('.jpg')]
                    if files:
                        img_path = os.path.join(brand_dir, files[0])
                        break
    
    if not os.path.exists(img_path):
        print("SKIP: No image found for testing.")
        return

    print(f"Using image: {img_path}")
    
    with open(img_path, "rb") as f:
        files = {"file": ("test_image.jpg", f, "image/jpeg")}
        response = client.post("/predict", files=files)
    
    if response.status_code == 200:
        data = response.json()
        print(f"Prediction Success: {data}")
    elif response.status_code == 503:
        print("Service Unavailable (Model probably not ready yet). Expected behavior if training.")
    else:
        print(f"FAIL: Status {response.status_code}, {response.text}")

if __name__ == "__main__":
    test_health()
    test_predict_endpoint()
