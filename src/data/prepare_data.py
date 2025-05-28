from pathlib import Path

import hydra
from datasets import load_dataset, DatasetDict
from omegaconf import DictConfig
from transformers import MarianTokenizer


@hydra.main(version_base="1.2", config_path="../../config", config_name="default")
def main(cfg: DictConfig):
    project_root = Path(__file__).resolve().parents[2]
    raw_file = project_root / cfg.data.processed / "mt_train.jsonl"
    out_dir = project_root / cfg.data.processed / "mt_tokenized"

    print(f"[PREPARE] ładowanie {raw_file}")

    ds = load_dataset("json", data_files=str(raw_file), split="train")

    ds = ds.train_test_split(test_size=0.1, seed=cfg.seed)
    dataset = DatasetDict({
        "train": ds["train"],
        "validation": ds["test"]
    })

    tokenizer = MarianTokenizer.from_pretrained(cfg.model.name_or_path)

    def tokenize_fn(batch):
        inputs = tokenizer(
            [f"translate English to Polish: {s}" for s in batch["src"]],
            text_target=batch["tgt"],
            truncation=True,
            padding="max_length",
            max_length=128
        )
        return inputs

    print("[PREPARE] tokenizuję dane…")
    tokenized = dataset.map(tokenize_fn, batched=True, remove_columns=["src", "tgt"])

    tokenized.save_to_disk(str(out_dir))
    print(f"[PREPARE] zapisane tokenizowane dane w {out_dir}")


if __name__ == "__main__":
    main()
