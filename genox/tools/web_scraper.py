import httpx
from bs4 import BeautifulSoup
from genox.tools.base import registry
import re

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.9",
}

@registry.register
def fetch_webpage(url: str) -> str:
    """Fetch and read the contents of a webpage, extracting clean text and articles.
    Args:
        url: Full web address (e.g. 'https://example.com').
    """
    url_clean = url.strip()
    if not url_clean.startswith("http://") and not url_clean.startswith("https://"):
        url_clean = "https://" + url_clean

    try:
        with httpx.Client(headers=HEADERS, follow_redirects=True, timeout=20.0) as client:
            response = client.get(url_clean)
            response.raise_for_status()

        soup = BeautifulSoup(response.text, "html.parser")

        # Strip useless elements
        for tag in soup(["script", "style", "nav", "footer", "iframe", "noscript", "svg", "header"]):
            tag.decompose()

        title = soup.title.string.strip() if soup.title and soup.title.string else "Untitled Page"
        
        # Prefer main / article if available
        main_content = soup.find("article") or soup.find("main") or soup.find("body")
        raw_text = main_content.get_text(separator="\n") if main_content else soup.get_text(separator="\n")
        
        # Clean up excessive newlines & spaces
        lines = [line.strip() for line in raw_text.splitlines() if line.strip()]
        clean_text = "\n".join(lines)

        if len(clean_text) > 8000:
            clean_text = clean_text[:8000] + f"\n\n... [Content truncated: {len(clean_text) - 8000} characters remaining]"

        return f"=== Webpage Content: {title} ===\nURL: {url_clean}\n\n{clean_text}"

    except httpx.HTTPStatusError as e:
        return f"HTTP Error {e.response.status_code} when loading {url_clean}"
    except Exception as e:
        return f"Error loading webpage '{url_clean}': {str(e)}"
