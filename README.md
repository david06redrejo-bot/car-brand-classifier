---
title: NanoLogoPro
emoji: 🚗
colorFrom: blue
colorTo: indigo
sdk: docker
pinned: false
app_port: 8000
---

# 🚗 NanoLogoPro: AI Car Brand Classifier

A robust implementation of **Bag of Visual Words (BoVW)** using **SIFT (Scale-Invariant Feature Transform)** and **Support Vector Machines (SVM)** to classify car brand logos.

🔗 **Live Demo on Hugging Face:** [david06redrejo-bot/car-brand-classifier](https://huggingface.co/spaces/david06redrejo-bot/car-brand-classifier)

![Project Preview](static/preview_image.png)

## 🌟 Data Science & Vision Pipeline
This project avoids "black box" deep learning in favor of a transparent, understandable computer vision pipeline:

1.  **Feature Extraction (SIFT):**
    *   We use **SIFT** to detect keypoints and compute 128-dimensional invariant descriptors for every image. SIFT is chosen over ORB for its superior robustness to scale and rotation changes, which is critical for logo detection.
2.  **Vocabulary Construction (K-Means):**
    *   Sift descriptors from the training set are clustered using **K-Means (k=50)** to create a "Codebook" of visual words.
3.  **Quantization (BoVW):**
    *   Each image is converted into a histogram of visual word frequencies.
4.  **Classification (SVM):**
    *   A **Support Vector Machine (SVM)** is trained on these histograms to classify the brand.

## 📁 Project Structure Explained

Here is a detailed breakdown of the codebase:

*   **`app/`**: FastAPI Backend
    *   `main.py`: The entry point. Initializes the FastAPI app, loads the models (`lifespan`), and serves the API.
    *   `routes.py`: Defines the `/predict` endpoint that receives an image and returns the brand.
*   **`core/`**: Computer Vision Logic
    *   `vision_logic.py`: The "brain" of the operation. Contains `extract_sift_features`, `build_histogram`, and the full `predict_pipeline`.
    *   `image_utils.py`: Helpers for loading and processing images (grayscale conversion).
    *   `config.py`: Central configuration for paths (models, data) and constants (class labels).
*   **`train/`**: Training Scripts
    *   `train_model.py`: Automates the entire training process: loads data -> extracts SIFT features -> builds Codebook -> trains SVM -> saves models.
    *   `download_data.py`: Helper to download the dataset from Kaggle.
*   **`models/`**: Serialized Artifacts
    *   `vocabulary.pkl`: The trained K-Means model (Visual Vocabulary).
    *   `scaler.pkl`: StandardScaler to normalize histograms before SVM.
    *   `classifier.joblib`: The trained SVM model.
*   **`static/`**: Frontend
    *   `index.html`: The single-page application structure.
    *   `style.css`: Modern glassmorphism styling and animations.
    *   `script.js`: Handles image upload, drag-and-drop, and API communication.
*   **`Dockerfile`**: Instructions for Dockerizing the app for deployment (e.g., Hugging Face Spaces).
*   **`requirements.txt`**: Python dependencies.

## 🚀 How to Run Locally

### Prerequisites
*   Python 3.10+
*   Git

### Steps

1.  **Clone the Repository**
    ```bash
    git clone https://github.com/david06redrejo-bot/car-brand-classifier.git
    cd car-brand-classifier
    ```

2.  **Create a Virtual Environment (Recommended)**
    ```bash
    python -m venv venv
    # Windows
    venv\Scripts\activate
    # Mac/Linux
    source venv/bin/activate
    ```

3.  **Install Dependencies**
    Note: We use `opencv-python-headless` for server environments.
    ```bash
    pip install -r requirements.txt
    ```

4.  **Run the Server**
    ```bash
    uvicorn app.main:app --reload
    ```

5.  **Access the App**
    Open your browser and navigate to: [http://127.0.0.1:8000](http://127.0.0.1:8000)

## 🐳 Docker Deployment

You can also run it inside a Docker container:

```bash
docker build -t car-classifier .
docker run -p 8000:8000 car-classifier
```
