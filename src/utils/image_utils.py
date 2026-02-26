from __future__ import annotations

import hashlib
import os
from pathlib import Path
from urllib.parse import urlparse

import requests


def _guess_extension(content_type: str | None, url: str) -> str:
    if content_type:
        ct = content_type.split(";", 1)[0].strip().lower()
        if ct == "image/jpeg":
            return ".jpg"
        if ct == "image/png":
            return ".png"
        if ct == "image/webp":
            return ".webp"
        if ct == "image/gif":
            return ".gif"

    parsed = urlparse(url)
    _, ext = os.path.splitext(parsed.path)
    if ext and len(ext) <= 5:
        return ext
    return ".img"


def download_image(image_url: str, images_dir: Path, timeout_seconds: int = 30) -> Path | None:
    if not image_url:
        return None

    images_dir.mkdir(parents=True, exist_ok=True)

    try:
        resp = requests.get(image_url, timeout=timeout_seconds)
        resp.raise_for_status()
    except Exception:
        return None

    ext = _guess_extension(resp.headers.get("Content-Type"), image_url)
    filename = hashlib.sha256(image_url.encode("utf-8")).hexdigest()[:24] + ext
    out_path = images_dir / filename

    try:
        out_path.write_bytes(resp.content)
    except Exception:
        return None

    return out_path


