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
import contextlib
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
from sklearn.svm import SVC
from core.image_utils import load_image
from core.vision_logic import extract_orb_features, build_histogram, normalize_histogram
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
def run_training(dataset_paths, classes, num_clusters=200, save_model=True, domain="cars", file_lock=None):
    from core.config import get_model_paths, METRICS_DIR
    
    print(f"Loading dataset for domain: {domain}...")
    image_paths, labels = load_dataset(dataset_paths, classes)
    
    if not image_paths:
        print("No images found! Check your dataset paths.")
        return 0.0

    print(f"Found {len(image_paths)} images.")

    all_descriptors = []
    image_descriptors = []

    # Extract ORB features from all images
    print("Extracting ORB features...")
    for path in image_paths:
        try:
            image = load_image(path)
            descriptors = extract_orb_features(image)
            # ORB can return None if no features found
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
        return 0.0

    # Train KMeans codebook
    print(f"Training KMeans with {num_clusters} clusters...")
    stack_descriptors = np.vstack(all_descriptors)
    # Convert to float for KMeans (ORB is uint8)
    stack_descriptors = stack_descriptors.astype(np.float32)
    
    # Adjust K-Means clusters if we have too few descriptors

    n_samples = stack_descriptors.shape[0]
    if n_samples < num_clusters:
        print(f"Warning: Not enough descriptors ({n_samples}) for {num_clusters} clusters. Reducing clusters to {n_samples}.")
        num_clusters = n_samples
    
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
    # Split into Train and Test for Evaluation
    from sklearn.model_selection import train_test_split
    try:
        X_train, X_test, y_train, y_test = train_test_split(histograms, labels, test_size=0.2, random_state=42, stratify=labels)
    except Exception as e:
        print(f"Warning: Train/Test split failed ({e}). Using full dataset for training and testing.")
        X_train, X_test, y_train, y_test = histograms, histograms, labels, labels

    # Train Standard Scaler on Train set
    print("Training SVM...")
    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_test_scaled = scaler.transform(X_test)
    
    # Use LinearSVC with CalibratedClassifierCV for probability
    from sklearn.svm import LinearSVC
    from sklearn.calibration import CalibratedClassifierCV
    
    linear_svc = LinearSVC(dual="auto", random_state=42)
    # Ensure we have enough samples for CV
    min_train_samples = min(np.bincount(y_train)) if len(y_train) > 0 else 0
    
    if min_train_samples < 2:
        print("Warning: Not enough samples for calibration. Using raw LinearSVC.")
        svm = linear_svc
        svm.fit(X_train_scaled, y_train)
    else:
        # Dynamic CV folds: at most 3, but limited by min_train_samples
        n_cv = min(3, min_train_samples)
        # CV must be < n_samples, actually for StratifiedKFold (default in CV), n_splits <= n_samples
        # But if n_samples=2, cv=2 works (1 in each).
        
        try:
            svm = CalibratedClassifierCV(linear_svc, method='sigmoid', cv=n_cv)
            svm.fit(X_train_scaled, y_train)
        except Exception as e:
            print(f"Calibration failed ({e}), reverting to raw LinearSVC.")
            svm = linear_svc
            svm.fit(X_train_scaled, y_train)
    
    # Evaluation & Confusion Matrix
    print("Evaluating model...")
    from sklearn.metrics import accuracy_score, confusion_matrix
    import json
    
    y_pred = svm.predict(X_test_scaled)
    acc = accuracy_score(y_test, y_pred)
    print(f"Test Set Accuracy: {acc * 100:.2f}%")

    # Generate Confusion Matrix data for frontend
    cm = confusion_matrix(y_test, y_pred)
    cm_list = cm.tolist()
    
    cm_data = {
        "domain": domain,
        "classes": classes,
        "matrix": cm_list,
        "accuracy": acc
    }
    
    # Save Confusion Matrix JSON to metrics folder
    os.makedirs(METRICS_DIR, exist_ok = True)
    metrics_path = METRICS_DIR / f"{domain}_metrics.json"
    
    with open(metrics_path, 'w') as f:
        json.dump(cm_data, f)
    print(f"Metrics saved to {metrics_path}")

    # Retrain on FULL dataset for final production model
    if save_model:
        print("Retraining on full dataset for production...")
        X_full_scaled = scaler.fit_transform(histograms)
        
        # Re-instantiate to be safe (though fit typically resets)
        # Re-instantiate to be safe (though fit typically resets)
        linear_svc_full = LinearSVC(dual="auto", random_state=42)
        
        min_full_samples = min(np.bincount(labels)) if len(labels) > 0 else 0
        if min_full_samples < 2:
             print("Warning: Not enough samples for full calibration. Using raw LinearSVC.")
             svm_full = linear_svc_full
             svm_full.fit(X_full_scaled, labels)
        else:
             n_cv = min(3, min_full_samples)
             try:
                svm_full = CalibratedClassifierCV(linear_svc_full, method='sigmoid', cv=n_cv)
                svm_full.fit(X_full_scaled, labels)
             except:
                 svm_full = linear_svc_full
                 svm_full.fit(X_full_scaled, labels)

        # Save artifacts using dynamic paths
        print(f"Saving models for domain: {domain}...")
        
        paths = get_model_paths(domain)
        # Ensure directory exists (paths['kmeans'] is a file path)
        paths['kmeans'].parent.mkdir(parents=True, exist_ok=True)
        
        ctx = file_lock if file_lock else contextlib.nullcontext()
        with ctx:
            joblib.dump(kmeans, paths['kmeans'])
            joblib.dump(scaler, paths['scaler'])
            joblib.dump(svm_full, paths['svm'])
            joblib.dump(classes, paths['classes'])
        print("Training complete.")
    else:
        print("Skipping model save (tuning mode).")
        
    return acc

from core.config import MODELS_DIR, CODEBOOK_PATH, SCALER_PATH, SVM_PATH, CLASS_LABELS

# ... (rest of imports)

if __name__ == '__main__':
    import argparse
    try:
        from core.config import DATA_DIR
    except ImportError:
        DATA_DIR = None

    # Fallback if DATA_DIR is not defined in config
    if DATA_DIR is None:
        DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'data', 'raw')

    parser = argparse.ArgumentParser(description="Train model for a specific domain")
    parser.add_argument("--domain", type=str, default="cars", help="Domain to train (cars, fashion, laliga, etc.)")
    parser.add_argument("--clusters", type=int, default=200, help="Number of KMeans clusters")
    
    args = parser.parse_args()
    
    domain = args.domain
    num_clusters = args.clusters
    
    from core.config import DOMAINS, CLASS_LABELS
    
    if domain == "all":
        print("Training all domains...")
        for d, cls_list in DOMAINS.items():
            print(f"\n>>> Starting training for {d} <<<")
            train_paths = [os.path.join(DATA_DIR, d)]
            run_training(train_paths, cls_list, num_clusters=num_clusters, domain=d)
    else:
        if domain not in DOMAINS:
            print(f"Error: Domain '{domain}' not found in configuration.")
            sys.exit(1)
            
        classes = DOMAINS[domain]
        # Path is data/raw/{domain}
        train_paths = [os.path.join(DATA_DIR, domain)]
        
        print(f"Training domain: {domain}")
        print(f"Data path: {train_paths}")
        print(f"Classes: {classes}")
        
        run_training(train_paths, classes, num_clusters=num_clusters, domain=domain)

