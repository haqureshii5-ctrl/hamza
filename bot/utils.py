import re
from typing import Iterable

def safe_truncate(text: str, limit: int) -> str:
    if len(text) <= limit:
        return text
    return text[: limit - 1].rstrip() + "…"

def normalize_topic(topic: str) -> str:
    return re.sub(r"\s+", " ", topic.strip().lower())

def format_hashtags(terms: Iterable[str]) -> str:
    normalized = []
    for term in terms:
        clean = re.sub(r"[^\w#]+", "", term.strip().replace(" ", ""))
        if clean:
            normalized.append(f"#{clean.lstrip('#')}")
    return " ".join(dict.fromkeys(normalized))
