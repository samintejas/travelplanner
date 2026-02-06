"""Web search fallback using DuckDuckGo."""

from duckduckgo_search import DDGS


def search_web(query: str, max_results: int = 5) -> list[dict]:
    """
    Search the web using DuckDuckGo.
    Returns list of results with title, url, and snippet.
    """
    try:
        with DDGS() as ddgs:
            results = list(ddgs.text(query, max_results=max_results))
            return [
                {
                    "title": r.get("title", ""),
                    "url": r.get("href", ""),
                    "snippet": r.get("body", "")
                }
                for r in results
            ]
    except Exception as e:
        print(f"Web search error: {e}")
        return []


def format_web_results(results: list[dict]) -> str:
    """Format web search results as context string."""
    if not results:
        return ""

    parts = ["[WEB SEARCH RESULTS]"]
    for r in results:
        parts.append(f"- {r['title']}: {r['snippet']}")

    return "\n".join(parts)


def search_travel_info(destination: str, topic: str = "") -> str:
    """Search for travel information about a destination."""
    query = f"{destination} travel {topic}".strip()
    results = search_web(query)
    return format_web_results(results)
