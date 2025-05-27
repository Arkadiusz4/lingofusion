from datasets import load_dataset
import os


def main():
    dataset = load_dataset("opus100", "en-pl", split="train[:100000]")

    print("Przykład:", dataset[0])

    out_dir = os.path.join("../data", "raw", "tatoeba-en-pl-100k")
    dataset.save_to_disk(out_dir)
    print(f"Surowe dane zapisane w: {out_dir}")


if __name__ == "__main__":
    main()
