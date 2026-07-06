"""Assembles and runs the Financial Research Crew."""
from crewai import Crew, Process

from tasks.research_tasks import build_tasks


def run_financial_research(ticker: str) -> str:
    """
    Kick off the multi-agent financial research pipeline.

    Args:
        ticker: Stock ticker symbol (e.g. 'AAPL', 'NVDA')

    Returns:
        Final report content as a string.
    """
    tasks = build_tasks(ticker)

    # Agents are derived from tasks to keep a single source of truth
    agents = [task.agent for task in tasks]

    crew = Crew(
        agents=agents,
        tasks=tasks,
        process=Process.sequential,   # tasks run in order; context flows forward
        verbose=True,
        memory=False,                 # set True + configure embedder for ChromaDB extension
        max_rpm=10,                   # rate-limit LLM calls
        share_crew=False,
    )

    result = crew.kickoff(inputs={"ticker": ticker.upper()})
    return str(result)
