"""
Task definitions for the Financial Research Crew.

Flow (sequential with explicit context passing):
  1. fundamental_analysis_task
  2. sentiment_analysis_task
  3. risk_validation_task      ← gate: reads output of tasks 1 & 2
  4. report_writing_task       ← only runs after risk validation is complete
"""
from datetime import datetime
from crewai import Task

from agents.fundamental_analyst import build_fundamental_analyst
from agents.sentiment_analyst    import build_sentiment_analyst
from agents.risk_strategist      import build_risk_strategist
from agents.report_writer        import build_report_writer


def build_tasks(ticker: str) -> list[Task]:
    ticker = ticker.upper()
    today  = datetime.now().strftime("%B %d, %Y")

    # ── Agents ─────────────────────────────────────────────────────────────────
    fundamental_agent = build_fundamental_analyst()
    sentiment_agent   = build_sentiment_analyst()
    risk_agent        = build_risk_strategist()
    writer_agent      = build_report_writer()

    # ── Task 1: Fundamental Analysis ───────────────────────────────────────────
    fundamental_task = Task(
        description=(
            f"Perform a comprehensive fundamental analysis of **{ticker}** as of {today}.\n\n"
            "1. Use the `fundamental_data` tool to retrieve all financial metrics.\n"
            "2. Use the `price_history` tool to retrieve the 6-month price trend.\n"
            "3. Calculate and interpret:\n"
            "   - Valuation: P/E (trailing & forward), Price/Sales, EV/EBITDA\n"
            "   - Profitability: ROE, ROA, Gross & Operating Margins\n"
            "   - Leverage: Debt/Equity, Debt/EBITDA — flag if > 3x\n"
            "   - Cash generation: Free Cash Flow yield\n"
            "4. Compare these metrics to the sector median where possible.\n"
            "5. Provide a final Fundamental Score: STRONG / FAIR / WEAK with justification."
        ),
        expected_output=(
            "A structured Markdown section with all computed ratios, a comparison "
            "to sector benchmarks, key strengths and weaknesses, and a Fundamental Score."
        ),
        agent=fundamental_agent,
    )

    # ── Task 2: Sentiment & News Analysis ──────────────────────────────────────
    sentiment_task = Task(
        description=(
            f"Conduct a 48-hour news sentiment analysis for **{ticker}** as of {today}.\n\n"
            "1. Use `news_search` with query: '{ticker} stock news earnings analyst'\n"
            "2. Use `news_search` again with query: '{ticker} company latest update'\n"
            "3. Synthesize all findings:\n"
            "   - Overall Sentiment: BULLISH / NEUTRAL / BEARISH\n"
            "   - List up to 5 **Positive Catalysts** with source and date\n"
            "   - List up to 5 **Negative Catalysts** with source and date\n"
            "   - Identify if there is unusual analyst activity (upgrades/downgrades)\n"
            "4. Assign a Sentiment Score from -5 (extremely bearish) to +5 (extremely bullish)."
        ),
        expected_output=(
            "A structured Markdown section with overall sentiment label, scored catalysts "
            "(positive and negative), sourced headlines, and a numerical Sentiment Score."
        ),
        agent=sentiment_agent,
    )

    # ── Task 3: Risk Validation (Gate) ─────────────────────────────────────────
    # This task receives context from BOTH previous tasks, making it a validation gate.
    risk_task = Task(
        description=(
            f"You are the FINAL GATE before the report is published for **{ticker}**.\n\n"
            "You have received:\n"
            "- The Fundamental Analysis (Task 1 output)\n"
            "- The Sentiment Analysis (Task 2 output)\n\n"
            "Your mandate:\n"
            "1. Use `macro_search` to research: '{ticker} regulatory risk antitrust competition 2025'\n"
            "2. Use `macro_search` to research: 'macroeconomic risk interest rates recession sector impact'\n"
            "3. Actively CHALLENGE the bullish assumptions in the prior analyses.\n"
            "4. Produce a **Risk Matrix** with the following categories (scored Low/Medium/High/Critical):\n"
            "   | Risk Category          | Score    | Description |\n"
            "   |------------------------|----------|-------------|\n"
            "   | Macroeconomic Risk     | ...      | ...         |\n"
            "   | Regulatory/Legal Risk  | ...      | ...         |\n"
            "   | Competitive Disruption | ...      | ...         |\n"
            "   | Management/Governance  | ...      | ...         |\n"
            "   | Valuation Risk         | ...      | ...         |\n"
            "   | Liquidity/Balance Sheet| ...      | ...         |\n\n"
            "5. Write a 'Bear Case' paragraph: what needs to go wrong for the stock to drop >20%.\n"
            "6. Conclude with a RISK VERDICT: ACCEPTABLE / ELEVATED / UNACCEPTABLE.\n"
            "   If UNACCEPTABLE, explain why the report should carry a SELL bias regardless of fundamentals.\n\n"
            "⚠️ DO NOT skip any risk category. An incomplete risk matrix = failed validation."
        ),
        expected_output=(
            "A complete Risk Matrix table (all 6 categories scored), a Bear Case scenario, "
            "a list of 3-5 key risk items the Writer MUST reference, and a RISK VERDICT."
        ),
        agent=risk_agent,
        context=[fundamental_task, sentiment_task],  # ← validation gate
    )

    # ── Task 4: Report Writing ──────────────────────────────────────────────────
    report_task = Task(
        description=(
            f"Synthesize all research into a final investment report for **{ticker}**.\n\n"
            "You have received validated outputs from:\n"
            "- Fundamental Analyst (Task 1)\n"
            "- Sentiment Analyst (Task 2)\n"
            "- Risk Strategist — VALIDATED (Task 3)\n\n"
            "Write the report using EXACTLY this Markdown structure:\n\n"
            "```\n"
            "# {ticker} Investment Research Report\n"
            "**Date:** {today} | **Analyst Team:** AI Research Crew\n\n"
            "---\n\n"
            "## 1. Executive Summary\n"
            "[3-4 sentences: company overview, key investment thesis, recommendation]\n\n"
            "## 2. Fundamental Analysis\n"
            "[Full content from Task 1 — ratios, score, comparison]\n\n"
            "## 3. Market Sentiment & News Analysis\n"
            "[Full content from Task 2 — catalysts, sentiment score]\n\n"
            "## 4. Risk Matrix\n"
            "[Full Risk Matrix table from Task 3 + Bear Case]\n\n"
            "## 5. Final Recommendation\n"
            "**Rating:** BUY / HOLD / SELL\n"
            "**12-Month Price Target:** $XXX (X% upside/downside)\n"
            "**Conviction Level:** HIGH / MEDIUM / LOW\n\n"
            "[2-3 paragraphs justifying the recommendation, explicitly addressing the\n"
            "risk verdict from the Risk Strategist. If risks are ELEVATED, the rating\n"
            "conviction must be reduced accordingly.]\n\n"
            "---\n"
            "*Disclaimer: This report is generated by an AI research system for\n"
            "informational purposes only and does not constitute financial advice.*\n"
            "```\n\n"
            "After writing, use the `save_report` tool with ticker='{ticker}' "
            "and the full report content."
        ),
        expected_output=(
            f"A complete, professional Markdown investment report for {ticker} "
            "saved to the outputs/ directory, with all 5 sections populated "
            "and a clear Buy/Hold/Sell recommendation with price target."
        ),
        agent=writer_agent,
        context=[fundamental_task, sentiment_task, risk_task],
        output_file=f"outputs/{ticker}_latest_report.md",
    )

    return [fundamental_task, sentiment_task, risk_task, report_task]
