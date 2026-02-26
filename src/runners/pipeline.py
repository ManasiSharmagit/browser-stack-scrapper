from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List

from selenium.webdriver.remote.webdriver import WebDriver

from config.settings import settings
from src.analysis.header_analyzer import analyze_repeated_words
from src.models.article import Article
from src.scraper.elpais_opinion_scraper import ElPaisOpinionScraper
from src.translation.translator import TranslationError, get_translator
from src.utils.image_utils import download_image


@dataclass(slots=True)
class PipelineResult:
    articles: List[Article]
    repeated_words: Dict[str, int]


def run_pipeline(driver: WebDriver, max_articles: int = 5) -> PipelineResult:
    scraper = ElPaisOpinionScraper(driver=driver)
    articles = scraper.scrape_first_n(max_articles)

    for article in articles:
        if article.cover_image_url:
            saved = download_image(article.cover_image_url, settings.IMAGES_DIR)
            if saved is not None:
                article.cover_image_path = str(saved)

    translator = get_translator()
    for article in articles:
        if translator is None:
            article.title_en = article.title_es
            continue

        try:
            article.title_en = translator.translate_title_es_to_en(article.title_es)
        except TranslationError:
            article.title_en = article.title_es

    english_titles = [a.title_en or a.title_es for a in articles]
    repeated_words = analyze_repeated_words(english_titles)

    return PipelineResult(articles=articles, repeated_words=repeated_words)

