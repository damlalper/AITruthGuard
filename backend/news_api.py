from __future__ import annotations

import datetime as dt
from dataclasses import dataclass
from typing import Iterable, List, Optional

import requests

from .data_loader import NewsRecord, _basic_clean_text


NEWS_API_ENDPOINT = "https://newsapi.org/v2/everything"


@dataclass
class NewsApiConfig:
    api_key: str
    language: str  # e.g., "tr,en"
    days_back: int
    query: str
    page_size: int = 100
    max_pages: int = 2  # avoid quota burn; adjust as needed


def fetch_recent_news(cfg: NewsApiConfig) -> List[NewsRecord]:
    if not cfg.api_key:
        return []
    to_date = dt.datetime.utcnow()
    from_date = to_date - dt.timedelta(days=cfg.days_back)

    headers = {"X-Api-Key": cfg.api_key}
    languages = [lang.strip() for lang in cfg.language.split(",") if lang.strip()]
    all_records: List[NewsRecord] = []

    for lang in languages:
        for page in range(1, cfg.max_pages + 1):
            try:
                params = {
                    "q": cfg.query,
                    "language": lang,
                    "from": from_date.strftime("%Y-%m-%d"),
                    "to": to_date.strftime("%Y-%m-%d"),
                    "sortBy": "publishedAt",
                    "pageSize": cfg.page_size,
                    "page": page,
                }
                resp = requests.get(NEWS_API_ENDPOINT, headers=headers, params=params, timeout=30)
                if resp.status_code != 200:
                    break
                data = resp.json()
                articles = data.get("articles", [])
                if not articles:
                    break
                for idx, a in enumerate(articles):
                    title = _basic_clean_text(a.get("title", ""))
                    content = _basic_clean_text(
                        a.get("content") or a.get("description") or ""
                    )
                    if not content and not title:
                        continue
                    all_records.append(
                        NewsRecord(
                            id=f"EXT-{lang}-{page}-{idx}",
                            title=title,
                            text=content or title,
                            label="EXTERNAL",
                            source=f"newsapi:{a.get('source', {}).get('name') or 'unknown'}",
                            url=a.get("url") or "",
                        )
                    )
            except Exception:
                break

    return all_records


