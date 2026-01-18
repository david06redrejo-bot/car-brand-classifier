"""
train/train_model.py

Responsibility:
    - Orchestrates the full model training pipeline.
    1. Iterates through the training dataset directory structure.
    2. Uses `core.image_utils` to load images.
    3. Uses `core.vision_logic` to extract features from all training images.
    4. Trains the Codebook (K-Means) using aggregated features.
    5. Generates histograms for all training images.
    6. Trains the Standard Scaler and SVM Classifier using these histograms.
    7. Saves the trained artifacts (Codebook, Scaler, SVM) to the `models/` directory using `pickle` or `joblib`.
"""

import os
import sys

# Add project root to sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import numpy as np
import joblib
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
from sklearn.svm import SVC
from core.image_utils import load_image
from core.vision_logic import extract_sift_features, build_histogram, normalize_histogram
from core.config import MODELS_DIR, CODEBOOK_PATH, SCALER_PATH, SVM_PATH

# Function to load dataset
def load_dataset(paths, classes):
    image_paths = []
    labels = []
    for i, dataset_path in enumerate(paths):
        if not os.path.exists(dataset_path):
            print(f"Warning: Dataset path not found: {dataset_path}")
            continue

        for class_label in classes:
            class_dir = os.path.join(dataset_path, class_label)
            
            if not os.path.exists(class_dir):
                print(f"Warning: Class directory not found: {class_dir}")
                continue

            for img_file in os.listdir(class_dir):
                if img_file.lower().endswith(('.png', '.jpg', '.jpeg', '.bmp')):
                    image_paths.append(os.path.join(class_dir, img_file))
                    labels.append(classes.index(class_label))

    return image_paths, labels

# Function to run training
def run_training(dataset_paths, classes, num_clusters=500):
    print("Loading dataset...")
    image_paths, labels = load_dataset(dataset_paths, classes)
    
    if not image_paths:
        print("No images found! Check your dataset paths.")
        return

    print(f"Found {len(image_paths)} images.")

    all_descriptors = []
    image_descriptors = []

    # Extract SIFT features from all images
    print("Extracting SIFT features...")
    for path in image_paths:
        try:
            image = load_image(path)
            descriptors = extract_sift_features(image)
            # SIFT can return None if no features found
            if descriptors is None:
                descriptors = np.array([]) 
            
            # For KMeans training, we need a flat list of descriptors
            if len(descriptors) > 0:
                all_descriptors.append(descriptors)
            
            # For Histogram building, we keep them per image
            image_descriptors.append(descriptors)
        except Exception as e:
            print(f"Error processing {path}: {e}")
            image_descriptors.append(np.array([]))

    if not all_descriptors:
        print("No descriptors extracted. Cannot train.")
        return

    # Train KMeans codebook
    print(f"Training KMeans with {num_clusters} clusters...")
    stack_descriptors = np.vstack(all_descriptors)
    # Convert to float for KMeans
    stack_descriptors = stack_descriptors.astype(np.float32)
    
    kmeans = KMeans(n_clusters=num_clusters, random_state=42)
    kmeans.fit(stack_descriptors)

    # Generate histograms for all images
    print("Generating histograms...")
    all_histograms = []
    for descriptors in image_descriptors:
        if len(descriptors) > 0:
            descriptors = descriptors.astype(np.float32)
            histogram = build_histogram(descriptors, kmeans)
        else:
            histogram = np.zeros(num_clusters, dtype=np.float32)
            
        norm_histogram = normalize_histogram(histogram)
        all_histograms.append(norm_histogram)
    
    histograms = np.array(all_histograms)
    labels = np.array(labels)

    # Split into Train and Test for Evaluation
    from sklearn.model_selection import train_test_split
    X_train, X_test, y_train, y_test = train_test_split(histograms, labels, test_size=0.2, random_state=42, stratify=labels)

    # Train Standard Scaler on Train set
    print("Training SVM...")
    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_test_scaled = scaler.transform(X_test)
    
    # Enable probability and train SVM
    svm = SVC(kernel='linear', C=1.0, random_state=42, probability=True)
    svm.fit(X_train_scaled, y_train)
    
    # Evaluation & Confusion Matrix
    print("Evaluating model...")
    from sklearn.metrics import accuracy_score, confusion_matrix
    import matplotlib.pyplot as plt
    import seaborn as sns

    y_pred = svm.predict(X_test_scaled)
    acc = accuracy_score(y_test, y_pred)
    print(f"Test Set Accuracy: {acc * 100:.2f}%")

    # Generate Confusion Matrix
    cm = confusion_matrix(y_test, y_pred)
    plt.figure(figsize=(10, 8))
    sns.heatmap(cm, annot=True, fmt='d', cmap='Blues', xticklabels=classes, yticklabels=classes)
    plt.xlabel('Predicted')
    plt.ylabel('Actual')
    plt.title('Confusion Matrix')
    
    # Save Confusion Matrix to static folder
    # Assuming config.py is in 'core' and static is one level up from core or train
    import core.config
    static_dir = os.path.join(core.config.BASE_DIR, 'static')
    os.makedirs(static_dir, exist_ok = True)
    conf_matrix_path = os.path.join(static_dir, 'confusion_matrix.png')
    plt.savefig(conf_matrix_path)
    plt.close()
    print(f"Confusion matrix saved to {conf_matrix_path}")

    # Retrain on FULL dataset for final production model
    print("Retraining on full dataset for production...")
    X_full_scaled = scaler.fit_transform(histograms)
    svm.fit(X_full_scaled, labels)

    # Save artifacts
    print("Saving models...")
    os.makedirs(MODELS_DIR, exist_ok = True)
    joblib.dump(kmeans, CODEBOOK_PATH)
    joblib.dump(scaler, SCALER_PATH)
    joblib.dump(svm, SVM_PATH)
    print("Training complete.")

from core.config import MODELS_DIR, CODEBOOK_PATH, SCALER_PATH, SVM_PATH, CLASS_LABELS

# ... (rest of imports)

if __name__ == '__main__':
    classes = CLASS_LABELS
    # ...
    # Corrected paths based on download_data.py structure
    # NOTE: Check if folders are capitalized usually given Kaggle dataset
    # The ls showed 'Test/lexus', so likely 'Train/lexus' exists.
    # We will try the most probable paths.
    train_path = [
        'data/raw/train/Car_Brand_Logos/Train', 
        'data/raw/train/Car_Brand_Logos/Test'
    ]
    run_training(train_path, classes)
