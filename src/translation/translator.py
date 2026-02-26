from __future__ import annotations

from dataclasses import dataclass
from typing import Any, List

import requests

from config.settings import settings


class TranslationError(RuntimeError):
    pass


@dataclass(slots=True)
class Translator:
    api_url: str
    api_key: str
    api_host: str

    def translate_title_es_to_en(self, title_es: str, timeout_seconds: int = 15) -> str:
        if not title_es:
            return title_es

        payload = {
            "from": "es",
            "to": "en",
            "q": [title_es],
        }

        headers = {
            "x-rapidapi-key": self.api_key,
            "x-rapidapi-host": self.api_host,
            "Content-Type": "application/json",
        }

        try:
            response = requests.post(self.api_url, json=payload, headers=headers, timeout=timeout_seconds)
            response.raise_for_status()
        except Exception as exc:
            raise TranslationError(f"Translation request failed: {exc}") from exc

        try:
            data: Any = response.json()
        except Exception as exc:
            raise TranslationError(f"Could not decode translation response as JSON: {exc}") from exc

        translated: Any = None
        if isinstance(data, list) and data:
            translated = data[0]

        if not translated or not isinstance(translated, str):
            raise TranslationError(
                "Translation response JSON was not the expected array of translated strings. "
                "Check your RapidAPI configuration or adjust translator.py if the provider changed.",
            )

        return translated


def get_translator() -> Translator | None:
    if not settings.TRANSLATE_API_URL or not settings.TRANSLATE_API_KEY or not settings.TRANSLATE_API_HOST:
        return None

    return Translator(
        api_url=settings.TRANSLATE_API_URL,
        api_key=settings.TRANSLATE_API_KEY,
        api_host=settings.TRANSLATE_API_HOST,
    )

