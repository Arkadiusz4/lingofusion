from fastapi import APIRouter, HTTPException
from .schema import PredictRequest, PredictResponse
from .models import translator
from .utils import simple_highlight

router = APIRouter()


@router.post("/predict", response_model=PredictResponse)
def predict(req: PredictRequest):
    text = req.text.strip()
    if not text:
        raise HTTPException(status_code=400, detail="Empty text")

    # obsługujemy tylko tryb tłumaczenia PL→EN
    if req.mode == "translate-pl-en":
        out = translator(text)
        output = out[0]["translation_text"]
        highlights = []  # albo simple_highlight(text, output)
    else:
        raise HTTPException(status_code=400, detail=f"Unsupported mode {req.mode}")

    return PredictResponse(output=output, highlights=highlights)
