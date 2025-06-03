import os
from functools import lru_cache
import torch
from torch import nn
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM
from peft import PeftModel

from .base import *

CURRENT_DIR = os.path.dirname(__file__)
APP_ROOT = os.path.abspath(os.path.join(CURRENT_DIR, "..", ".."))

# --------------- PL → EN ---------------
LORA_PLEN = os.path.join(
    APP_ROOT,
    "helsinki_train20k_ep3_r8_len128",
    "lora_adapter"
)

MODEL_PLEN = "Helsinki-NLP/opus-mt-pl-en"
print("[translator.py] Ładuję PL→EN tokenizer i bazowy model…")
tokenizer_plen = AutoTokenizer.from_pretrained(MODEL_PLEN)
base_plen = AutoModelForSeq2SeqLM.from_pretrained(MODEL_PLEN)

print("[translator.py] Ładuję PL→EN adapter LoRA z:", LORA_PLEN)
peft_plen = PeftModel.from_pretrained(base_plen, LORA_PLEN, local_files_only=True)

print("[translator.py] Scalanie (merge) i kwantyzacja PL→EN…")
merged_plen = peft_plen.merge_and_unload()
quantized_plen = torch.quantization.quantize_dynamic(
    merged_plen,
    {nn.Linear},
    dtype=torch.qint8
)
print("[translator.py] ✔ PL→EN gotowe.")

# --------------- EN → PL ---------------
LORA_ENPL = os.path.join(
    APP_ROOT,
    "gsarti_enpl_train100k_ep7_r8_len128",
    "lora_adapter"
)

MODEL_ENPL = "gsarti/opus-mt-tc-en-pl"
print("[translator.py] Ładuję EN→PL tokenizer i bazowy model…")
tokenizer_enpl = AutoTokenizer.from_pretrained(MODEL_ENPL)
base_enpl = AutoModelForSeq2SeqLM.from_pretrained(MODEL_ENPL)

print("[translator.py] Ładuję EN→PL adapter LoRA z:", LORA_ENPL)
peft_enpl = PeftModel.from_pretrained(base_enpl, LORA_ENPL, local_files_only=True)

print("[translator.py] Scalanie (merge) i kwantyzacja EN→PL…")
merged_enpl = peft_enpl.merge_and_unload()
quantized_enpl = torch.quantization.quantize_dynamic(
    merged_enpl,
    {nn.Linear},
    dtype=torch.qint8
)
print("[translator.py] ✔ EN→PL gotowe.")

from torch import no_grad


def translate_pl_en_manual(text: str) -> str:
    inputs = tokenizer_plen(
        text,
        return_tensors="pt",
        truncation=True,
        max_length=256
    )
    with no_grad():
        out_ids = quantized_plen.generate(
            input_ids=inputs["input_ids"],
            attention_mask=inputs["attention_mask"],
            max_length=64,
            num_beams=1
        )
    return tokenizer_plen.decode(out_ids[0], skip_special_tokens=True)


def translate_en_pl_manual(text: str) -> str:
    inputs = tokenizer_enpl(
        text,
        return_tensors="pt",
        truncation=True,
        max_length=256
    )
    with no_grad():
        out_ids = quantized_enpl.generate(
            input_ids=inputs["input_ids"],
            attention_mask=inputs["attention_mask"],
            max_length=64,
            num_beams=1
        )
    return tokenizer_enpl.decode(out_ids[0], skip_special_tokens=True)


@lru_cache(maxsize=512)
def cached_translate_pl_en(text: str) -> str:
    return translate_pl_en_manual(text)


@lru_cache(maxsize=512)
def cached_translate_en_pl(text: str) -> str:
    return translate_en_pl_manual(text)
