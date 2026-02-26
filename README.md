## El País Opinion Scraper

This project uses Selenium to open `elpais.com`, accept the cookie banner, navigate to the Opinión section, scrape the first five articles, optionally download their cover images, translate the titles from Spanish to English via a translation API, and analyze which English words appear more than twice across the headers. The same end‑to‑end pipeline can be run locally in a single browser or in parallel across multiple browsers and real devices on BrowserStack.

### High-level flow

1. Open the El País base URL from `EL_PAIS_BASE_URL`.
2. Accept the cookie consent banner.
3. Click the `Opinión` navigation link and wait for article elements.
4. Collect the first five article titles and URLs from the Opinión listing.
5. Visit each article page, extract the full Spanish content, and detect the cover image URL.
6. Download each cover image into the `images` directory.
7. Translate each Spanish title to English using the configured translation API.
8. Aggregate all translated titles and compute repeated words (count ≥ 3).
9. Print article details and the repeated-word statistics.

---

## Setup

### Prerequisites

- Python 3.10 or later.
- Google Chrome installed locally (for the local runner).
- A matching ChromeDriver available on your `PATH`.
- A BrowserStack account (for the BrowserStack runner).

### Create and activate a virtual environment

From the project root:

```bash
python -m venv .venv
source .venv/bin/activate  # macOS/Linux
# .venv\Scripts\activate   # Windows PowerShell
```

### Install dependencies

With the virtual environment active:

```bash
pip install -r requirements.txt
```

The main Python dependencies are:

- `selenium` for browser automation.
- `requests` for HTTP calls (translation API and image downloads).
- `python-dotenv` for loading configuration from `.env`.

---

## Environment variables and `.env`

Configuration is provided via environment variables, typically set in a `.env` file in the project root. The `config/settings.py` module loads `.env` automatically.

Use `env.example` as a template:

```bash
cp env.example .env
```

Then edit `.env` and fill in the real values:

- **Translation API (RapidAPI – Rapid Translate Multi Traduction)**
  - `TRANSLATE_API_KEY`: your RapidAPI `X-RapidAPI-Key` value.
  - `TRANSLATE_API_URL`: `https://rapid-translate-multi-traduction.p.rapidapi.com/t`
  - `TRANSLATE_API_HOST`: `rapid-translate-multi-traduction.p.rapidapi.com`

- **BrowserStack**
  - `BROWSERSTACK_USERNAME`: your BrowserStack username.
  - `BROWSERSTACK_ACCESS_KEY`: your BrowserStack access key.
  - `BROWSERSTACK_BUILD_NAME`: a label for grouping runs in the BrowserStack dashboard (e.g. `el-pais-scraper-build-1`).
  - `BROWSERSTACK_HUB_URL`: `hub-cloud.browserstack.com/wd/hub` (host plus path, no protocol).

- **Project settings**
  - `IMAGES_DIR`: directory where cover images will be saved (default `images`).
  - `EL_PAIS_BASE_URL`: base URL for the El País site (e.g. `https://elpais.com/`).
  - `SELENIUM_IMPLICIT_WAIT_SECONDS`: implicit wait time in seconds for Selenium element searches (default `10`).
  - `PAGE_LOAD_TIMEOUT_SECONDS`: page load timeout in seconds (default `60`).

Only `env.example` contains explanatory comments; `.env` itself should contain plain key/value pairs.

---

## Running locally

With `.venv` activated and `.env` configured:

```bash
bash scripts/run_local.sh
```

The script:

1. Activates `.venv` (if present).
2. Ensures dependencies from `requirements.txt` are installed.
3. Executes `python -m src.runners.local_runner`.

The local runner will:

- Open a local Chrome instance.
- Run the full pipeline described above.
- Print, for each of the first five Opinion articles:
  - URL.
  - Spanish title.
  - English title.
  - A snippet of Spanish content.
  - Cover image URL and saved image path (if any).
- Print the repeated-word counts for words appearing at least three times across the English titles.

---

## Running on BrowserStack

Once your BrowserStack credentials and hub URL are set in `.env`, you can run the same pipeline in parallel across multiple browsers and devices:

```bash
bash scripts/run_browserstack.sh
```

The script:

1. Activates `.venv` (if present).
2. Ensures dependencies are installed.
3. Executes `python -m src.runners.browserstack_runner`.

The BrowserStack runner:

- Builds five different capabilities (desktop and mobile combinations).
- Starts one remote WebDriver per capability against the BrowserStack hub.
- Runs `run_pipeline` in each session concurrently using a thread pool.
- Prints per-session success/failure logs and a final summary indicating how many sessions completed successfully.

You can monitor individual sessions and screenshots in the BrowserStack Automate dashboard under the configured build name.

