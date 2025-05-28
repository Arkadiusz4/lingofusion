import os
from datasets import load_dataset


def download_opus_books():
    ds = load_dataset("opus_books", "en-pl", split="train")
    os.makedirs("data/raw", exist_ok=True)
    out = "data/raw/opensubs.tsv"
    with open(out, "w", encoding="utf-8") as f:
        for ex in ds:
            src = ex["translation"]["en"]
            tgt = ex["translation"]["pl"]
            f.write(f"{src}\t{tgt}\n")
    print(f"[DOWNLOAD] zapisano {len(ds)} par do {out}")


if __name__ == "__main__":
    download_opus_books()
