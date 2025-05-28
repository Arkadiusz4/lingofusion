# src/training/train_mt.py
from pathlib import Path
import hydra
from omegaconf import DictConfig
from datasets import load_from_disk
from transformers import (
    MarianMTModel,
    MarianTokenizer,
    Seq2SeqTrainingArguments,
    Seq2SeqTrainer,
    DataCollatorForSeq2Seq
)
from peft import LoraConfig, get_peft_model, TaskType


@hydra.main(version_base="1.2", config_path="../../config", config_name="default")
def train_mt(cfg: DictConfig):
    project_root = Path(__file__).resolve().parents[2]

    # 1) dataset
    data_dir = project_root / cfg.data.processed / "mt_tokenized"
    ds = load_from_disk(str(data_dir))

    # 2) tokenizer + baza Marian
    tokenizer = MarianTokenizer.from_pretrained(cfg.model.name_or_path)
    model = MarianMTModel.from_pretrained(cfg.model.name_or_path)

    # 3) konfiguracja LoRA z cfg.lora
    tgt_mods = list(cfg.lora.target_modules)
    lora_cfg = LoraConfig(
        task_type=TaskType.SEQ_2_SEQ_LM,
        inference_mode=False,
        r=cfg.lora.r,
        lora_alpha=cfg.lora.lora_alpha,
        lora_dropout=cfg.lora.lora_dropout,
        target_modules=tgt_mods
    )
    model = get_peft_model(model, lora_cfg)

    # 4) unikalny katalog na tę konfigurację
    hp = cfg.lora
    ep = cfg.training.epochs
    name = f"r{hp.r}_a{hp.lora_alpha}_d{int(hp.lora_dropout * 100)}_e{ep}"
    output_dir = project_root / "checkpoints" / f"mt_lora_{name}"

    # 5) TrainingArguments
    training_args = Seq2SeqTrainingArguments(
        output_dir=str(output_dir),
        num_train_epochs=ep,
        per_device_train_batch_size=cfg.training.batch_size,
        per_device_eval_batch_size=cfg.training.batch_size,
        learning_rate=cfg.training.lr,
        predict_with_generate=True,
        save_strategy="epoch",
        logging_strategy="steps",
        logging_steps=100,
        save_total_limit=2,
        remove_unused_columns=False,
        fp16=False,
    )

    # 6) Data collator + Trainer
    data_collator = DataCollatorForSeq2Seq(tokenizer, model=model)
    trainer = Seq2SeqTrainer(
        model=model,
        args=training_args,
        train_dataset=ds["train"],
        eval_dataset=ds["validation"],
        data_collator=data_collator,
        tokenizer=tokenizer
    )

    # 7) Trenuj i zapis adaptera
    trainer.train()
    model.save_pretrained(output_dir)
    print(f"[TRAIN] LoRA adapters saved to {output_dir}")


if __name__ == "__main__":
    train_mt()
