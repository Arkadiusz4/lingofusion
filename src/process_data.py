import os
from datasets import load_from_disk, DatasetDict
from transformers import MBart50TokenizerFast

RAW_DIR = "../data/raw/tatoeba-en-pl-100k"
PROC_DIR = "../data/processed/tatoeba-en-pl-100k"


def load_raw():
    return load_from_disk(RAW_DIR)


def split_dataset(ds):
    # 1) train/val/test 80/10/10
    ds_train_val = ds.train_test_split(test_size=0.2, seed=42)
    ds_val_test = ds_train_val["test"].train_test_split(test_size=0.5, seed=42)
    return DatasetDict({
        "train": ds_train_val["train"],
        "validation": ds_val_test["train"],
        "test": ds_val_test["test"],
    })


def tokenize_dataset(datasets: DatasetDict, tokenizer):
    def _tokenize(batch):
        inp = [t["en"] for t in batch["translation"]]
        tgt = [t["pl"] for t in batch["translation"]]
        model_inputs = tokenizer(
            inp,
            truncation=True,
            padding="max_length",
            max_length=128
        )
        labels = tokenizer(
            tgt,
            truncation=True,
            padding="max_length",
            max_length=128
        ).input_ids
        model_inputs["labels"] = labels
        return model_inputs

    return datasets.map(
        _tokenize,
        batched=True,
        remove_columns=datasets["train"].column_names,
        desc="Tokenizing texts",
    )


def main():
    raw = load_raw()
    splits = split_dataset(raw)

    tokenizer = MBart50TokenizerFast.from_pretrained(
        "facebook/mbart-large-50",
        src_lang="en_XX",
        tgt_lang="pl_PL"
    )

    tokenized = tokenize_dataset(splits, tokenizer)

    os.makedirs(PROC_DIR, exist_ok=True)
    tokenized.save_to_disk(PROC_DIR)
    print(f"Processing done. Tokenized data in: {PROC_DIR}")


if __name__ == "__main__":
    main()
