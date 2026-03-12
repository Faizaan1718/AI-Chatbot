from __future__ import annotations

from functools import lru_cache
from pathlib import Path

from transformers import AutoTokenizer, AutoModelForCausalLM

from app.config import get_config
from memory.session_manager import SessionManager
from retrieval.faq_index import FAQIndex


@lru_cache(maxsize=1)
def get_session_manager() -> SessionManager:
    cfg = get_config()
    return SessionManager(max_turns=cfg.max_history_turns)


@lru_cache(maxsize=1)
def get_faq_index() -> FAQIndex:
    cfg = get_config()
    index = FAQIndex(embedding_model=cfg.embedding_model)
    try:
        index.load()
    except FileNotFoundError:
        index.load_faqs()
        index.build_index()
        index.save()
    return index


@lru_cache(maxsize=1)
def get_model_and_tokenizer():
    cfg = get_config()
    model_path = Path(cfg.model_path)
    if model_path.exists():
        tokenizer = AutoTokenizer.from_pretrained(str(model_path))
        model = AutoModelForCausalLM.from_pretrained(str(model_path))
    else:
        tokenizer = AutoTokenizer.from_pretrained(cfg.base_model_name)
        model = AutoModelForCausalLM.from_pretrained(cfg.base_model_name)
    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token
    return model, tokenizer

