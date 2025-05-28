from pathlib import Path
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM, pipeline
from peft import PeftModel
import torch


def load_translation_model(adapter_dir: str, base_model_name: str, device: str = None):
    device = device or ("cuda" if torch.cuda.is_available() else "cpu")
    base = AutoModelForSeq2SeqLM.from_pretrained(base_model_name)
    model = PeftModel.from_pretrained(base, adapter_dir)
    model.to(device).eval()
    tokenizer = AutoTokenizer.from_pretrained(base_model_name)
    return model, tokenizer, device


def translate(texts, model, tokenizer, device, max_length: int = 128):
    if isinstance(texts, str):
        texts = [texts]

    inputs = tokenizer(
        texts,
        return_tensors="pt",
        padding=True,
        truncation=True,
        max_length=max_length
    )
    inputs = {k: v.to(device) for k, v in inputs.items()}
    with torch.no_grad():
        outs = model.generate(**inputs)
    return tokenizer.batch_decode(outs, skip_special_tokens=True)


if __name__ == "__main__":
    base = "t5-small"
    project_root = Path(__file__).resolve().parents[2]
    adapter_dir = project_root / "checkpoints" / "mt_lora"

    model, tokenizer, device = load_translation_model(str(adapter_dir), base)
    examples = ["Hello, how are you?", "This is a test."]
    outputs = translate(examples, model, tokenizer, device)
    for src, tgt in zip(examples, outputs):
        print(f"> {src}\n< {tgt}\n")
