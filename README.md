---
title: OmniVision
emoji: 👁️
colorFrom: cyan
colorTo: purple
sdk: docker
pinned: true
app_port: 8000
---

# 👁️ OmniVision: Multi-Domain Visual Intelligence System

OmniVision is a scalable, **Self-Healing Computer Vision Architecture** that goes beyond simple classification. It is designed to autonomously adapt, learn from user feedback, and manage intelligence across multiple distinct domains (Automotive, Fashion, Sports, Tech, Food).

🔗 **Live Demo:** [david06redrejo-bot/car-brand-classifier](https://huggingface.co/spaces/david06redrejo-bot/car-brand-classifier)

![OmniVision Interface](static/preview_image.png)

## 🧠 The Architecture: SIFT + BoVW + Active Learning

This project rejects the "black box" Deep Learning paradigm in favor of a transparent, debuggable pipelien:

1.  **Modular Intelligence (The Brain):**
    *   A custom `ModelManager` lazy-loads domain-specific "brains" (SVM + Vocabulary) into memory only when needed (LRU Caching).
    *   Supported Domains: `Cars`, `Fashion`, `LaLiga`, `Tech`, `Food`.

2.  **Vision Pipeline (The Eyes):**
    *   **SIFT (Scale-Invariant Feature Transform):** Extracts robust localized keypoints (edges, corners, textures) invariant to scale and rotation.
    *   **Bag of Visual Words (BoVW):** Quantizes these features into a histogram using a K-Means Codebook (k=500).
    *   **SVM Classification:** A calibrated Linear SVM predicts the class probability.

3.  **Self-Healing Data Loop (The Nervous System):**
    *   **Active Learning:** User feedback (`/feedback`) is not just logged—it triggers the system.
    *   **Autonomy:** If a user flags a "New Class" (e.g., "Sega" in Tech):
        1.  The system detects data starvation.
        2.  Triggers a background **Scraper Agent** to fetch images via DuckDuckGo.
        3.  Sanitizes and augments the new data.
        4.  **Re-trains** the domain model in the background without downtime.

## 📁 Project Structure

*   **`app/`**: The Neural Core
    *   `main.py`: Application entry point & lifespan management.
    *   `routes.py`: API endpoints for Prediction and Feedback Loop.
    *   `services/`: Microservices for Scraper, ModelManager, and Training.
*   **`core/`**: Vision Logic
    *   `vision_logic.py`: SIFT extraction and Histogram generation.
    *   `config.py`: Centralized configuration and domain definitions.
*   **`data/`**: Neural Memory
    *   `raw/`: Source images organized by `{domain}/{class_label}`.
*   **`models/`**: Serialized Knowledge
    *   Contains `.pkl` artifacts for each domain (Codebook, Scaler, SVM).
*   **`static/`**: Omni-Interface
    *   Glassmorphism UI/UX with Cyber-Industrial aesthetics.
    *   `metrics/`: Real-time JSON feeds for the "Intelligence Hub" visualizations.

## 🚀 Deployment & Usage

### Prerequisites
*   Python 3.10+
*   Git

### Quick Start

1.  **Clone & Install**
    ```bash
    git clone https://github.com/david06redrejo-bot/car-brand-classifier.git
    cd car-brand-classifier
    pip install -r requirements.txt
    ```

2.  **Ignition**
    ```bash
    # Start the Uvicorn Server
    python -m uvicorn app.main:app --reload
    ```
    Access the Omni-Interface at `http://127.0.0.1:8000`.

3.  **Command Line Tools**
    *   **Seed a new domain:** `python scripts/data_seeder.py --domain tech`
    *   **Train a domian:** `python train/train_model.py` (Edit script for specific domain targeting)

## 🐳 Docker Support

```bash
docker build -t omnivision .
docker run -p 8000:8000 omnivision
```
