"""
app/schemas.py

Responsibility:
    - Defines Pydantic models for data validation and serialization.
    - `PredictionResponse`: Standardizes the JSON output structure.
"""

from pydantic import BaseModel
from typing import Union

class PredictionResponse(BaseModel):
    label: str
    confidence: Union[float, str] = "N/A" # SVM predict doesn't always give proba unless calibrated
