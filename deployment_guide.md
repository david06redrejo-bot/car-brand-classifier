
# 🚀 Deployment Guide: BoVW Image Classifier
**Role:** Expert MLOps & Cloud Architect
**Objective:** Deploy FastAPI + OpenCV app to Production.

---

## 1. Repository Preparation

### A. Configure `.gitignore`
Stop raw training data from bloating your repo. Ensure `models/` is **tracked** (unless they exceed 100MB, but yours are small ~4MB).

**Run this command to create/update `.gitignore`:**
```bash
# Add these lines to .gitignore
__pycache__/
*.pyc
venv/
.env
.DS_Store
data/raw/    # DO NOT commit raw specific car images
```

### B. Git LFS (Large File Storage)
Your models are small (`vocabulary.pkl` is ~4.5MB), so standard Git works fine. However, for MLOps best practices (scalable to larger models):

**Initialize Git LFS:**
```bash
git lfs install
git lfs track "models/*.pkl"
git lfs track "models/*.joblib"
git add .gitattributes
```

---

## 2. Environment Containerization (Docker)
The `Dockerfile` has been created in your root directory. It is optimized for production.

**Key Features:**
- **Base:** `python:3.11-slim` (Small footprint).
- **Sys Deps:** Installs `libgl1` and `libglib2.0-0` (Critical for OpenCV).
- **Run Command:** Uses `sh -c` to handle dynamic `$PORT` assignment (vital for Railway/Render).

---

## 3. Deployment Strategy (Choose One)

### Option A: Hugging Face Spaces (Recommended for ML Demos)
*Best for: Free hosting, built-in ML community visibility, decent RAM (16GB on CPU tier).*

1.  **Create Space:**
    *   Go to [huggingface.co/spaces](https://huggingface.co/spaces) -> "Create new Space".
    *   **Name:** `car-brand-classifier`
    *   **SDK:** `Docker` (Select "Docker" as the SDK, not Streamlit/Gradio).
    *   **Hardware:** Public CPU (Free).

2.  **Push Code:**
    ```bash
    git remote add space https://huggingface.co/spaces/YOUR_USERNAME/car-brand-classifier
    git push space main
    ```

3.  **Result:** Your app will be live at `https://huggingface.co/spaces/YOUR_USERNAME/car-brand-classifier` (The embed URL will be provided by HF).

### Option B: Render / Railway (General Production)
*Best for: True REST API usage, scalability, custom domains.*

*   **RAM Limits:**
    *   **Render (Free):** 512MB RAM. **WARNING:** Your `KMeans` model (`vocabulary.pkl`) loaded into memory + FastAPI overhead might hit this limit. If the app crashes with "OOM" (Out of Memory), use Railway.
    *   **Railway (Trial/Hobby):** 512MB - 8GB RAM (Usage based). Much safer for ML apps.

**Deploy on Railway:**
1.  Install Railway CLI or connect GitHub repo on [railway.app](https://railway.app).
2.  Railway detects the `Dockerfile` automatically.
3.  It injects the `PORT` variable, which our Docker CMD handles.

---

## 4. Frontend Adjustments
**Status: DONE.**
I verified your `static/index.html`. It uses relative paths:
```javascript
const response = await fetch('/predict', { ... });
```
This is **production-ready**. It effectively means "send request to the same domain I'm currently on," whether that's `localhost:8000` or `my-app.railway.app`.

---

## 5. CI/CD (Automation)
To deploy automatically on every push:

**For Hugging Face:**
1.  Go to your HF Space -> Settings.
2.  **Github Actions integration:** Click "Connect to GitHub".
3.  Follow the flow to sync your GitHub repo with the Space. Now, every push to GitHub triggers a build on HF.

**For Railway/Render:**
1.  Connect your GitHub repository directly in their dashboard.
2.  Auto-deploy is enabled by default.

---

## 6. Verification
Once deployed, run the same verification script but change the URL:
```bash
# Verify remote API
python verify_app.py --url https://your-app-url.com
```
