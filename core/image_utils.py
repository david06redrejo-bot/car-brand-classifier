"""
core/image_utils.py

Responsibility:
    - Handles low-level image operations.
    - `read_image_file(file_data)`: Decodes raw bytes into a Grayscale OpenCV image.
    - `load_image(path)`: Loads an image from disk (for training).
    - Handles resizing to ensure consistency.
"""

import cv2
import numpy as np
import os

def read_image_file(file_data: bytes, target_width: int = 640) -> np.ndarray:
    """
    Decodes raw image bytes into a grayscale OpenCV image and resizes it.
    
    Args:
        file_data (bytes): Raw image bytes from the API upload.
        target_width (int): Target width for resizing (maintains aspect ratio).
        
    Returns:
        np.ndarray: Preprocessed grayscale image.
    """
    # 1. Decode bytes to numpy array
    nparr = np.frombuffer(file_data, np.uint8)
    
    # 2. Decode image from array (Grayscale mode)
    img = cv2.imdecode(nparr, cv2.IMREAD_GRAYSCALE)
    
    if img is None:
        raise ValueError("Could not decode image bytes.")
        
    return resize_image(img, target_width)

def load_image(path: str, target_width: int = 640) -> np.ndarray:
    """
    Loads an image from disk as grayscale and resizes it.
    
    Args:
        path (str): File path to the image.
        target_width (int): Target width for resizing.
        
    Returns:
        np.ndarray: Preprocessed grayscale image.
    """
    if not os.path.exists(path):
        raise FileNotFoundError(f"Image not found: {path}")
        
    img = cv2.imread(path, cv2.IMREAD_GRAYSCALE)
    if img is None:
        raise ValueError(f"Failed to load image: {path}")
        
    return resize_image(img, target_width)

def resize_image(img: np.ndarray, target_width: int) -> np.ndarray:
    """
    Helper to resize specific image to width.
    """
    height, width = img.shape[:2]
    if width > target_width:
        scale_ratio = target_width / width
        new_height = int(height * scale_ratio)
        img = cv2.resize(img, (target_width, new_height), interpolation=cv2.INTER_AREA)
    return img
