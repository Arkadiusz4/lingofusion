from functools import lru_cache
import torch
from torch import nn
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM, pipeline

from .base import *

GEC_MODEL_ID = "vennify/t5-base-grammar-correction"

_gec_pipeline = None


def get_gec_pipeline():
    global _gec_pipeline
    if _gec_pipeline is None:
        print("[corrector.py] 1/2 – Ładuję tokenizer i model GEC…")
        tokenizer = AutoTokenizer.from_pretrained(GEC_MODEL_ID)
        base_model = AutoModelForSeq2SeqLM.from_pretrained(GEC_MODEL_ID)

        print("[corrector.py] 2/2 – Kwantyzacja GEC (T5-base)…")
        quantized_gec_model = torch.quantization.quantize_dynamic(
            base_model,
            {nn.Linear},
            dtype=torch.qint8
        )

        _gec_pipeline = pipeline(
            "text2text-generation",
            model=quantized_gec_model,
            tokenizer=tokenizer,
            device=-1,
            generation_kwargs={"max_length": 128, "num_beams": 1}
        )
        print("[corrector.py] ✔ GEC pipeline gotowe.")
    return _gec_pipeline


from torch import no_grad


def correct_gec_manual(text: str) -> str:
    gec = get_gec_pipeline()
    gec_input = "gec: " + text
    inputs = gec.tokenizer(
        gec_input,
        return_tensors="pt",
        truncation=True,
        max_length=256
    )
    with no_grad():
        out_ids = gec.model.generate(
            input_ids=inputs["input_ids"],
            attention_mask=inputs["attention_mask"],
            max_length=128,
            num_beams=1
        )
    return gec.tokenizer.decode(out_ids[0], skip_special_tokens=True)


@lru_cache(maxsize=512)
def cached_correct_gec(text: str) -> str:
    return correct_gec_manual(text)
