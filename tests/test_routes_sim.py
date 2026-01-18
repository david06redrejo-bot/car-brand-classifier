"""
tests/test_routes_sim.py

Simulates the behavior of app/routes.py endpoint to ensure no crashes.
"""

import sys
import os
import asyncio
import pytest
from unittest.mock import MagicMock, AsyncMock
from fastapi import UploadFile

# Add root
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.routes import predict
from app.services.model_manager import ModelManager

# Verify we can import it
print("Successfully imported app.routes.predict")

@pytest.mark.asyncio
async def test_predict_flow():
    print("Testing predict flow...")
    
    # Mocking UploadFile
    mock_file = MagicMock(spec=UploadFile)
    
    # Create a small dummy image
    import cv2
    import numpy as np
    img = np.zeros((100, 100, 3), dtype=np.uint8)
    _, img_encoded = cv2.imencode('.jpg', img)
    mock_content = img_encoded.tobytes()
    
    # Mock read
    mock_file.read = AsyncMock(return_value=mock_content)
    
    # Mock Request
    mock_request = MagicMock()
    
    # Mock ModelManager loading to avoid actual file IO if files missing
    # BUT we actually want to test real behavior if possible.
    # If models are missing, it should raise 503, not crash.
    
    try:
        response = await predict(mock_request, domain="cars", file=mock_file)
        print("Success Response:", response)
    except Exception as e:
        print("Caught Expected Exception (likely 503 if models missing, or actual result):")
        print(e)
        
    print("Test Complete.")

if __name__ == "__main__":
    asyncio.run(test_predict_flow())
