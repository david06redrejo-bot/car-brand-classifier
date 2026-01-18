"""
tests/test_refinery.py

Test script to verify the Data Refinery logic (Deduplication & Augmentation).
"""

import unittest
import os
import shutil
import cv2
import numpy as np
import sys
# Add project root to sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from scripts.refinery import deduplicate_class, augment_class, compute_phash

class TestDataRefinery(unittest.TestCase):
    def setUp(self):
        self.test_dir = "tests/temp_data"
        self.class_dir = os.path.join(self.test_dir, "class_A")
        
        if os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir)
            
        os.makedirs(self.class_dir)
        
        # Create a dummy image (black square)
        self.img = np.zeros((100, 100, 3), dtype=np.uint8)
        self.img_path = os.path.join(self.class_dir, "img1.png")
        cv2.imwrite(self.img_path, self.img)

    def tearDown(self):
        if os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir)

    def test_deduplication(self):
        # Create a duplicate
        dup_path = os.path.join(self.class_dir, "img1_dup.png")
        shutil.copy(self.img_path, dup_path)
        
        # Verify 2 files exist
        self.assertEqual(len(os.listdir(self.class_dir)), 2)
        
        # Run deduplication
        deduplicate_class(self.class_dir)
        
        # Verify 1 file remains
        self.assertEqual(len(os.listdir(self.class_dir)), 1)

    def test_augmentation(self):
        # Verify 1 file exists initially
        self.assertEqual(len(os.listdir(self.class_dir)), 1)
        
        # Run augmentation to target 5
        augment_class(self.class_dir, target_count=5)
        
        # Verify 5 files exist
        self.assertEqual(len(os.listdir(self.class_dir)), 5)
        
        # Check if files start with aug_
        files = os.listdir(self.class_dir)
        aug_files = [f for f in files if f.startswith("aug_")]
        self.assertEqual(len(aug_files), 4)

if __name__ == "__main__":
    unittest.main()
