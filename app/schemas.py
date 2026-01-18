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
    confidence: Union[float, str] = "N/A"

class FeedbackRequest(BaseModel):
    image_base64: str
    label: str
    is_correct: bool
    new_brand_name: Union[str, None] = None
