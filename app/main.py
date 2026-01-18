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
# from core.config import CODEBOOK_PATH, SCALER_PATH, SVM_PATH # Obsolete

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Lifespan context manager.
    Model loading is now lazy-handled by ModelManager.
    """
    print("System startup...")
    yield
    print("Shutting down...")

from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse

# ... (existing imports)

app = FastAPI(
    title="BoVW Image Classifier",
    description="API for Image Classification using Bag of Visual Words",
    version="1.0.0",
    lifespan=lifespan
)

# Robust Path Resolution
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
STATIC_DIR = os.path.join(BASE_DIR, "static")

# Mount Static Files
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")

# Include Router
app.include_router(router)

@app.get("/")
async def read_index():
    index_path = os.path.join(STATIC_DIR, "index.html")
    with open(index_path, "r", encoding="utf-8") as f:
        return HTMLResponse(content=f.read())


if __name__ == "__main__":
    import uvicorn
    # Use reload=True only if debugging; implies specific directory structure
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
