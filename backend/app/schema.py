from pydantic import BaseModel
from typing import List, Optional


class PredictRequest(BaseModel):
    text: str
    mode: str  # "translate-pl-en" lub "gec-en" (jeśli dodasz korektor)


class Highlight(BaseModel):
    start: int
    end: int
    suggestion: str


class PredictResponse(BaseModel):
    output: str
    highlights: Optional[List[Highlight]] = []
