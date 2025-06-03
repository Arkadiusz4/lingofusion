from pydantic import BaseModel
from typing import List, Optional


class PredictRequest(BaseModel):
    text: str
    mode: str


class Highlight(BaseModel):
    start: int
    end: int
    suggestion: str


class PredictResponse(BaseModel):
    output: str
    highlights: Optional[List[Highlight]] = []
