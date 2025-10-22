from __future__ import annotations

import json
import os
from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple

import faiss
import numpy as np


@dataclass
class IndexMetadata:
    dim: int
    metric: str  # "ip" or "l2"
    count: int


class FaissIndexManager:
    def __init__(self, dim: int, metric: str = "ip") -> None:
        if metric not in {"ip", "l2"}:
            raise ValueError("metric must be 'ip' or 'l2'")
        self.dim = dim
        self.metric = metric
        self.index = (
            faiss.IndexFlatIP(dim) if metric == "ip" else faiss.IndexFlatL2(dim)
        )
        self.payload: List[Dict] = []

    def add(self, embeddings: np.ndarray, metadatas: List[Dict]) -> None:
        if embeddings.dtype != np.float32:
            embeddings = embeddings.astype(np.float32)
        if embeddings.ndim != 2 or embeddings.shape[0] != len(metadatas):
            raise ValueError("embeddings must be 2D and match metadatas length")
        self.index.add(embeddings)
        self.payload.extend(metadatas)

    def search(self, query_embeddings: np.ndarray, k: int = 5) -> Tuple[np.ndarray, List[List[Dict]]]:
        if query_embeddings.dtype != np.float32:
            query_embeddings = query_embeddings.astype(np.float32)
        distances, indices = self.index.search(query_embeddings, k)
        results: List[List[Dict]] = []
        for row in indices:
            hits: List[Dict] = []
            for idx in row:
                if idx == -1:
                    continue
                if 0 <= idx < len(self.payload):
                    hits.append(self.payload[idx])
            results.append(hits)
        return distances, results

    def save(self, faiss_path: str, data_csv_path: str, metadata_json_path: str) -> None:
        faiss.write_index(self.index, faiss_path)

        # Save flattened data CSV (title + text + label + source)
        import csv

        with open(data_csv_path, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(
                f, fieldnames=["id", "title", "text", "label", "source", "url"]
            )
            writer.writeheader()
            for meta in self.payload:
                writer.writerow(
                    {
                        "id": meta.get("id", ""),
                        "title": meta.get("title", ""),
                        "text": meta.get("text", ""),
                        "label": meta.get("label", ""),
                        "source": meta.get("source", ""),
                        "url": meta.get("url", ""),
                    }
                )

        # Save metadata JSON (schema + counts)
        info = IndexMetadata(dim=self.dim, metric=self.metric, count=len(self.payload))
        with open(metadata_json_path, "w", encoding="utf-8") as f:
            json.dump(info.__dict__, f, ensure_ascii=False, indent=2)

    @staticmethod
    def load(faiss_path: str, metadata_json_path: str, payload: Optional[List[Dict]] = None) -> "FaissIndexManager":
        index = faiss.read_index(faiss_path)
        with open(metadata_json_path, "r", encoding="utf-8") as f:
            meta = json.load(f)
        mgr = FaissIndexManager(dim=meta["dim"], metric=meta["metric"])
        mgr.index = index
        mgr.payload = payload or []
        return mgr


