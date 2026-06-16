import requests
import trafilatura

# Some sites block requests with no User-Agent, treating them as bots.
# A normal browser-like header avoids unnecessary failures.
USER_AGENT = "Mozilla/5.0 (compatible; KAIROXBot/1.0)"

# Keep this short. One slow or dead site should not stall the whole
# ingestion run waiting on a response.
FETCH_TIMEOUT_SECONDS = 10


def scrape_article(url: str) -> str | None:
    """
    Fetches a URL and extracts the main article text using trafilatura.
    Returns None if the page can't be fetched or no article content
    can be extracted (paywalls, JS-rendered pages, dead links, bot
    blocking, etc). Scraping is best-effort, not guaranteed. Callers
    should fall back to the RSS snippet when this returns None.
    """
    try:
        response = requests.get(
            url,
            headers={"User-Agent": USER_AGENT},
            timeout=FETCH_TIMEOUT_SECONDS,
        )
        response.raise_for_status()
    except Exception:
        return None

    return trafilatura.extract(response.text)