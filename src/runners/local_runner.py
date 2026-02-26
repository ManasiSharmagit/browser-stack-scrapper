from __future__ import annotations

from textwrap import shorten

from selenium import webdriver
from selenium.webdriver.chrome.options import Options as ChromeOptions

from config.settings import settings
from src.runners.pipeline import PipelineResult, run_pipeline


def _create_local_driver() -> webdriver.Chrome:
    options = ChromeOptions()
    driver = webdriver.Chrome(options=options)
    driver.set_page_load_timeout(settings.PAGE_LOAD_TIMEOUT_SECONDS)
    return driver


def _print_result(result: PipelineResult) -> None:
    print("\n=== Articles ===\n")
    for idx, article in enumerate(result.articles, start=1):
        print(f"Article #{idx}")
        print(f"  URL: {article.url}")
        print(f"  Title (ES): {article.title_es}")
        print(f"  Title (EN): {article.title_en}")
        snippet = shorten(article.content_es, width=300, placeholder="...")
        print(f"  Content (ES, snippet): {snippet}")
        print(f"  Cover image URL: {article.cover_image_url or 'N/A'}")
        print(f"  Saved image path: {article.cover_image_path or 'N/A'}")
        print()

    print("=== Repeated words in translated titles (count >= 3) ===")
    if not result.repeated_words:
        print("  None found.")
    else:
        for word, count in sorted(result.repeated_words.items(), key=lambda x: (-x[1], x[0])):
            print(f"  {word}: {count}")


def main() -> None:
    driver = None
    try:
        driver = _create_local_driver()
        pipeline_result = run_pipeline(driver)
        _print_result(pipeline_result)
    finally:
        if driver is not None:
            driver.quit()


if __name__ == "__main__":
    main()

