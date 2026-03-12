import json
from dataclasses import dataclass
from pathlib import Path
from typing import List, Dict

import torch
from torch.utils.data import Dataset
from transformers import (
    AutoTokenizer,
    AutoModelForCausalLM,
    Trainer,
    TrainingArguments,
)


ROOT_DIR = Path(__file__).resolve().parents[1]
DATA_PATH = ROOT_DIR / "data" / "synthetic_dialogs.jsonl"
MODEL_NAME = "microsoft/DialoGPT-small"
OUTPUT_DIR = ROOT_DIR / "models" / "checkpoints" / "ecommerce-support"


@dataclass
class DialogExample:
    history: str
    response: str


def load_dialogs(path: Path) -> List[DialogExample]:
    examples: List[DialogExample] = []
    with path.open("r", encoding="utf-8") as f:
        for line in f:
            record: Dict = json.loads(line)
            turns = record.get("turns", [])
            history_parts: List[str] = []
            for i in range(len(turns) - 1):
                speaker = turns[i]["speaker"]
                text = turns[i]["text"]
                prefix = "Customer" if speaker == "user" else "Agent"
                history_parts.append(f"{prefix}: {text}")
            if not turns:
                continue
            last_turn = turns[-1]
            if last_turn["speaker"] != "bot":
                continue
            response = last_turn["text"]
            history = "\n".join(history_parts)
            examples.append(DialogExample(history=history, response=response))
    return examples


class DialogDataset(Dataset):
    def __init__(self, tokenizer, examples: List[DialogExample], max_length: int = 256):
        self.tokenizer = tokenizer
        self.examples = examples
        self.max_length = max_length

    def __len__(self) -> int:
        return len(self.examples)

    def __getitem__(self, idx: int):
        ex = self.examples[idx]
        text = ex.history + "\nAgent: " + ex.response
        enc = self.tokenizer(
            text,
            truncation=True,
            max_length=self.max_length,
            padding="max_length",
            return_tensors="pt",
        )
        input_ids = enc["input_ids"].squeeze(0)
        attention_mask = enc["attention_mask"].squeeze(0)
        labels = input_ids.clone()
        return {
            "input_ids": input_ids,
            "attention_mask": attention_mask,
            "labels": labels,
        }


def main() -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    print(f"Loading dialogs from {DATA_PATH}")
    examples = load_dialogs(DATA_PATH)
    if not examples:
        raise RuntimeError("No dialog examples found for training.")

    tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token

    model = AutoModelForCausalLM.from_pretrained(MODEL_NAME)

    dataset = DialogDataset(tokenizer, examples)

    training_args = TrainingArguments(
        output_dir=str(OUTPUT_DIR),
        num_train_epochs=1,
        per_device_train_batch_size=2,
        learning_rate=5e-5,
        weight_decay=0.01,
        logging_steps=10,
        save_steps=50,
        save_total_limit=1,
        remove_unused_columns=False,
    )

    trainer = Trainer(
        model=model,
        args=training_args,
        train_dataset=dataset,
    )

    print("Starting training...")
    trainer.train()
    print("Saving model...")
    trainer.save_model(str(OUTPUT_DIR))
    tokenizer.save_pretrained(str(OUTPUT_DIR))
    print(f"Model saved to {OUTPUT_DIR}")


if __name__ == "__main__":
    main()

