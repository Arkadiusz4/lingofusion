#!/usr/bin/env python3
import os
import torch
from datasets import load_from_disk
from transformers import (
    MBartForConditionalGeneration,
    MBart50TokenizerFast,
    DataCollatorForSeq2Seq,
    Seq2SeqTrainer,
    Seq2SeqTrainingArguments,
)
from peft import PeftModel
from evaluate import load as load_metric

OUTPUT_DIR = "../models/mt-lora"
PROC_DIR = "../data/processed/tatoeba-en-pl-10k"


def main():
    # 1) Data
    ds = load_from_disk(PROC_DIR)
    test_ds = ds["test"]

    # 2) Tokenizer + base model
    tokenizer = MBart50TokenizerFast.from_pretrained(
        "facebook/mbart-large-50", src_lang="en_XX", tgt_lang="pl_PL"
    )
    base_model = MBartForConditionalGeneration.from_pretrained("facebook/mbart-large-50")

    # 3) Load your LoRA adapter into the base model
    model = PeftModel.from_pretrained(base_model, OUTPUT_DIR)
    # move to device
    device = torch.device("cuda" if torch.cuda.is_available() else
                          "mps" if torch.backends.mps.is_available() else
                          "cpu")
    model = model.to(device).eval()

    # 4) tell MBart which language to generate
    model.config.forced_bos_token_id = tokenizer.lang_code_to_id["pl_PL"]
    model.config.decoder_start_token_id = tokenizer.lang_code_to_id["pl_PL"]
    model.config.num_beams = 4  # optional: beam search

    # 5) Data collator
    data_collator = DataCollatorForSeq2Seq(tokenizer, model=model)

    # 6) Seq2SeqTrainingArguments
    args = Seq2SeqTrainingArguments(
        output_dir="./eval_mt",
        per_device_eval_batch_size=8,
        do_train=False,
        do_eval=True,
        predict_with_generate=True,
        generation_max_length=128,
    )

    # 7) BLEU
    bleu = load_metric("sacrebleu")

    def compute_metrics(eval_pred):
        preds, labels = eval_pred
        decoded_preds = tokenizer.batch_decode(preds, skip_special_tokens=True)
        decoded_labels = tokenizer.batch_decode(
            [[l for l in lab if l != -100] for lab in labels],
            skip_special_tokens=True
        )
        res = bleu.compute(
            predictions=decoded_preds,
            references=[[r] for r in decoded_labels]
        )
        return {"bleu": res["score"]}

    # 8) Seq2SeqTrainer
    trainer = Seq2SeqTrainer(
        model=model,
        args=args,
        eval_dataset=test_ds,
        data_collator=data_collator,
        tokenizer=tokenizer,
        compute_metrics=compute_metrics,
    )

    # 9) Run generation‐based evaluation
    pred = trainer.predict(test_ds)
    print("→ Test BLEU:", pred.metrics["test_bleu"])

    # 10) sanity‐check some examples
    samples = [
        "This is a test sentence.",
        "I love programming in Python.",
        "The quick brown fox jumps over the lazy dog."
    ]
    inputs = tokenizer(samples, return_tensors="pt", padding=True).to(device)
    outs = model.generate(**inputs, max_length=128)
    decoded = tokenizer.batch_decode(outs, skip_special_tokens=True)
    print("\nSAMPLES:")
    for src, tgt in zip(samples, decoded):
        print(f"EN: {src}\nPL: {tgt}\n")


if __name__ == "__main__":
    main()
