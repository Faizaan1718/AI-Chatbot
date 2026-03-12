import json
from pathlib import Path


DATA_DIR = Path(__file__).resolve().parent
OUTPUT_PATH = DATA_DIR / "ecommerce_faqs.json"


def build_sample_faqs() -> list[dict]:
    faqs: list[dict] = [
        {
            "id": "shipping_time",
            "question": "How long does shipping take?",
            "answer": "Standard shipping usually takes 3-5 business days. Express options are available at checkout.",
            "category": "shipping",
            "tags": ["delivery", "time", "shipping"],
        },
        {
            "id": "order_tracking",
            "question": "How can I track my order?",
            "answer": "Once your order ships, we email you a tracking link. You can also track it from the 'My Orders' section after logging in.",
            "category": "orders",
            "tags": ["tracking", "orders"],
        },
        {
            "id": "return_policy",
            "question": "What is your return policy?",
            "answer": "You can return most items within 30 days of delivery for a full refund, provided they are unused and in original packaging.",
            "category": "returns",
            "tags": ["returns", "refund"],
        },
        {
            "id": "payment_methods",
            "question": "Which payment methods do you accept?",
            "answer": "We accept major credit and debit cards, as well as popular digital wallets. Available options are shown at checkout.",
            "category": "payments",
            "tags": ["payment", "cards"],
        },
        {
            "id": "change_order",
            "question": "Can I change or cancel my order?",
            "answer": "You can change or cancel your order within 30 minutes of placing it from the 'My Orders' page, as long as it has not been shipped.",
            "category": "orders",
            "tags": ["change", "cancel", "orders"],
        },
    ]
    return faqs


def main() -> None:
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    faqs = build_sample_faqs()
    with OUTPUT_PATH.open("w", encoding="utf-8") as f:
        json.dump(faqs, f, ensure_ascii=False, indent=2)
    print(f"Wrote {len(faqs)} FAQs to {OUTPUT_PATH}")


if __name__ == "__main__":
    main()

