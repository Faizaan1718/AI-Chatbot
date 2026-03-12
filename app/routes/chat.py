from __future__ import annotations

import uuid
from typing import Any, Dict, List

from flask import Blueprint, jsonify, request
import torch

from app.dependencies import get_session_manager, get_faq_index, get_model_and_tokenizer


bp = Blueprint("chat", __name__)


def _ensure_session_id(payload: Dict[str, Any]) -> str:
    session_id = payload.get("session_id") or str(uuid.uuid4())
    return str(session_id)


def _build_prompt(history: List[dict], user_message: str, faq_context: str) -> str:
    system_intro = "You are an e-commerce support assistant. Be friendly, concise, and helpful.\n"
    faq_section = ""
    if faq_context:
        faq_section = "Here are some relevant help center snippets:\n" + faq_context + "\n\n"

    history_lines: List[str] = []
    for turn in history:
        prefix = "Customer" if turn["role"] == "user" else "Agent"
        history_lines.append(f"{prefix}: {turn['content']}")
    history_text = "\n".join(history_lines)

    prompt = system_intro + faq_section + history_text
    if history_text:
        prompt += "\n"
    prompt += f"Customer: {user_message}\nAgent:"
    return prompt


@bp.route("/chat", methods=["POST"])
def chat() -> Any:
    data = request.get_json(force=True) or {}
    message = data.get("message", "").strip()
    if not message:
        return jsonify({"error": "message is required"}), 400

    session_id = _ensure_session_id(data)
    session_manager = get_session_manager()
    faq_index = get_faq_index()
    model, tokenizer = get_model_and_tokenizer()

    context_turns = [
        {"role": t.role, "content": t.content} for t in session_manager.get_context(session_id)
    ]

    faq_results = faq_index.search(message, top_k=3)
    faq_context_lines: List[str] = []
    suggested_faqs: List[Dict[str, Any]] = []
    for item, score in faq_results:
        faq_context_lines.append(f"Q: {item.question}\nA: {item.answer}")
        suggested_faqs.append(
            {
                "id": item.id,
                "question": item.question,
                "answer": item.answer,
                "score": score,
            }
        )
    faq_context = "\n\n".join(faq_context_lines)

    prompt = _build_prompt(context_turns, message, faq_context)
    inputs = tokenizer(prompt, return_tensors="pt")

    with torch.no_grad():
        output_ids = model.generate(
            **inputs,
            max_new_tokens=128,
            pad_token_id=tokenizer.eos_token_id,
            do_sample=True,
            top_p=0.9,
            temperature=0.8,
        )

    generated = tokenizer.decode(output_ids[0], skip_special_tokens=True)
    # Extract only the assistant's latest part after the last "Agent:" marker
    agent_reply = generated.split("Agent:")[-1].strip()

    session_manager.append_turn(session_id, "user", message)
    session_manager.append_turn(session_id, "assistant", agent_reply)

    return jsonify(
        {
            "reply": agent_reply,
            "suggested_faqs": suggested_faqs,
            "session_id": session_id,
        }
    )


@bp.route("/reset_session", methods=["POST"])
def reset_session() -> Any:
    data = request.get_json(force=True) or {}
    session_id = data.get("session_id")
    if not session_id:
        return jsonify({"error": "session_id is required"}), 400
    session_manager = get_session_manager()
    session_manager.clear_session(session_id)
    return jsonify({"status": "ok", "session_id": session_id})


@bp.route("/health", methods=["GET"])
def health() -> Any:
    return jsonify({"status": "ok"})

