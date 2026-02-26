from __future__ import annotations

from dataclasses import dataclass


@dataclass(slots=True)
class Article:
    title_es: str
    content_es: str
    url: str
    cover_image_url: str | None = None
    cover_image_path: str | None = None
    title_en: str | None = None

