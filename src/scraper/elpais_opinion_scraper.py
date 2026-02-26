from __future__ import annotations

from dataclasses import dataclass
from typing import List, Optional, Tuple

from selenium.common.exceptions import (
    NoSuchElementException,
    TimeoutException,
    StaleElementReferenceException,
)
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from config.settings import settings
from src.models.article import Article


_DEFAULT_WAIT_SECONDS = 15


@dataclass(slots=True)
class ElPaisOpinionScraper:
    driver: WebDriver
    wait_seconds: int = _DEFAULT_WAIT_SECONDS

    def __post_init__(self) -> None:
        if not settings.EL_PAIS_BASE_URL:
            raise ValueError(
                "EL_PAIS_BASE_URL is not set. Configure it in your .env or environment "
                "before using ElPaisOpinionScraper.",
            )

        # Use a sensible implicit wait to make basic find_element calls more robust.
        try:
            self.driver.implicitly_wait(settings.SELENIUM_IMPLICIT_WAIT_SECONDS)
        except Exception:
            # Some remote drivers may not support this; it's safe to ignore.
            pass

    @property
    def base_url(self) -> str:
        assert settings.EL_PAIS_BASE_URL is not None
        return settings.EL_PAIS_BASE_URL

    def scrape_first_n(self, n: int = 5) -> List[Article]:
        self._open_opinion_section()
        cards = self._find_article_cards()

        title_url_pairs: List[Tuple[str, str]] = []
        seen_urls: set[str] = set()

        for card in cards:
            if len(title_url_pairs) >= n:
                break

            extracted = self._extract_title_and_url_from_card(card)
            if not extracted:
                continue

            title_es, url = extracted
            if not url or url in seen_urls:
                continue

            seen_urls.add(url)
            title_url_pairs.append((title_es, url))

        articles: List[Article] = []
        for title_es, url in title_url_pairs:
            detail = self._scrape_article_detail(title_es, url)
            if detail:
                articles.append(detail)

        return articles

    def _open_opinion_section(self) -> None:
        self.driver.get(self.base_url)

        self._accept_cookies_if_present()

        try:
            opinion_link = WebDriverWait(self.driver, self.wait_seconds).until(
                EC.element_to_be_clickable(
                    (By.XPATH, "//a[normalize-space()='Opinión']"),
                ),
            )
        except TimeoutException:
            try:
                opinion_link = WebDriverWait(self.driver, self.wait_seconds).until(
                    EC.element_to_be_clickable(
                        (By.XPATH, "//a[contains(normalize-space(), 'Opinión')]"),
                    ),
                )
            except TimeoutException as exc:
                raise TimeoutException(
                    "Could not locate a clickable 'Opinión' link in the site navigation.",
                ) from exc

        try:
            opinion_link.click()
        except TimeoutException:
            pass

        self._accept_cookies_if_present()

        try:
            WebDriverWait(self.driver, self.wait_seconds).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "article")),
            )
        except TimeoutException as exc:
            raise TimeoutException(
                "Timed out waiting for Opinion articles after clicking the 'Opinión' link.",
            ) from exc

        try:
            html = self.driver.find_element(By.TAG_NAME, "html")
            lang = (html.get_attribute("lang") or "").lower()
            if not lang.startswith("es"):
                raise RuntimeError(
                    f"El País page language appears to be '{lang}', not Spanish ('es'). "
                    "Switch the site to Spanish and try again.",
                )
        except NoSuchElementException:
            pass

    def _accept_cookies_if_present(self) -> None:
        try:
            wait = WebDriverWait(self.driver, 5)

            def _click_button(d: WebDriver) -> bool:
                try:
                    btn = d.find_element(By.ID, "didomi-notice-agree-button")
                except (NoSuchElementException, StaleElementReferenceException):
                    return False

                if not btn.is_displayed() or not btn.is_enabled():
                    return False

                d.execute_script("arguments[0].click();", btn)
                return True

            try:
                wait.until(_click_button)
                return
            except TimeoutException:
                pass

            xpath = (
                "//*[self::button or self::span or self::a or self::div]"
                "[contains(translate(normalize-space(), 'ACEPTAR', 'aceptar'), 'aceptar')]"
            )
            candidates = self.driver.find_elements(By.XPATH, xpath)
            for el in candidates:
                try:
                    if el.is_displayed() and el.is_enabled():
                        self.driver.execute_script("arguments[0].click();", el)
                        break
                except StaleElementReferenceException:
                    continue
        except Exception:
            return

    def _find_article_cards(self):
        return self.driver.find_elements(By.CSS_SELECTOR, "article")

    def _extract_title_and_url_from_card(self, card) -> Optional[Tuple[str, str]]:
        candidate_selectors = ("h2 a", "h3 a", "a")
        try:
            for selector in candidate_selectors:
                links = card.find_elements(By.CSS_SELECTOR, selector)
                if not links:
                    continue

                link = links[0]
                title = (link.text or "").strip()
                url = (link.get_attribute("href") or "").strip()

                if title and url:
                    return title, url
        except StaleElementReferenceException:
            return None

        return None

    def _scrape_article_detail(self, title_es: str, url: str) -> Optional[Article]:
        try:
            self.driver.get(url)
        except Exception:
            return None

        try:
            article_el = WebDriverWait(self.driver, self.wait_seconds).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "article")),
            )
        except TimeoutException:
            return None

        content_text = (article_el.text or "").strip()

        cover_image_url: Optional[str] = None
        image_selectors = (
            "figure img",
            "header img",
            "img",
        )
        for selector in image_selectors:
            try:
                img = article_el.find_element(By.CSS_SELECTOR, selector)
                src = (img.get_attribute("src") or "").strip()
                if src:
                    cover_image_url = src
                    break
            except NoSuchElementException:
                continue

        return Article(
            title_es=title_es,
            content_es=content_text,
            url=url,
            cover_image_url=cover_image_url,
        )

