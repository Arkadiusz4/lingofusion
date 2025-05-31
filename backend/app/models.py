import os
import torch
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM, pipeline
from peft import PeftModel

# 1. BASE_DIR to /app/app (w kontenerze)
BASE_DIR = os.path.dirname(__file__)

# 2. W kontenerze adapter LoRA jest skopiowany do /app/mt-pl-en-lora/lora
LORA_DIR = os.path.abspath(
    os.path.join(BASE_DIR, "..", "mt-pl-en-lora", "lora")
)

# 3. Ładujemy tokenizer i bazowy model z Hugging Face Hub (cache)
MODEL_NAME = "Helsinki-NLP/opus-mt-pl-en"
tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
base_model = AutoModelForSeq2SeqLM.from_pretrained(MODEL_NAME)

# 4. Dokładamy adapter LoRA z lokalnego folderu
model = PeftModel.from_pretrained(
    base_model,
    LORA_DIR,
    local_files_only=True
)

# 5. Budujemy pipeline:
device = 0 if torch.cuda.is_available() else -1
translator = pipeline(
    "translation",
    model=model,
    tokenizer=tokenizer,
    device=device
)
