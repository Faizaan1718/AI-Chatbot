import json
from pathlib import Path
from typing import List, Dict


DATA_DIR = Path(__file__).resolve().parent
OUTPUT_PATH = DATA_DIR / "synthetic_dialogs.jsonl"


def build_sample_dialogs() -> List[Dict]:
    dialogs: List[Dict] = []

    dialogs.append(
        {
            "dialog_id": "d1",
            "turns": [
                {"speaker": "user", "text": "Hi, how long will my order take to arrive?"},
                {
                    "speaker": "bot",
                    "text": "Standard shipping usually takes 3-5 business days after your order is processed.",
                },
                {"speaker": "user", "text": "Can I get it faster?"},
                {
                    "speaker": "bot",
                    "text": "Yes, we offer express shipping options at checkout if they are available in your area.",
                },
            ],
        }
    )

    dialogs.append(
        {
            "dialog_id": "d2",
            "turns": [
                {"speaker": "user", "text": "I want to return a product I bought last week."},
                {
                    "speaker": "bot",
                    "text": "You can return most items within 30 days as long as they are unused and in the original packaging.",
                },
                {"speaker": "user", "text": "Do I have to pay for return shipping?"},
                {
                    "speaker": "bot",
                    "text": "Return shipping is free on damaged or incorrect items. For other returns, fees depend on your location and reason for return.",
                },
            ],
        }
    )

    dialogs.append(
        {
            "dialog_id": "d3",
            "turns": [
                {"speaker": "user", "text": "Which payment methods do you support?"},
                {
                    "speaker": "bot",
                    "text": "We accept major credit and debit cards, as well as popular digital wallets. All available options show at checkout.",
                },
                {"speaker": "user", "text": "Is cash on delivery available?"},
                {
                    "speaker": "bot",
                    "text": "Cash on delivery is available in select regions. You will see the option during checkout if it is supported for your address.",
                },
            ],
        }
    )

    return dialogs


def main() -> None:
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    dialogs = build_sample_dialogs()
    with OUTPUT_PATH.open("w", encoding="utf-8") as f:
        for dialog in dialogs:
            f.write(json.dumps(dialog, ensure_ascii=False) + "\n")
    print(f"Wrote {len(dialogs)} dialogs to {OUTPUT_PATH}")


if __name__ == "__main__":
    main()

