"""
app/main.py

Responsibility:
    - Entry point for the FastAPI application.
    - Initializes the `FastAPI` app instance.
    - Implements `lifespan` context manager to load models once on startup.
"""

from fastapi import FastAPI
from contextlib import asynccontextmanager
import joblib
import os
import sys

# Add the project root to sys.path to allow imports from core
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.routes import router
from core.config import CODEBOOK_PATH, SCALER_PATH, SVM_PATH

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Lifespan context manager to handle startup and shutdown events.
    Loads ML models into app.state to keep them in memory.
    """
    # Startup: Load models
    print("Loading models...")
    try:
        # Load artifacts using joblib (since they were saved with joblib/pickle)
        # Note: joblib.load works for both pickle and joblib files usually
        app.state.kmeans = joblib.load(CODEBOOK_PATH)
        app.state.scaler = joblib.load(SCALER_PATH)
        app.state.svm = joblib.load(SVM_PATH)
        print("Models loaded successfully.")
    except Exception as e:
        print(f"Error loading models: {e}")
        # In a real scenario, we might want to crash if models fail to load
        # For now, we'll log it.
        app.state.kmeans = None
        app.state.scaler = None
        app.state.svm = None
    
    yield
    
    # Shutdown: Clean up resources if necessary
    print("Shutting down...")
    app.state.kmeans = None
    app.state.scaler = None
    app.state.svm = None

from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse

# ... (existing imports)

app = FastAPI(
    title="BoVW Image Classifier",
    description="API for Image Classification using Bag of Visual Words",
    version="1.0.0",
    lifespan=lifespan
)

# Mount Static Files
app.mount("/static", StaticFiles(directory="static"), name="static")

# Include Router
app.include_router(router)

@app.get("/")
async def read_index():
    with open("static/index.html", "r", encoding="utf-8") as f:
        return HTMLResponse(content=f.read())


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
