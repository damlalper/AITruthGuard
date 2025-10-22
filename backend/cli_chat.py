from __future__ import annotations

import argparse
import json

from .rag_chatbot import RAGChatbot


def main() -> None:
    parser = argparse.ArgumentParser(description="AITruthGuard RAG Chatbot CLI")
    parser.add_argument("query", type=str, help="Input text / news to verify")
    parser.add_argument("--k", type=int, default=5, help="Top-K retrieval from FAISS")
    args = parser.parse_args()

    bot = RAGChatbot()
    out = bot.ask(args.query, k=args.k)
    print(json.dumps(out, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()





