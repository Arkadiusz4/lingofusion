import itertools
import subprocess
from pathlib import Path

import pandas as pd
import torch
import evaluate
from datasets import load_from_disk
from transformers import MarianTokenizer, MarianMTModel
from peft import PeftModel

project_root = Path(__file__).resolve().parents[2]

grid = {
    "r": [8, 16, 32],
    "lora_alpha": [16, 32, 64],
    "lora_dropout": [0.0, 0.1, 0.2],
    "epochs": [5, 7, 10],
}


def train_adapter(params):
    script = project_root / "src" / "training" / "train_mt.py"
    overrides = [
        f"lora.r={params['r']}",
        f"lora.lora_alpha={params['lora_alpha']}",
        f"lora.lora_dropout={params['lora_dropout']}",
        f"training.epochs={params['epochs']}",
        "mode=translation"
    ]
    cmd = ["python", str(script), *overrides]
    subprocess.run(cmd, check=True, cwd=str(project_root))


def eval_bleu(params):
    name = f"r{params['r']}_a{params['lora_alpha']}_d{int(params['lora_dropout'] * 100)}_e{params['epochs']}"
    ckpt = project_root / "checkpoints" / f"mt_lora_{name}"

    ds = load_from_disk(str(project_root / "data/processed/mt_tokenized"))
    test = ds["validation"].select(range(200))

    base = MarianMTModel.from_pretrained("gsarti/opus-mt-tc-en-pl")
    model = PeftModel.from_pretrained(base, ckpt)
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
    return metric.compute(predictions=preds, references=refs)["score"]


def main():
    results = []

    for combo in itertools.product(*grid.values()):
        params = dict(zip(grid.keys(), combo))
        print(f"\n=== EXPERIMENT {params} ===")
        train_adapter(params)
        bleu = eval_bleu(params)
        print(f"→ BLEU: {bleu:.2f}")
        results.append({**params, "bleu": bleu})

    df = pd.DataFrame(results)
    df.to_csv("sweep_results_mt.csv", index=False)
    print("\n=== ALL RESULTS ===")
    print(df)

    import matplotlib.pyplot as plt
    plt.figure(figsize=(6, 4))
    for alpha in grid["lora_alpha"]:
        sub = df[df.lora_alpha == alpha]
        plt.plot(sub.r, sub.bleu, marker="o", label=f"α={alpha}")
    plt.xlabel("r")
    plt.ylabel("BLEU")
    plt.title("LoRA sweep: BLEU vs r by alpha")
    plt.legend()
    plt.tight_layout()
    plt.savefig("sweep_bleu_vs_r.png")
    print("Saved plot → sweep_bleu_vs_r.png")


if __name__ == "__main__":
    main()
