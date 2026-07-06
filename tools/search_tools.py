"""Search & sentiment tools — Tavily (preferred) with DuckDuckGo fallback."""
from __future__ import annotations

from datetime import datetime, timedelta
from typing import Type

from pydantic import BaseModel, Field
from crewai.tools import BaseTool

from config.settings import USE_TAVILY, TAVILY_API_KEY


# ── Input schemas ──────────────────────────────────────────────────────────────

class NewsSearchInput(BaseModel):
    query: str = Field(..., description="Search query for financial news")
    max_results: int = Field(default=8, description="Number of results to return")


class SentimentInput(BaseModel):
    text: str = Field(..., description="Text corpus to analyze for market sentiment")
    ticker: str = Field(..., description="Ticker the text refers to")


# ── News search ────────────────────────────────────────────────────────────────

class NewsSearchTool(BaseTool):
    name: str = "news_search"
    description: str = (
        "Searches the web for the latest financial news about a company or topic "
        "from the last 48 hours. Returns headlines and snippets."
    )
    args_schema: Type[BaseModel] = NewsSearchInput

    def _run(self, query: str, max_results: int = 8) -> str:
        since = (datetime.utcnow() - timedelta(hours=48)).strftime("%Y-%m-%d")
        enriched_query = f"{query} after:{since}"

        if USE_TAVILY:
            return self._tavily_search(enriched_query, max_results)
        return self._ddg_search(enriched_query, max_results)

    # ── Tavily ─────────────────────────────────────────────────────────────────
    def _tavily_search(self, query: str, max_results: int) -> str:
        try:
            from tavily import TavilyClient
            client = TavilyClient(api_key=TAVILY_API_KEY)
            response = client.search(
                query=query,
                search_depth="advanced",
                max_results=max_results,
                include_answer=True,
            )
            results = []
            if response.get("answer"):
                results.append(f"**AI Summary:** {response['answer']}\n")

            for r in response.get("results", []):
                results.append(
                    f"- **{r.get('title', 'No title')}**\n"
                    f"  {r.get('content', '')[:300]}...\n"
                    f"  Source: {r.get('url', '')}"
                )
            return "\n".join(results) if results else "No results found."
        except Exception as e:
            return f"Tavily search error: {e}"

    # ── DuckDuckGo fallback ────────────────────────────────────────────────────
    def _ddg_search(self, query: str, max_results: int) -> str:
        try:
            from duckduckgo_search import DDGS
            with DDGS() as ddgs:
                hits = list(ddgs.news(query, max_results=max_results))

            if not hits:
                return "No recent news found."

            results = []
            for h in hits:
                results.append(
                    f"- **{h.get('title', '')}** ({h.get('date', '')})\n"
                    f"  {h.get('body', '')[:280]}...\n"
                    f"  Source: {h.get('url', '')}"
                )
            return "\n".join(results)
        except Exception as e:
            return f"DuckDuckGo search error: {e}"


# ── Macro / sector search ──────────────────────────────────────────────────────

class MacroSearchTool(BaseTool):
    name: str = "macro_search"
    description: str = (
        "Searches for macroeconomic, regulatory, or competitive threats relevant "
        "to a company or sector. Use this to identify risk catalysts."
    )
    args_schema: Type[BaseModel] = NewsSearchInput

    def _run(self, query: str, max_results: int = 6) -> str:
        risk_query = f"{query} risk regulation competition threat recession"
        news_tool = NewsSearchTool()
        return news_tool._run(query=risk_query, max_results=max_results)
