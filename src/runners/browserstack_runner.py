from __future__ import annotations

import concurrent.futures
from dataclasses import dataclass
from typing import Any, Dict, List

from selenium import webdriver
from selenium.webdriver.remote.webdriver import WebDriver

from config.settings import settings
from src.runners.pipeline import PipelineResult, run_pipeline


@dataclass(slots=True)
class BrowserStackConfig:
    username: str
    access_key: str
    hub_url: str
    build_name: str


def _get_bs_config() -> BrowserStackConfig:
    if not settings.BROWSERSTACK_USERNAME or not settings.BROWSERSTACK_ACCESS_KEY:
        raise ValueError(
            "BrowserStack credentials are not configured. "
            "Set BROWSERSTACK_USERNAME and BROWSERSTACK_ACCESS_KEY in your .env or environment.",
        )
    if not settings.BROWSERSTACK_HUB_URL:
        raise ValueError(
            "BrowserStack hub URL is not configured. "
            "Set BROWSERSTACK_HUB_URL in your .env or environment.",
        )

    return BrowserStackConfig(
        username=settings.BROWSERSTACK_USERNAME,
        access_key=settings.BROWSERSTACK_ACCESS_KEY,
        hub_url=settings.BROWSERSTACK_HUB_URL,
        build_name=settings.BROWSERSTACK_BUILD_NAME or "el-pais-scraper-browserstack",
    )


def _build_capabilities() -> List[Dict[str, Any]]:
    bs = _get_bs_config()

    base_bstack_options: Dict[str, Any] = {
        "buildName": bs.build_name,
        "projectName": "ElPais Opinion Scraper",
        "sessionName": "ElPais Opinion pipeline",
        "seleniumVersion": "4.0.0",
    }

    caps: List[Dict[str, Any]] = [
        {
            "browserName": "Chrome",
            "browserVersion": "latest",
            "bstack:options": {
                **base_bstack_options,
                "os": "Windows",
                "osVersion": "11",
            },
        },
        {
            "browserName": "Edge",
            "browserVersion": "latest",
            "bstack:options": {
                **base_bstack_options,
                "os": "Windows",
                "osVersion": "10",
            },
        },
        {
            "browserName": "Safari",
            "browserVersion": "latest",
            "bstack:options": {
                **base_bstack_options,
                "os": "OS X",
                "osVersion": "Sonoma",
            },
        },
        {
            "browserName": "Chrome",
            "browserVersion": "latest",
            "bstack:options": {
                **base_bstack_options,
                "deviceName": "Samsung Galaxy S23",
                "osVersion": "13.0",
                "platformName": "android",
                "realMobile": True,
            },
        },
        {
            "browserName": "Safari",
            "browserVersion": "latest",
            "bstack:options": {
                **base_bstack_options,
                "deviceName": "iPhone 15",
                "osVersion": "17",
                "platformName": "ios",
                "realMobile": True,
            },
        },
    ]
    return caps


def _create_remote_driver(capabilities: Dict[str, Any], bs: BrowserStackConfig) -> WebDriver:
    options = webdriver.ChromeOptions()
    for key, value in capabilities.items():
        options.set_capability(key, value)

    return webdriver.Remote(
        command_executor=f"https://{bs.username}:{bs.access_key}@{bs.hub_url}",
        options=options,
    )


def _run_single_session(capabilities: Dict[str, Any], index: int) -> PipelineResult | None:
    bs = _get_bs_config()
    driver: WebDriver | None = None
    try:
        driver = _create_remote_driver(capabilities, bs)
        driver.set_page_load_timeout(settings.PAGE_LOAD_TIMEOUT_SECONDS)
        result = run_pipeline(driver)
        print(f"[BrowserStack session #{index}] Completed successfully.")
        return result
    except Exception as exc:
        print(f"[BrowserStack session #{index}] Failed: {exc}")
        return None
    finally:
        if driver is not None:
            driver.quit()


def main() -> None:
    capabilities_list = _build_capabilities()

    print("Starting BrowserStack runs in parallel...")

    results: List[PipelineResult | None] = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=len(capabilities_list)) as executor:
        futures = [
            executor.submit(_run_single_session, caps, i + 1)
            for i, caps in enumerate(capabilities_list)
        ]
        for future in concurrent.futures.as_completed(futures):
            results.append(future.result())

    successful = [r for r in results if r is not None]
    print(f"\nBrowserStack runs completed. Successful sessions: {len(successful)}/{len(results)}")


if __name__ == "__main__":
    main()

