from crewai.tools import BaseTool
from pydantic import Field
from duckduckgo_search import DDGS


class DuckDuckGoSearchTool(BaseTool):
    name: str = "DuckDuckGo Web Search"
    description: str = "Searches the web via DuckDuckGo for current facts. Input is a plain search query string. Returns numbered results with title, snippet, and source URL."
    max_results: int = Field(default=5, description="Number of results to return")

    def _run(self, query: str) -> str:
        try:
            with DDGS() as ddgs:
                results = list(ddgs.text(query, max_results=self.max_results))
        except Exception as exc:
            return f"Search failed for query '{query}' ({exc}). Do not invent facts to fill this gap."

        if not results:
            return f"No search results found for '{query}'. Do not fabricate an answer."

        formatted = []
        for i, r in enumerate(results, start=1):
            title = r.get("title", "Untitled")
            body = r.get("body", "").strip()
            href = r.get("href", "")
            formatted.append(f"{i}. {title}\n   {body}\n   Source: {href}")

        return "\n\n".join(formatted)
