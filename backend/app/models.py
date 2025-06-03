# app/models.py

import os
import torch
from torch import nn
from functools import lru_cache
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM
from peft import PeftModel

# Ustawiamy liczbę wątków CPU (dostosuj do liczby fizycznych rdzeni Twojego laptopa)
torch.set_num_threads(4)
torch.set_num_interop_threads(1)

print("[models.py] Rozpoczynam ładowanie modeli…")

BASE_DIR = os.path.dirname(__file__)
LORA_PLEN = os.path.abspath(os.path.join(BASE_DIR, "..", "helsinki_train20k_ep3_r8_len128", "lora_adapter"))
LORA_ENPL = os.path.abspath(os.path.join(BASE_DIR, "..", "gsarti_enpl_train100k_ep7_r8_len128", "lora_adapter"))
LORA_GEC = os.path.abspath(os.path.join(BASE_DIR, "..", "t5-large_jfleg+nucle+bea_ep7_r8", "lora_adapter"))

# ------------------ PL → EN ------------------
print("[models.py] 1/3 – Ładuję PL→EN tokenizer i bazowy model…")
MODEL_PLEN = "Helsinki-NLP/opus-mt-pl-en"
tokenizer_plen = AutoTokenizer.from_pretrained(MODEL_PLEN)
base_plen = AutoModelForSeq2SeqLM.from_pretrained(MODEL_PLEN)

print("[models.py] 2/3 – Ładuję PL→EN adapter LoRA…")
peft_plen = PeftModel.from_pretrained(base_plen, LORA_PLEN, local_files_only=True)

print("[models.py] 3/3 – Scalanie (merge) i kwantyzacja PL→EN…")
merged_plen = peft_plen.merge_and_unload()
quantized_plen = torch.quantization.quantize_dynamic(
    merged_plen,
    {nn.Linear},
    dtype=torch.qint8
)
print("[models.py] ✔ PL→EN gotowe.")

# ------------------ EN → PL ------------------
print("[models.py] 1/3 – Ładuję EN→PL tokenizer i bazowy model…")
MODEL_ENPL = "gsarti/opus-mt-tc-en-pl"
tokenizer_enpl = AutoTokenizer.from_pretrained(MODEL_ENPL)
base_enpl = AutoModelForSeq2SeqLM.from_pretrained(MODEL_ENPL)

print("[models.py] 2/3 – Ładuję EN→PL adapter LoRA…")
peft_enpl = PeftModel.from_pretrained(base_enpl, LORA_ENPL, local_files_only=True)

print("[models.py] 3/3 – Scalanie (merge) i kwantyzacja EN→PL…")
merged_enpl = peft_enpl.merge_and_unload()
quantized_enpl = torch.quantization.quantize_dynamic(
    merged_enpl,
    {nn.Linear},
    dtype=torch.qint8
)
print("[models.py] ✔ EN→PL gotowe.")

# ------------------ GEC (T5-base) – leniwe ładowanie ------------------
_gec_pipeline = None


def get_gec_pipeline():
    global _gec_pipeline
    if _gec_pipeline is None:
        print("[models.py] 1/2 – Pierwsze wywołanie GEC – ładuję tokenizer i bazowy model T5-base…")
        # Używamy publicznego, wytrenowanego modelu GEC na bazie t5-base
        GEC_MODEL_ID = "vennify/t5-base-grammar-correction"  # przykład

        tokenizer = AutoTokenizer.from_pretrained(GEC_MODEL_ID)
        base_model = AutoModelForSeq2SeqLM.from_pretrained(GEC_MODEL_ID)

        print("[models.py] 2/2 – Kwantyzacja modelu GEC (T5-base)…")
        # Kwantyzujemy dynamicznie do INT8, ale to i tak mniejsze od T5-large
        quantized_gec_model = torch.quantization.quantize_dynamic(
            base_model,
            {nn.Linear},
            dtype=torch.qint8
        )

        from transformers import pipeline
        _gec_pipeline = pipeline(
            "text2text-generation",
            model=quantized_gec_model,
            tokenizer=tokenizer,
            device=-1,  # CPU
            generation_kwargs={"max_length": 128, "num_beams": 1}
        )
        print("[models.py] ✔ GEC pipeline (T5-base) gotowe.")
    return _gec_pipeline


print("[models.py] Wszystkie eager‐loadowane modele (PL→EN i EN→PL) zostały załadowane.")
print("[models.py] GEC (T5-large) będzie ładowany leniwie przy pierwszym wywołaniu korekty.")

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


def correct_gec_manual(text: str) -> str:
    # Pobieramy pipeline GEC, tworząc go przy pierwszym wywołaniu
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
def _cached_translate_pl_en(text: str) -> str:
    return translate_pl_en_manual(text)


@lru_cache(maxsize=512)
def _cached_translate_en_pl(text: str) -> str:
    return translate_en_pl_manual(text)


@lru_cache(maxsize=512)
def _cached_correct_gec(text: str) -> str:
    return correct_gec_manual(text)
