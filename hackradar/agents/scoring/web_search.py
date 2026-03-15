"""
Google Custom Search tool for scoring agents.

Provides:
- `google_search`: a Railtracks function_node the agent can call at its discretion.
- `prefetch_similar_projects`: async fetch used by RAGPrefetchStrategy (injected into
  the prompt so the LLM can decide whether the results are relevant).

Requires GOOGLE_SEARCH_API_KEY + GOOGLE_SEARCH_ENGINE_ID in config/.env.
"""

import logging
from typing import Any

import httpx
import railtracks as rt

from hackradar.config import get_settings

logger = logging.getLogger(__name__)

GOOGLE_SEARCH_URL = "https://www.googleapis.com/customsearch/v1"


def _format_results(data: dict) -> str:
    """Format a Google Custom Search API response into a readable string."""
    items = data.get("items", [])
    if not items:
        return "[No similar projects found via web search]"

    parts: list[str] = []
    for i, item in enumerate(items, 1):
        title = item.get("title", "Untitled")
        url = item.get("link", "")
        snippet = item.get("snippet", "").replace("\n", " ")
        parts.append(f"{i}. **{title}**\n   URL: {url}\n   Summary: {snippet}")

    return "\n\n".join(parts)


async def _do_google_search(query: str, num_results: int = 5) -> str:
    """Call Google Custom Search API and return formatted results."""
    settings = get_settings()
    api_key = settings.google_search_api_key
    engine_id = settings.google_search_engine_id

    if not api_key or not engine_id:
        logger.warning("Google search skipped: GOOGLE_SEARCH_API_KEY or GOOGLE_SEARCH_ENGINE_ID not set")
        return "[Web search skipped: credentials not configured]"

    params = {
        "key": api_key,
        "cx": engine_id,
        "q": query,
        "num": min(num_results, 10),
    }
    try:
        async with httpx.AsyncClient(timeout=15.0) as client:
            response = await client.get(GOOGLE_SEARCH_URL, params=params)
            response.raise_for_status()
            return _format_results(response.json())
    except httpx.HTTPStatusError as exc:
        logger.error("Google Search API error %s: %s", exc.response.status_code, exc.response.text)
        return f"[Web search failed: HTTP {exc.response.status_code}]"
    except Exception as exc:
        logger.error("Web search failed: %s", exc)
        return f"[Web search failed: {exc}]"


@rt.function_node
async def google_search(query: str, num_results: int = 5) -> str:
    """
    Search Google for similar projects or existing implementations related to the query.

    Use this tool when evaluating novelty, originality, innovation, or uniqueness criteria.
    Search for the project's core idea to discover whether similar tools already exist.

    Args:
        query (str): A description of the project idea or technology to search for.
        num_results (int): Number of results to return (max 10, default 5).

    Returns:
        A numbered list of similar projects with titles, URLs, and descriptions.
    """
    return await _do_google_search(query, num_results)


async def prefetch_similar_projects(query: str) -> str:
    """
    Pre-fetch web search results for a project.

    Used by RAGPrefetchStrategy (which cannot make tool calls) to inject
    similar-project context into the prompt. The LLM decides which criteria
    benefit from the results.
    """
    return await _do_google_search(query, num_results=5)
