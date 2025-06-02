# app/routes.py
import asyncio
from concurrent.futures import ThreadPoolExecutor
from fastapi import APIRouter, HTTPException
from .schema import PredictRequest, PredictResponse, Highlight
from .models import (
    _cached_translate_pl_en,
    _cached_translate_en_pl,
    _cached_correct_gec,
)
from .utils import simple_highlight

router = APIRouter()
executor = ThreadPoolExecutor(max_workers=1)  # pojedynczy wątek inferencyjny


@router.post("/predict", response_model=PredictResponse)
async def predict(req: PredictRequest):
    text = req.text.strip()
    if not text:
        raise HTTPException(400, "Empty text")

    loop = asyncio.get_event_loop()

    if req.mode == "translate-pl-en":
        output = await loop.run_in_executor(executor, _cached_translate_pl_en, text)
        highlights = []

    elif req.mode == "translate-en-pl":
        output = await loop.run_in_executor(executor, _cached_translate_en_pl, text)
        highlights = []

    elif req.mode == "correct":
        corrected = await loop.run_in_executor(executor, _cached_correct_gec, text)
        highlights = simple_highlight(text, corrected)
        output = corrected

    else:
        raise HTTPException(400, f"Unsupported mode {req.mode}")

    return PredictResponse(output=output, highlights=highlights)
