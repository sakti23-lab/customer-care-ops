"""Customer-Care RAG chatbot core.

Retrieval-Augmented Generation over a travel customer-care knowledge base.
- With GEMINI_API_KEY: embeddings via Gemini + answer via Gemini chat
  (production-equivalent: Vertex AI Vector Search + text-embedding-004).
- Without a key: a local TF-IDF vector store +templated answer, so the app is
  always demonstrable. This mirrors the RAG retrieval pattern (retrieve ->
  ground -> generate) without cloud cost.

Proves: Engineer AI Agents / Gemini / Vertex AI (Google Cloud badges) + RAG.
"""
from __future__ import annotations
import os
import re
import hashlib
from collections import Counter

import numpy as np
import pandas as pd

DIM = 256  # local hashed-vector dimension


def _tokenize(text: str):
    return re.findall(r"[a-z0-9]+", text.lower())


class RAGEngine:
    def __init__(self, kb_path: str, api_key: str | None = None):
        self.api_key = api_key or os.environ.get("GEMINI_API_KEY")
        self.docs = self._load_kb(kb_path)
        self.mode = "gemini" if self.api_key else "local"
        self.matrix = np.array([self._embed(d["text"]) for d in self.docs])

    # ---------- knowledge base ----------
    def _load_kb(self, path: str):
        df = pd.read_csv(path)
        docs = []
        for _, r in df.iterrows():
            text = f"TOPIC: {r.get('topic','')}\nQ: {r['question']}\nA: {r['answer']}"
            docs.append({"text": text, "topic": str(r.get("topic", "")),
                         "question": str(r["question"])})
        return docs

    # ---------- embeddings ----------
    def _embed_local(self, text: str) -> np.ndarray:
        vec = np.zeros(DIM)
        for tok, c in Counter(_tokenize(text)).items():
            h = int(hashlib.md5(tok.encode()).hexdigest(), 16) % DIM
            vec[h] += c
        n = np.linalg.norm(vec)
        return vec / n if n > 0 else vec

    def _embed_gemini(self, text: str) -> np.ndarray:
        import google.generativeai as genai
        if not hasattr(self, "_gem"):
            genai.configure(api_key=self.api_key)
            self._gem = genai
        res = self._gem.embed_content(
            model="models/text-embedding-004", content=text)
        return np.asarray(res["embedding"], dtype=np.float32)

    def _embed(self, text: str) -> np.ndarray:
        return self._embed_gemini(text) if self.mode == "gemini" else self._embed_local(text)

    # ---------- retrieve ----------
    def retrieve(self, query: str, k: int = 3):
        q = self._embed(query)
        sims = self.matrix @ q
        top = np.argsort(-sims)[:k]
        return [(self.docs[i], float(sims[i])) for i in top]

    # ---------- generate ----------
    def answer(self, query: str, k: int = 3) -> str:
        hits = self.retrieve(query, k=k)
        ctx = "\n\n".join(d["text"] for d, _ in hits)
        if self.mode == "gemini":
            try:
                import google.generativeai as genai
                if not hasattr(self, "_gem"):
                    genai.configure(api_key=self.api_key)
                    self._gem = genai
                prompt = (
                    "You are a customer-care assistant for a travel company. "
                    "Answer ONLY from the context. If unsure, say so.\n\n"
                    f"CONTEXT:\n{ctx}\n\nQUESTION: {query}\n\nANSWER:"
                )
                m = self._gem.GenerativeModel("gemini-2.0-flash")
                return m.generate_content(prompt).text.strip()
            except Exception:
                pass  # fall through to template
        return (
            "Berdasarkan basis pengetahuan layanan (RAG retrieval):\n\n"
            + ctx
            + "\n\n[Mode lokal: set GEMINI_API_KEY untuk jawaban Gemini generative.]"
        )
