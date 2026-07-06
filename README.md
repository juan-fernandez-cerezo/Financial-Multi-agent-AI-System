# 📊 Financial Multi-agent-AI-system

A multi-agent AI system that acts as a small investment research desk: give it a stock ticker, and four collaborating AI agents pull financial data, scan the news, stress-test the bull case, and hand back a structured Markdown investment report with a Buy / Hold / Sell recommendation.

Built with **[CrewAI](https://crewai.com)**, **Google Gemini**, and **Yahoo Finance**.

> Educational project only. Nothing this system produces is financial advice. See [Disclaimer](#disclaimer).

---

## How it works

The four agents run as a **sequential pipeline**, each one handing its output forward as context to the next:

```
                    ┌───────────────────────────┐
   ticker  ────────►│  Fundamental Analyst       │
                    │  Yahoo Finance ratios,     │
                    │  price trend, valuation    │
                    └────────────┬──────────────┘
                                 │
                    ┌────────────▼──────────────┐
                    │  Sentiment Analyst         │
                    │  48h news search, catalyst │
                    │  detection, sentiment score│
                    └────────────┬──────────────┘
                                 │
                    ┌────────────▼──────────────┐
                    │  Risk Strategist           │
                    │  VALIDATION GATE — red-    │
                    │  teams both prior analyses,│
                    │  builds a scored risk      │
                    │  matrix, issues a verdict  │
                    └────────────┬──────────────┘
                                 │
                    ┌────────────▼──────────────┐
                    │  Report Writer             │
                    │  Synthesizes everything    │
                    │  into the final report and │
                    │  saves it to outputs/      │
                    └────────────────────────────┘
```

The **Risk Strategist** is the key design choice here: rather than letting an optimistic fundamental/sentiment read flow straight into a recommendation, it's explicitly prompted to challenge every bullish assumption and produce a Low/Medium/High/Critical risk matrix *before* the report is allowed to be written. If its verdict is unfavorable, the final recommendation is required to reflect that.

## Agent roster

| Agent | Role | Tools |
|---|---|---|
| **Fundamental Analyst** | Pulls financial statements & ratios, scores financial health | `fundamental_data`, `price_history` (Yahoo Finance) |
| **Sentiment Analyst** | Scans the last 48h of news for catalysts, scores sentiment | `news_search` (Tavily, or DuckDuckGo fallback) |
| **Risk Strategist** | Red-teams the prior two analyses, builds a risk matrix | `macro_search` |
| **Report Writer** | Synthesizes all outputs into the final report | `save_report` |

## Report structure

Every run produces a Markdown file with five sections:

```markdown
# {TICKER} Investment Research Report

## 1. Executive Summary
## 2. Fundamental Analysis
## 3. Market Sentiment & News Analysis
## 4. Risk Matrix
## 5. Final Recommendation   <- Buy / Hold / Sell + 12-month price target
```

Reports are saved to `outputs/{TICKER}_latest_report.md`.

## Two ways to run it

**CLI**

```bash
python main.py --ticker AAPL
```

**Streamlit dashboard** — includes a live pipeline view and lets you browse/download past reports

```bash
streamlit run dashboard.py
```

## Quick start

```bash
# 1. Clone & enter the project
git clone https://github.com/your-username/financial-research-agents.git
cd financial-research-agents

# 2. Create a virtual environment
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Configure API keys
cp .env.example .env
# Edit .env - add GOOGLE_API_KEY (required), TAVILY_API_KEY (optional)

# 5. Run
python main.py --ticker AAPL
```

## Configuration

| Variable | Required | Description |
|---|---|---|
| `GOOGLE_API_KEY` | Yes | Google AI Studio API key (powers the Gemini agents) |
| `GEMINI_MODEL_NAME` | No | Default: `gemini-2.0-flash` |
| `TAVILY_API_KEY` | No | Higher-quality news search (falls back to free DuckDuckGo search if unset) |
| `OUTPUT_DIR` | No | Default: `outputs/` |

## Project structure

```
financial-research-agents/
├── main.py                  # CLI entry point
├── dashboard.py              # Streamlit UI
├── requirements.txt
├── .env.example
├── config/
│   └── settings.py           # Central config & env vars
├── agents/
│   ├── fundamental_analyst.py
│   ├── sentiment_analyst.py
│   ├── risk_strategist.py
│   └── report_writer.py
├── tools/
│   ├── financial_tools.py     # Yahoo Finance wrappers
│   ├── search_tools.py        # Tavily / DuckDuckGo wrappers
│   └── report_tools.py        # Markdown save tool
├── tasks/
│   └── research_tasks.py      # Task graph, incl. the risk validation gate
├── crews/
│   └── financial_crew.py      # Crew assembly & sequential process
└── outputs/                   # Generated reports (gitignored)
```

## Roadmap

- [ ] **Vector memory** - ChromaDB so the Sentiment Analyst remembers news context across runs
- [ ] **Hallucination check** - Ragas evaluation module to verify financial data accuracy
- [ ] **Multi-ticker batch mode** - compare 3-5 tickers side by side
- [ ] **Scheduled reports** - cron/GitHub Actions for auto-generated weekly reports
- [ ] **Earnings calendar mode** - pre/post-earnings analysis

## Disclaimer

This system is for **educational and informational purposes only**. It does not constitute financial advice. Always conduct your own research before making investment decisions.
