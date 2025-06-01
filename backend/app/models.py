import os
import torch
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM, pipeline
from peft import PeftModel

BASE_DIR = os.path.dirname(__file__)

LORA_DIR = os.path.abspath(
    os.path.join(BASE_DIR, "..", "helsinki_train20k_ep3_r8_len128", "lora_adapter")
)

MODEL_NAME = "Helsinki-NLP/opus-mt-pl-en"
tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
base_model = AutoModelForSeq2SeqLM.from_pretrained(MODEL_NAME)

model = PeftModel.from_pretrained(
    base_model,
    LORA_DIR,
    local_files_only=True
)

device = 0 if torch.cuda.is_available() else -1
translator = pipeline(
    "translation",
    model=model,
    tokenizer=tokenizer,
    device=device
)
