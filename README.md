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

A Computer Vision web application that identifies car brands from images using **Bag of Visual Words (BoVW)** and **Machine Learning (SVM)**.

![Project Preview](static/preview_image.png)
*(Note: Upload a screenshot of your app to the static folder and name it preview_image.png for it to show here!)*

## 🌟 Features
*   **Computer Vision Core:** Uses OpenCV (ORB descriptors) + K-Means Clustering to create a "Visual Vocabulary" of car logos.
*   **Machine Learning:** Support Vector Machine (SVM) classifier for accurate prediction.
*   **Modern Frontend:** Glassmorphism UI, animated speedometer loading, and drag-and-drop interaction.
*   **FastAPI Backend:** Lightweight and fast Python API serving the model.

## 🛠 Tech Stack
*   **Backend:** Python 3.11, FastAPI, Uvicorn
*   **Computer Vision:** OpenCV, Scikit-Learn, Numpy
*   **Frontend:** HTML5, CSS3 (Animations), Vanilla JS
*   **Deployment:** Docker ready

## 🚀 How to Run Locally

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/YOUR_USERNAME/car-brand-classifier.git
    cd car-brand-classifier
    ```

2.  **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

3.  **Run the application:**
    ```bash
    uvicorn app.main:app --reload
    ```
    Visit `http://127.0.0.1:8000` to use the app.

## 🐳 Docker Deployment
This project includes a production-ready `Dockerfile`.

```bash
docker build -t car-classifier .
docker run -p 8000:8000 car-classifier
```

## 📁 Project Structure
*   `app/`: FastAPI application logic & routes.
*   `core/`: Computer Vision logic (Feature extraction, BoVW).
*   `models/`: Serialized ML models (Codebook, SVM, Scaler).
*   `static/`: Frontend assets (HTML, CSS, JS).
*   `train/`: Scripts for training the model from scratch.
