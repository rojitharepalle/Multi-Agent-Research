from langchain_core.tools import tool
from tavily import TavilyClient
from core.config import settings
from core.logging import logger


@tool
def web_search(query: str, max_results: int = 5) -> str:
    """
    Search the web for current information about a topic.
    Use this to find recent news, facts, and general knowledge.

    Args:
        query: The search query string
        max_results: Number of results to return (default 5)

    Returns:
        Formatted string of search results with titles, URLs, and snippets
    """
    try:
        client = TavilyClient(api_key=settings.tavily_api_key)
        response = client.search(
            query=query,
            max_results=max_results,
            search_depth="advanced",
            include_answer=True,
        )

        results = []

        if response.get("answer"):
            results.append(f"Quick Answer: {response['answer']}\n")

        for i, result in enumerate(response.get("results", []), 1):
            results.append(
                f"[{i}] {result.get('title', 'No title')}\n"
                f"URL: {result.get('url', '')}\n"
                f"Content: {result.get('content', '')[:500]}\n"
            )

        formatted = "\n".join(results) if results else "No results found."
        logger.info(f"Web search for '{query}' returned {len(response.get('results', []))} results")
        return formatted

    except Exception as e:
        logger.error(f"Web search failed: {e}")
        return f"Web search failed: {str(e)}"
