import pytest
import io
import numpy as np
import cv2
from fastapi.testclient import TestClient
from app.main import app

# Create a TestClient
# Note: This requires the models to be loaded or mocked.
# The app's lifespan loads models. TestClient triggers lifespan events by default.
client = TestClient(app)

def create_dummy_jpg(width=100, height=100):
    """Creates a valid JPEG image in memory."""
    img = np.zeros((height, width, 3), dtype=np.uint8)
    # Add some random data so it's not just black
    cv2.randn(img, 128, 50)
    _, buf = cv2.imencode('.jpg', img)
    return io.BytesIO(buf.tobytes())

def test_predict_valid_jpg():
    """Test valid image prediction flow."""
    img_buf = create_dummy_jpg()
    response = client.post(
        "/predict", 
        files={"file": ("test.jpg", img_buf, "image/jpeg")}
    )
    # It might fail with 500 if models are not present locally (e.g. in this environment if not trained).
    # Ideally we should mock the prediction logic if models are missing, 
    # but for integration tests we often expect the env to be ready.
    # If it fails due to missing model, we can catch it or the test fails (which is correct behavior).
    assert response.status_code == 200
    data = response.json()
    assert "label" in data
    assert "confidence" in data

def test_predict_invalid_file_content():
    """Test uploading a text file disguised as an image."""
    fake_img = io.BytesIO(b"This is just text, not an image.")
    response = client.post(
        "/predict", 
        files={"file": ("fake.jpg", fake_img, "image/jpeg")}
    )
    # Expecting 400 Bad Request because CV2 failed to decode
    assert response.status_code == 400
    assert "Could not decode" in response.json()["detail"]

def test_predict_large_4k_image():
    """Test uploading a large 4K resolution image."""
    # 3840 x 2160
    img_buf = create_dummy_jpg(3840, 2160)
    response = client.post(
        "/predict", 
        files={"file": ("large_4k.jpg", img_buf, "image/jpeg")}
    )
    assert response.status_code == 200
    
def test_consecutive_requests():
    """Simulate stress/lazy loading by firing multiple requests."""
    img_buf = create_dummy_jpg()
    for i in range(5):
        img_buf.seek(0)
        response = client.post(
            "/predict", 
            files={"file": (f"test_{i}.jpg", img_buf, "image/jpeg")}
        )
        assert response.status_code == 200
