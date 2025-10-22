import os
from dataclasses import dataclass
from typing import Optional

from dotenv import load_dotenv, find_dotenv


@dataclass
class AppConfig:
    news_api_key: Optional[str]
    gemini_api_key: Optional[str]
    model_name: str
    data_dir: str
    dataset_fake_path: str
    dataset_true_path: str
    output_faiss_path: str
    output_data_csv_path: str
    output_metadata_json_path: str
    index_metric: str
    news_language: str
    news_days_back: int
    news_query: str
    batch_size: int
    env_path: Optional[str] = None


def load_config() -> AppConfig:
    # Load .env from nearest file (project root or parents)
    env_path = find_dotenv(usecwd=True)
    if env_path:
        load_dotenv(dotenv_path=env_path, override=True)
    else:
        env_path = os.path.join(os.getcwd(), ".env")
        load_dotenv(dotenv_path=env_path, override=True)

    project_root = os.getcwd()
    data_dir = os.path.join(project_root, "data", "FakeNews_dataset")

    def _clean(val: Optional[str]) -> Optional[str]:
        if val is None:
            return None
        v = val.strip().strip('"').strip("'")
        return v if v else None

    return AppConfig(
        news_api_key=_clean(os.getenv("NEWS_API_KEY")),
        gemini_api_key=_clean(os.getenv("GEMINI_API_KEY")),
        # Multilingual, compact model suitable for TR/EN
        model_name=os.getenv(
            "EMBEDDING_MODEL",
            "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2",
        ),
        data_dir=data_dir,
        dataset_fake_path=os.path.join(data_dir, "Fake.csv"),
        dataset_true_path=os.path.join(data_dir, "True.csv"),
        output_faiss_path=os.path.join(project_root, "truth_guard_index.faiss"),
        output_data_csv_path=os.path.join(project_root, "truth_guard_data.csv"),
        output_metadata_json_path=os.path.join(project_root, "truth_guard_metadata.json"),
        index_metric=os.getenv("INDEX_METRIC", "ip"),  # ip (cosine via norm) or l2
        news_language=os.getenv("NEWS_LANGUAGE", "tr,en"),
        news_days_back=int(os.getenv("NEWS_DAYS_BACK", "7")),
        news_query=os.getenv("NEWS_QUERY", "(finans OR ekonomi OR bankacilik) OR (finance OR economy OR banking)"),
        batch_size=int(os.getenv("BATCH_SIZE", "64")),
        env_path=env_path if os.path.exists(env_path) else None,
    )


