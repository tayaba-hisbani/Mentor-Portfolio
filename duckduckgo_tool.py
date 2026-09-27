"""
A lightweight, dependency-free DuckDuckGo search tool for CrewAI agents.

We hit the `duckduckgo_search` package directly instead of going through a
LangChain wrapper, so there's one less dependency to install and version-pin.
Every result includes its source URL so agents (and the user) can verify
claims instead of taking the model's word for it.
"""

from crewai.tools import BaseTool
from pydantic import Field
from duckduckgo_search import DDGS


class DuckDuckGoSearchTool(BaseTool):
    name: str = "DuckDuckGo Web Search"
    description: str = (
        "Searches the web via DuckDuckGo for current, real-world information "
        "(freelance platform rules, pricing benchmarks, in-demand skills, "
        "portfolio examples, market trends). Input should be a plain search "
        "query string. Returns a numbered list of results with title, "
        "snippet, and source URL. Always prefer this tool over guessing when "
        "a claim needs to be current or verifiable."
    )
    max_results: int = Field(default=5, description="Number of results to return")

    def _run(self, query: str) -> str:
        try:
            with DDGS() as ddgs:
                results = list(ddgs.text(query, max_results=self.max_results))
        except Exception as exc:  # network hiccups, rate limits, etc.
            return (
                f"Search failed for query '{query}' ({exc}). "
                "Do not invent facts to fill this gap — tell the user the "
                "search could not be completed and answer only from what is "
                "already verified."
            )

        if not results:
            return (
                f"No search results found for '{query}'. "
                "Do not fabricate an answer — say the information could not "
                "be verified."
            )

        formatted = []
        for i, r in enumerate(results, start=1):
            title = r.get("title", "Untitled")
            body = r.get("body", "").strip()
            href = r.get("href", "")
            formatted.append(f"{i}. {title}\n   {body}\n   Source: {href}")

        return "\n\n".join(formatted)
