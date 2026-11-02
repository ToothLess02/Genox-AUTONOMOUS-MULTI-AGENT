from genox.tools.base import registry
import json

@registry.register
def web_search(query: str, max_results: int = 5) -> str:
    """Search the internet for live information, news, documentation, or facts.
    Args:
        query: The search keywords or question.
        max_results: Number of search results (default 5, max 10).
    """
    clean_query = query.strip()
    if not clean_query:
        return "Error: Search query cannot be empty."

    max_results = max(1, min(max_results, 10))

    try:
        try:
            from ddgs import DDGS
        except ImportError:
            from duckduckgo_search import DDGS

        ddgs = DDGS()
        results = list(ddgs.text(clean_query, max_results=max_results))
        
        if not results:
            return f"No web search results found for query: '{clean_query}'."

        formatted = [f"=== Web Search Results for '{clean_query}' ==="]
        for idx, item in enumerate(results, 1):
            title = item.get("title", "No Title")
            url = item.get("href") or item.get("link", "")
            snippet = item.get("body") or item.get("snippet", "")
            formatted.append(f"{idx}. {title}\n   URL: {url}\n   Summary: {snippet}\n")

        return "\n".join(formatted)

    except Exception as e:
        return f"Web Search Error: {str(e)}"
