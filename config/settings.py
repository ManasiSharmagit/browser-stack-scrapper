import os
from pathlib import Path

from dotenv import load_dotenv


BASE_DIR = Path(__file__).resolve().parent.parent

load_dotenv(BASE_DIR / ".env")


class Settings:
    EL_PAIS_BASE_URL: str | None = os.getenv("EL_PAIS_BASE_URL")
    IMAGES_DIR: Path = Path(os.getenv("IMAGES_DIR", BASE_DIR / "images"))
    TRANSLATE_API_KEY: str | None = os.getenv("TRANSLATE_API_KEY")
    TRANSLATE_API_URL: str | None = os.getenv("TRANSLATE_API_URL")
    TRANSLATE_API_HOST: str | None = os.getenv("TRANSLATE_API_HOST")
    BROWSERSTACK_USERNAME: str | None = os.getenv("BROWSERSTACK_USERNAME")
    BROWSERSTACK_ACCESS_KEY: str | None = os.getenv("BROWSERSTACK_ACCESS_KEY")
    BROWSERSTACK_BUILD_NAME: str | None = os.getenv("BROWSERSTACK_BUILD_NAME")
    BROWSERSTACK_HUB_URL: str | None = os.getenv("BROWSERSTACK_HUB_URL")
    SELENIUM_IMPLICIT_WAIT_SECONDS: int = int(os.getenv("SELENIUM_IMPLICIT_WAIT_SECONDS", "10"))
    PAGE_LOAD_TIMEOUT_SECONDS: int = int(os.getenv("PAGE_LOAD_TIMEOUT_SECONDS", "60"))


settings = Settings()

