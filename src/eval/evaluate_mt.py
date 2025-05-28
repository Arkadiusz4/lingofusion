from datasets import load_from_disk
import evaluate
from transformers import MarianTokenizer, MarianMTModel
from peft import PeftModel
import torch
from pathlib import Path


def main():
    project_root = Path(__file__).resolve().parents[2]
    ds = load_from_disk(str(project_root / "data/processed/mt_tokenized"))
    test = ds["validation"]

    base = MarianMTModel.from_pretrained("gsarti/opus-mt-tc-en-pl")
    model = PeftModel.from_pretrained(base, project_root / "checkpoints/mt_lora")
    tok = MarianTokenizer.from_pretrained("gsarti/opus-mt-tc-en-pl")
    device = "cuda" if torch.cuda.is_available() else "cpu"
    model.to(device).eval()

    preds, refs = [], []
    for ex in test:
        src_txt = tok.decode(ex["input_ids"], skip_special_tokens=True)
        ref_txt = tok.decode(ex["labels"], skip_special_tokens=True)
        inputs = tok(src_txt, return_tensors="pt", padding=True).to(device)
        out = model.generate(**inputs)
        preds.append(tok.decode(out[0], skip_special_tokens=True))
        refs.append([ref_txt])

    metric = evaluate.load("sacrebleu")
    bleu = metric.compute(predictions=preds, references=refs)
    print(f"BLEU (200 przykładów): {bleu['score']:.2f}")


if __name__ == "__main__":
    main()
