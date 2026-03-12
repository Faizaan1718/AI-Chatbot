from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import List, Dict, Any, Tuple

import faiss  # type: ignore
import numpy as np
from sentence_transformers import SentenceTransformer


ROOT_DIR = Path(__file__).resolve().parents[1]
FAQ_PATH = ROOT_DIR / "data" / "ecommerce_faqs.json"
INDEX_DIR = ROOT_DIR / "retrieval" / "index"


@dataclass
class FAQItem:
    id: str
    question: str
    answer: str
    category: str
    tags: List[str]


class FAQIndex:
    def __init__(self, embedding_model: str = "all-MiniLM-L6-v2") -> None:
        self.embedding_model_name = embedding_model
        self.model = SentenceTransformer(embedding_model)
        self.faqs: List[FAQItem] = []
        self.index: faiss.IndexFlatIP | None = None

    def load_faqs(self, path: Path = FAQ_PATH) -> None:
        with path.open("r", encoding="utf-8") as f:
            raw = json.load(f)
        self.faqs = [
            FAQItem(
                id=item["id"],
                question=item["question"],
                answer=item["answer"],
                category=item.get("category", ""),
                tags=item.get("tags", []),
            )
            for item in raw
        ]

    def build_index(self) -> None:
        if not self.faqs:
            self.load_faqs()
        questions = [f.question for f in self.faqs]
        embeddings = self.model.encode(questions, convert_to_numpy=True, show_progress_bar=False)
        embeddings = self._normalize(embeddings)
        dim = embeddings.shape[1]
        self.index = faiss.IndexFlatIP(dim)
        self.index.add(embeddings.astype(np.float32))

    @staticmethod
    def _normalize(x: np.ndarray) -> np.ndarray:
        norms = np.linalg.norm(x, axis=1, keepdims=True) + 1e-10
        return x / norms

    def save(self, directory: Path = INDEX_DIR) -> None:
        directory.mkdir(parents=True, exist_ok=True)
        if self.index is None:
            raise RuntimeError("Index not built.")
        faiss.write_index(self.index, str(directory / "faq.index"))
        meta = {
            "embedding_model": self.embedding_model_name,
            "faqs": [faq.__dict__ for faq in self.faqs],
        }
        with (directory / "meta.json").open("w", encoding="utf-8") as f:
            json.dump(meta, f, ensure_ascii=False, indent=2)

    def load(self, directory: Path = INDEX_DIR) -> None:
        meta_path = directory / "meta.json"
        index_path = directory / "faq.index"
        if not meta_path.exists() or not index_path.exists():
            raise FileNotFoundError("FAQ index files not found. Please build the index first.")
        with meta_path.open("r", encoding="utf-8") as f:
            meta = json.load(f)
        self.embedding_model_name = meta["embedding_model"]
        self.model = SentenceTransformer(self.embedding_model_name)
        self.faqs = [
            FAQItem(
                id=item["id"],
                question=item["question"],
                answer=item["answer"],
                category=item.get("category", ""),
                tags=item.get("tags", []),
            )
            for item in meta["faqs"]
        ]
        self.index = faiss.read_index(str(index_path))

    def search(self, query: str, top_k: int = 3) -> List[Tuple[FAQItem, float]]:
        if self.index is None:
            self.build_index()
        assert self.index is not None
        emb = self.model.encode([query], convert_to_numpy=True, show_progress_bar=False)
        emb = self._normalize(emb).astype(np.float32)
        scores, indices = self.index.search(emb, top_k)
        results: List[Tuple[FAQItem, float]] = []
        for idx, score in zip(indices[0], scores[0]):
            if idx < 0 or idx >= len(self.faqs):
                continue
            results.append((self.faqs[idx], float(score)))
        return results


def build_and_save_index() -> None:
    index = FAQIndex()
    index.load_faqs()
    index.build_index()
    index.save()
    print(f"Built FAQ index with {len(index.faqs)} items at {INDEX_DIR}")


if __name__ == "__main__":
    build_and_save_index()

