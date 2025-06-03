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
executor = ThreadPoolExecutor(max_workers=1)


@router.post("/predict", response_model=PredictResponse)
async def predict(req: PredictRequest):
    text = req.text.replace("\r", "")
    if not text:
        raise HTTPException(400, "Empty text")

    loop = asyncio.get_event_loop()

    # -------------------- Tłumaczenie PL→EN --------------------
    if req.mode == "translate-pl-en":
        lines_src = text.split("\n")
        translated_lines: list[str] = []

        for line in lines_src:
            if not line.strip():
                translated_lines.append("")
            else:
                translated_line = await loop.run_in_executor(
                    executor, _cached_translate_pl_en, line
                )
                translated_lines.append(translated_line)

        output = "\n".join(translated_lines)
        highlights: list[Highlight] = []

    # -------------------- Tłumaczenie EN→PL --------------------
    elif req.mode == "translate-en-pl":
        lines_src = text.split("\n")
        translated_lines: list[str] = []

        for line in lines_src:
            if not line.strip():
                translated_lines.append("")
            else:
                translated_line = await loop.run_in_executor(
                    executor, _cached_translate_en_pl, line
                )
                translated_lines.append(translated_line)

        output = "\n".join(translated_lines)
        highlights = []

    # -------------------- Korekcja (GEC) --------------------
    elif req.mode == "correct":
        lines_src = text.split("\n")
        corrected_lines: list[str] = []

        for line in lines_src:
            if not line.strip():
                corrected_lines.append("")
            else:
                corrected_line = await loop.run_in_executor(
                    executor, _cached_correct_gec, line
                )
                corrected_lines.append(corrected_line)

        output = "\n".join(corrected_lines)
        highlights = simple_highlight(text, output)

    else:
        raise HTTPException(400, f"Unsupported mode {req.mode}")

    return PredictResponse(output=output, highlights=highlights)
