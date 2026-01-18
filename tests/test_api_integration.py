import pytest
import io
import numpy as np
import cv2
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock
from app.main import app

client = TestClient(app)

def create_dummy_jpg(width=100, height=100):
    """Creates a valid JPEG image in memory."""
    img = np.zeros((height, width, 3), dtype=np.uint8)
    cv2.randn(img, 128, 50)
    _, buf = cv2.imencode('.jpg', img)
    return io.BytesIO(buf.tobytes())

@pytest.fixture
def mock_dependencies():
    with patch("app.services.model_manager.ModelManager") as MockManager, \
         patch("app.routes.predict_pipeline") as mock_pipeline:
        
        # Setup ModelManager to return "something" so we pass the "if not models" check
        instance = MockManager.return_value
        instance.load_domain.return_value = {
            'kmeans': MagicMock(),
            'scaler': MagicMock(),
            'svm': MagicMock()
        }
        
        # Setup pipeline to return index 0 (Hyundai) and high confidence
        mock_pipeline.return_value = (0, 0.95)
        
        yield

def test_predict_valid_jpg(mock_dependencies):
    """Test valid image prediction flow with mocked models."""
    img_buf = create_dummy_jpg()
    response = client.post(
        "/predict?domain=cars", 
        files={"file": ("test.jpg", img_buf, "image/jpeg")}
    )
    assert response.status_code == 200
    data = response.json()
    assert "label" in data
    # Index 0 in cars is hyundai
    assert data["label"].lower() == "hyundai"
    assert data["confidence"] == 0.95

def test_predict_invalid_file_content(mock_dependencies):
    """Test uploading a text file disguised as an image."""
    fake_img = io.BytesIO(b"This is just text, not an image.")
    response = client.post(
        "/predict", 
        files={"file": ("fake.jpg", fake_img, "image/jpeg")}
    )
    assert response.status_code == 400
    assert "Could not read file" in response.json()["detail"] or "Invalid image format" in response.json()["detail"]

def test_predict_large_4k_image(mock_dependencies):
    """Test uploading a large 4K resolution image."""
    img_buf = create_dummy_jpg(3840, 2160)
    response = client.post(
        "/predict?domain=cars", 
        files={"file": ("large_4k.jpg", img_buf, "image/jpeg")}
    )
    assert response.status_code == 200
    
def test_consecutive_requests(mock_dependencies):
    """Simulate stress/lazy loading by firing multiple requests."""
    img_buf = create_dummy_jpg()
    for i in range(5):
        img_buf.seek(0)
        response = client.post(
            "/predict?domain=cars", 
            files={"file": (f"test_{i}.jpg", img_buf, "image/jpeg")}
        )
        assert response.status_code == 200
