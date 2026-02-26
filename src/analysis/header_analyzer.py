from __future__ import annotations

import collections
import re
from typing import Dict, Iterable


_WORD_RE = re.compile(r"[A-Za-z0-9']+")


def _extract_words(text: str) -> Iterable[str]:
    if not text:
        return []
    return (match.group(0).lower() for match in _WORD_RE.finditer(text))


def analyze_repeated_words(titles: Iterable[str], min_count: int = 3) -> Dict[str, int]:
    counter: collections.Counter[str] = collections.Counter()
    for title in titles:
        counter.update(_extract_words(title))

    return {word: count for word, count in counter.items() if count >= min_count}

