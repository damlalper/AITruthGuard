from __future__ import annotations

import os
from dataclasses import dataclass
from typing import List, Tuple

import pandas as pd


@dataclass
class NewsRecord:
    id: str
    title: str
    text: str
    label: str  # "FAKE" | "TRUE" | "EXTERNAL"
    source: str  # file path or provider
    url: str = ""  # optional link if available


def _basic_clean_text(text: str) -> str:
    if not isinstance(text, str):
        return ""
    # Minimal normalization: strip, collapse whitespace
    cleaned = " ".join(text.replace("\n", " ").replace("\r", " ").split())
    return cleaned.strip()


def load_fake_true_csvs(fake_path: str, true_path: str) -> List[NewsRecord]:
    records: List[NewsRecord] = []
    if not os.path.exists(fake_path):
        raise FileNotFoundError(f"Fake dataset not found at {fake_path}")
    if not os.path.exists(true_path):
        raise FileNotFoundError(f"True dataset not found at {true_path}")

    fake_df = pd.read_csv(fake_path)
    true_df = pd.read_csv(true_path)

    # Expected columns commonly: title, text | may vary across datasets.
    def extract(df: pd.DataFrame, label: str) -> List[NewsRecord]:
        cols = {c.lower(): c for c in df.columns}
        title_col = cols.get("title") or next((c for c in df.columns if c.lower().startswith("title")), None)
        text_col = cols.get("text") or next((c for c in df.columns if c.lower().startswith("text")), None)
        if text_col is None:
            # Try content/body fallbacks
            text_col = (
                cols.get("content")
                or cols.get("body")
                or next((c for c in df.columns if "content" in c.lower() or "body" in c.lower()), None)
            )
        if text_col is None:
            raise ValueError("Could not infer text/content column in dataset")

        out: List[NewsRecord] = []
        for idx, row in df.iterrows():
            title_val = _basic_clean_text(str(row.get(title_col, ""))) if title_col else ""
            text_val = _basic_clean_text(str(row.get(text_col, "")))
            if not text_val:
                continue
            rec = NewsRecord(
                id=f"{label}-{idx}",
                title=title_val,
                text=text_val,
                label=label,
                source=f"csv:{os.path.basename(fake_path) if label=='FAKE' else os.path.basename(true_path)}",
                url="",
            )
            out.append(rec)
        return out

    records.extend(extract(fake_df, "FAKE"))
    records.extend(extract(true_df, "TRUE"))

    return records


