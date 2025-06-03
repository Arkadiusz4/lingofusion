from fastapi import APIRouter, HTTPException
from typing import List

from app.schemas.predict import PredictRequest, PredictResponse, Highlight
from app.services.translation_service import (
    translate_lines_pl_en,
    translate_lines_en_pl,
)
from app.services.correction_service import correct_lines
from app.utils.highlight import simple_highlight

router = APIRouter()


@router.post("/predict", response_model=PredictResponse)
async def predict(req: PredictRequest):
    text = req.text.replace("\r", "")
    if not text:
        raise HTTPException(400, "Empty text")

    lines_src: List[str] = text.split("\n")

    if req.mode == "translate-pl-en":
        translated_lines = await translate_lines_pl_en(lines_src)
        output = "\n".join(translated_lines)
        highlights: List[Highlight] = []

    elif req.mode == "translate-en-pl":
        translated_lines = await translate_lines_en_pl(lines_src)
        output = "\n".join(translated_lines)
        highlights = []

    elif req.mode == "correct":
        corrected_lines = await correct_lines(lines_src)
        output = "\n".join(corrected_lines)
        highlights = simple_highlight(text, output)

    else:
        raise HTTPException(400, f"Unsupported mode {req.mode}")

    return PredictResponse(output=output, highlights=highlights)
