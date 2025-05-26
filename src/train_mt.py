import os
import logging

import torch
from datasets import load_from_disk
from transformers import (
    MBartForConditionalGeneration,
    MBart50TokenizerFast,
    Trainer,
    TrainingArguments,
    DataCollatorForSeq2Seq,
    set_seed,
    TrainerCallback,
)
from evaluate import load as load_metric
from peft import LoraConfig, get_peft_model, TaskType

# =============================================================================
#  CONFIG
# =============================================================================
PROC_DIR = "../data/processed/tatoeba-en-pl-10k"
OUTPUT_DIR = "../models/mt-lora"


# =============================================================================
#  CALLBACKS
# =============================================================================
class SimpleLogCallback(TrainerCallback):
    def on_train_begin(self, args, state, control, **kwargs):
        print(">>> STARTING TRAINING")

    def on_train_end(self, args, state, control, **kwargs):
        print(">>> TRAINING FINISHED")


class SaveBestCallback(TrainerCallback):
    """Only save a checkpoint when BLEU improves."""

    def __init__(self):
        self.best_bleu = float("-inf")

    def on_evaluate(self, args, state, control, metrics=None, **kwargs):
        bleu = metrics.get("bleu")
        if bleu is not None and bleu > self.best_bleu:
            self.best_bleu = bleu
            print(f">>> New best BLEU: {bleu:.2f} – saving checkpoint")
            control.should_save = True


# =============================================================================
#  METRIC: SACREBLEU
# =============================================================================
bleu_metric = load_metric("sacrebleu")


def compute_metrics(eval_pred):
    preds, labels = eval_pred
    decoded_preds = tokenizer.batch_decode(preds, skip_special_tokens=True)
    decoded_labels = tokenizer.batch_decode(
        [[l for l in label if l != -100] for label in labels],
        skip_special_tokens=True
    )
    results = bleu_metric.compute(predictions=decoded_preds,
                                  references=[[ref] for ref in decoded_labels])
    return {"bleu": results["score"]}


# =============================================================================
#  MAIN
# =============================================================================
def main():
    logging.basicConfig(level=logging.INFO)
    set_seed(42)

    # Load data
    ds = load_from_disk(PROC_DIR)
    train_ds, val_ds = ds["train"], ds["validation"]

    # Load model + tokenizer
    model = MBartForConditionalGeneration.from_pretrained("facebook/mbart-large-50")
    global tokenizer
    tokenizer = MBart50TokenizerFast.from_pretrained(
        "facebook/mbart-large-50",
        src_lang="en_XX", tgt_lang="pl_PL"
    )

    # Apply LoRA
    lora_config = LoraConfig(
        task_type=TaskType.SEQ_2_SEQ_LM,
        inference_mode=False,
        r=32,  # wyższy rank
        lora_alpha=64,
        lora_dropout=0.1,
        target_modules=["q_proj", "v_proj", "k_proj", "o_proj"],
    )
    model = get_peft_model(model, lora_config)

    # Data collator
    data_collator = DataCollatorForSeq2Seq(tokenizer, model=model)

    # Training arguments
    args = TrainingArguments(
        output_dir=OUTPUT_DIR,
        per_device_train_batch_size=32,
        per_device_eval_batch_size=16,
        learning_rate=3e-4,
        num_train_epochs=10,

        # logging
        logging_dir="runs/mt-lora",
        logging_steps=100,

        # run evaluation every 500 steps
        do_train=True,
        do_eval=True,
        eval_steps=500,

        # checkpoint every 500 steps
        save_steps=500,
        save_total_limit=2,

        # use FP16 if available
        fp16=torch.cuda.is_available(),
    )

    # Trainer
    trainer = Trainer(
        model=model,
        args=args,
        train_dataset=train_ds,
        eval_dataset=val_ds,
        data_collator=data_collator,
        tokenizer=tokenizer,
        compute_metrics=compute_metrics,
    )

    trainer.add_callback(SimpleLogCallback())
    trainer.add_callback(SaveBestCallback())

    # Start training
    trainer.train()

    # Final save of LoRA adapters and (last) model
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    model.save_pretrained(OUTPUT_DIR)
    print(f">>> PEFT-owany model zapisany w: {OUTPUT_DIR}")


if __name__ == "__main__":
    main()
