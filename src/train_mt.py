import os
import logging
import types

import torch
from datasets import load_from_disk
from transformers import (
    MBartForConditionalGeneration,
    MBart50TokenizerFast,
    DataCollatorForSeq2Seq,
    Trainer,
    TrainingArguments,
    set_seed,
    TrainerCallback,
)
from evaluate import load as load_metric
from peft import LoraConfig, get_peft_model, TaskType

# Configuration
PROC_DIR = "../data/processed/tatoeba-en-pl-100k"
OUTPUT_DIR = "../models/mbart50-lora"
BEST_CKPT_DIR = os.path.join(OUTPUT_DIR, "best_bleu")
os.makedirs(OUTPUT_DIR, exist_ok=True)
os.makedirs(BEST_CKPT_DIR, exist_ok=True)

# Hyperparams
EPOCHS = 6
TRAIN_BSZ = 8
EVAL_BSZ = 8
ACCUM_STEPS = 4
LR = 2e-4
LOG_STEPS = 200
EVAL_STEPS = 1000
SAVE_STEPS = 1000


# Callbacks
class SimpleLogCallback(TrainerCallback):
    def on_train_begin(self, args, state, control, **kwargs):
        print(">>> ROZPOCZYNAM TRENOWANIE")

    def on_train_end(self, args, state, control, **kwargs):
        print(">>> TRENING ZAKOŃCZONY")


class SaveBestCallback(TrainerCallback):
    def __init__(self, tokenizer, ckpt_dir):
        self.best = float("-inf")
        self.tokenizer = tokenizer
        self.ckpt_dir = ckpt_dir

    def on_evaluate(self, args, state, control, metrics=None, **kwargs):
        bleu = metrics.get("bleu", 0.0)
        if bleu > self.best:
            self.best = bleu
            print(f">>> Nowy najlepszy BLEU: {bleu:.2f}, zapisuję do {self.ckpt_dir}")
            control.should_save = False
            args.model.save_pretrained(self.ckpt_dir)
            self.tokenizer.save_pretrained(self.ckpt_dir)


def wrap_forward(model):
    orig_forward = model.forward

    def forward_with_pop(self, *args, **kwargs):
        kwargs.pop("num_items_in_batch", None)
        return orig_forward(*args, **kwargs)

    model.forward = types.MethodType(forward_with_pop, model)


def main():
    logging.basicConfig(level=logging.INFO)
    set_seed(42)

    # 1) Dataset
    ds = load_from_disk(PROC_DIR)
    train_ds = ds["train"]
    val_ds = ds["validation"]

    # 2) Tokenizer
    tokenizer = MBart50TokenizerFast.from_pretrained(
        "facebook/mbart-large-50", src_lang="en_XX", tgt_lang="pl_PL"
    )

    # 3) Base model + wrap + LoRA
    device = torch.device("mps") if torch.backends.mps.is_available() else torch.device("cpu")
    base_model = MBartForConditionalGeneration.from_pretrained("facebook/mbart-large-50")
    wrap_forward(base_model)
    base_model.to(device)

    lora_cfg = LoraConfig(
        task_type=TaskType.SEQ_2_SEQ_LM,
        inference_mode=False,
        r=16, lora_alpha=32, lora_dropout=0.1,
        target_modules=["q_proj", "v_proj"],
    )
    model = get_peft_model(base_model, lora_cfg)

    # 4) Data collator
    data_collator = DataCollatorForSeq2Seq(
        tokenizer, model=model, label_pad_token_id=-100, pad_to_multiple_of=8
    )

    # 5) BLEU metric
    bleu_metric = load_metric("sacrebleu")

    def compute_metrics(eval_pred):
        preds, labs = eval_pred
        decoded = tokenizer.batch_decode(preds, skip_special_tokens=True)
        cleaned = [[l for l in lab if l != -100] for lab in labs]
        references = [[r] for r in tokenizer.batch_decode(cleaned, skip_special_tokens=True)]
        res = bleu_metric.compute(predictions=decoded, references=references)
        return {"bleu": res["score"]}

    # 6) TrainingArguments
    args = TrainingArguments(
        output_dir=OUTPUT_DIR,
        per_device_train_batch_size=TRAIN_BSZ,
        gradient_accumulation_steps=ACCUM_STEPS,
        per_device_eval_batch_size=EVAL_BSZ,
        learning_rate=LR,
        num_train_epochs=EPOCHS,
        logging_dir="runs/mbart50-lora",
        logging_steps=LOG_STEPS,
        do_train=True,
        do_eval=True,
        eval_steps=EVAL_STEPS,
        save_steps=SAVE_STEPS,
        save_total_limit=2,
        gradient_checkpointing=False,
        dataloader_num_workers=0 if device.type == "mps" else 4,
        fp16=(device.type != "mps"),
        remove_unused_columns=False,
    )

    # 7) Trainer
    trainer = Trainer(
        model=model,
        args=args,
        train_dataset=train_ds,
        eval_dataset=val_ds,
        data_collator=data_collator,
        tokenizer=tokenizer,
        compute_metrics=compute_metrics,
        callbacks=[SimpleLogCallback(), SaveBestCallback(tokenizer, BEST_CKPT_DIR)],
    )

    # 8) Train
    trainer.train()

    # 9) Save last
    last_dir = os.path.join(OUTPUT_DIR, "last")
    os.makedirs(last_dir, exist_ok=True)
    model.save_pretrained(last_dir)
    tokenizer.save_pretrained(last_dir)
    print(f">>> Ostatni model zapisany w: {last_dir}")
    print(f">>> Najlepszy BLEU zapisany w: {BEST_CKPT_DIR}")


if __name__ == "__main__":
    main()
