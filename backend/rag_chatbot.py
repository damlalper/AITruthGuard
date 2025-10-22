from __future__ import annotations

from typing import Dict, List, Tuple

import numpy as np
from numpy.linalg import norm
import google.generativeai as genai
import csv

from .config import load_config
from .embedder import SentenceEmbedder
from .index_manager import FaissIndexManager
from .news_api import NewsApiConfig, fetch_recent_news


def _cosine_similarity(vec_a: np.ndarray, vec_b: np.ndarray) -> float:
    denom = (norm(vec_a) * norm(vec_b))
    if denom == 0:
        return 0.0
    return float(np.dot(vec_a, vec_b) / denom)


class RAGChatbot:
    def __init__(self) -> None:
        self.cfg = load_config()
        self.embedder = SentenceEmbedder(self.cfg.model_name)
        self.index = FaissIndexManager.load(self.cfg.output_faiss_path, self.cfg.output_metadata_json_path)
        # Load persisted payload so searches return metadata across restarts
        try:
            payload: List[Dict] = []
            with open(self.cfg.output_data_csv_path, "r", encoding="utf-8") as f:
                reader = csv.DictReader(f)
                for row in reader:
                    payload.append({
                        "id": row.get("id", ""),
                        "title": row.get("title", ""),
                        "text": row.get("text", ""),
                        "label": row.get("label", ""),
                        "source": row.get("source", ""),
                        "url": row.get("url", ""),
                    })
            self.index.payload = payload
        except Exception:
            # If CSV missing/corrupt, continue with empty payload
            self.index.payload = self.index.payload or []

        # Gemini setup (optional but recommended)
        if self.cfg.gemini_api_key:
            try:
                genai.configure(api_key=self.cfg.gemini_api_key)
                self.gemini_model = None
                try:
                    # Try to pick a model that supports generateContent
                    models = list(genai.list_models())
                    def _clean_name(mname: str) -> str:
                        return mname.split("/")[-1] if "/" in mname else mname
                    for m in models:
                        name = getattr(m, "name", "")
                        methods = set(getattr(m, "supported_generation_methods", []) or [])
                        if name and name.startswith("models/gemini") and ("generateContent" in methods or "generate_text" in methods):
                            self.gemini_model = genai.GenerativeModel(_clean_name(name))
                            break
                except Exception:
                    self.gemini_model = None

                # Final fallbacks if listing failed or nothing matched
                if self.gemini_model is None:
                    for name in ["gemini-pro", "gemini-1.0-pro"]:
                        try:
                            self.gemini_model = genai.GenerativeModel(name)
                            break
                        except Exception:
                            self.gemini_model = None
            except Exception:
                self.gemini_model = None
        else:
            self.gemini_model = None

    def retrieve_from_index(self, query: str, k: int = 5) -> List[Dict]:
        qvec = self.embedder.encode([query], batch_size=1, normalize=True)
        distances, results = self.index.search(qvec, k=k)
        return results[0] if results else []

    def fetch_recent_news(self, query: str, max_items: int = 10) -> List[Dict]:
        news_cfg = NewsApiConfig(
            api_key=self.cfg.news_api_key or "",
            language=self.cfg.news_language,
            days_back=self.cfg.news_days_back,
            query=query,
        )
        records = fetch_recent_news(news_cfg)
        return [r.__dict__ for r in records][:max_items]

    def similarity_score(self, query: str, docs: List[Dict]) -> List[Tuple[Dict, float]]:
        if not docs:
            return []
        doc_texts = [f"{d.get('title','')}. {d.get('text','')}".strip() for d in docs]
        doc_vecs = self.embedder.encode(doc_texts, batch_size=self.cfg.batch_size, normalize=True)
        qvec = self.embedder.encode([query], batch_size=1, normalize=True)[0]
        scores: List[Tuple[Dict, float]] = []
        for d, v in zip(docs, doc_vecs):
            scores.append((d, _cosine_similarity(qvec, v)))
        scores.sort(key=lambda x: x[1], reverse=True)
        return scores

    def generate_answer(self, query: str, index_docs: List[Dict], news_docs: List[Dict]) -> str:
        # Prepare context text
        def fmt(d: Dict) -> str:
            title = d.get("title", "").strip()
            url = d.get("url", "").strip()
            source = d.get("source", "").strip()
            preview = (d.get("text", "") or "").strip()[:500]
            return f"- Title: {title}\n  Source: {source}\n  URL: {url}\n  Excerpt: {preview}"

        context_sections: List[str] = []
        if index_docs:
            context_sections.append("En Yakın Eşleşmeler (Dataset):\n" + "\n".join(fmt(d) for d in index_docs[:5]))
        if news_docs:
            context_sections.append("Güncel Haberler (NewsAPI):\n" + "\n".join(fmt(d) for d in news_docs[:5]))
        context_text = "\n\n".join(context_sections) if context_sections else "(No context)"

        user_prompt = (
            "Aşağıdaki bağlamı kullanarak soruyu yanıtla. Kaynakları ve kısa özet ver."
            " Yanıt Türkçe ve kısa olsun.\n\n"
            f"Soru/Haber: {query}\n\nBağlam:\n{context_text}\n\n"
            "İstenen çıktı formatı: 'Bu haber şu şekilde görünüyor... %DOĞRULUK ... kaynaklar: <linkler>'"
        )

        if not self.gemini_model:
            # Fallback: concise deterministic summary without LLM
            lines: List[str] = [
                "LLM yapılandırılmadı (GEMINI_API_KEY yok).",
                "Aşağıda bağlam özetleri ve kaynaklar listelenmiştir:\n",
            ]
            if index_docs:
                lines.append("Dataset Benzerleri:")
                for d in index_docs[:3]:
                    title = d.get("title") or "(başlık yok)"
                    url = d.get("url") or ""
                    source = d.get("source") or ""
                    lines.append(f"- {title} [{source}] {url}")
            if news_docs:
                lines.append("Güncel Haberler:")
                for d in news_docs[:3]:
                    title = d.get("title") or "(başlık yok)"
                    url = d.get("url") or ""
                    source = d.get("source") or ""
                    lines.append(f"- {title} [{source}] {url}")
            lines.append("Öneri: Daha açıklayıcı yanıt için GEMINI_API_KEY ekleyin.")
            return "\n".join(lines)

        try:
            resp = self.gemini_model.generate_content(user_prompt)
            return resp.text.strip() if hasattr(resp, "text") and resp.text else ""
        except Exception as e:
            # Robust fallback: never raise to API; return deterministic summary
            lines: List[str] = [
                f"LLM hatası: {str(e)}",
                "Aşağıda bağlam özetleri ve kaynaklar listelenmiştir:\n",
            ]
            if index_docs:
                lines.append("Dataset Benzerleri:")
                for d in index_docs[:3]:
                    title = d.get("title") or "(başlık yok)"
                    url = d.get("url") or ""
                    source = d.get("source") or ""
                    lines.append(f"- {title} [{source}] {url}")
            if news_docs:
                lines.append("Güncel Haberler:")
                for d in news_docs[:3]:
                    title = d.get("title") or "(başlık yok)"
                    url = d.get("url") or ""
                    source = d.get("source") or ""
                    lines.append(f"- {title} [{source}] {url}")
            return "\n".join(lines)

    def ask(self, input_text: str, k: int = 5) -> Dict:
        # 1) Retrieve from FAISS
        index_docs = self.retrieve_from_index(input_text, k=k)

        # 2) Fetch recent news for the query
        news_docs = self.fetch_recent_news(input_text, max_items=10)

        # 3) Compute similarity scores
        scored_news = self.similarity_score(input_text, news_docs)
        scored_index = self.similarity_score(input_text, index_docs)

        # 4) Compose answer with Gemini
        answer = self.generate_answer(input_text, index_docs, news_docs)

        # Simple confidence from top cosine
        top_scores = [s for _, s in (scored_news[:1] + scored_index[:1])]
        confidence = float(np.mean(top_scores)) if top_scores else 0.0

        return {
            "answer": answer,
            "confidence": confidence,
            "top_news": [d for d, s in scored_news[:5]],
            "top_index": [d for d, s in scored_index[:5]],
        }


