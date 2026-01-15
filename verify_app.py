
import os
import sys
from fastapi.testclient import TestClient

# Add project root to sys.path
sys.path.append(os.path.abspath(os.path.dirname(__file__)))

from app.main import app


def test_prediction():
    # Use context manager to trigger lifespan startup (loading models)
    with TestClient(app) as client:
        # Path to a test image
        image_path = os.path.join("data", "raw", "train", "Car_Brand_Logos", "Train", "volkswagen", "a1.jpg")
        
        if not os.path.exists(image_path):
            print(f"Test image not found at {image_path}")
            return

        print(f"Testing with image: {image_path}")
        
        with open(image_path, "rb") as f:
            response = client.post("/predict", files={"file": ("test.jpg", f, "image/jpeg")})
            
        print("Status Code:", response.status_code)
        print("JSON Response:", response.json())


if __name__ == "__main__":
    test_prediction()
