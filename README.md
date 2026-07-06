# 📊 AI Financial Research Crew

> A production-ready **multi-agent system** that acts as a full investment research team, analyzing any stock ticker and generating a structured Markdown report with Buy / Hold / Sell recommendations.

Built with **[CrewAI](https://crewai.com)**, **Yahoo Finance**, and **GPT-4o**.

---

## Architecture

```
main.py / dashboard.py
        │
        ▼
 Financial Research Crew (Sequential)
        │
        ├─► 📈 Fundamental Analyst
        │       └─ Tools: YahooFinance, PriceHistory
        │
        ├─► 📰 Sentiment Analyst
        │       └─ Tools: NewsSearch (Tavily / DuckDuckGo)
        │
        ├─► 🛡️ Risk Strategist  ← VALIDATION GATE
        │       └─ Tools: MacroSearch
        │       └─ Context: outputs from agents 1 & 2
        │
        └─► ✍️ Report Writer
                └─ Tools: SaveReport
                └─ Context: outputs from all 3 agents
                └─ Output: outputs/{TICKER}_latest_report.md
```

## Agent Roster

| Agent | Role | Key Tools |
|-------|------|-----------|
| **Fundamental Analyst** | CFA-level financial metrics analysis | `yfinance`, P/E, ROE, Debt/EBITDA |
| **Sentiment Analyst** | 48-hour news & catalyst detection | Tavily / DuckDuckGo Search |
| **Risk Strategist** | Red-team validation gate | MacroSearch, Risk Matrix |
| **Report Writer** | Professional Markdown synthesis | SaveReport |

## Report Structure

```markdown
# {TICKER} Investment Research Report

## 1. Executive Summary
## 2. Fundamental Analysis
## 3. Market Sentiment & News Analysis
## 4. Risk Matrix
## 5. Final Recommendation  ← Buy / Hold / Sell + Price Target
```

---

## Quick Start

```bash
# 1. Clone & enter project
git clone https://github.com/your-username/financial-research-agents.git
cd financial-research-agents

# 2. Create virtual environment
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Configure API keys
cp .env.example .env
# Edit .env — add OPENAI_API_KEY (required) and TAVILY_API_KEY (optional)

# 5. Run CLI
python main.py --ticker AAPL

# 6. Run Streamlit Dashboard
streamlit run dashboard.py
```

---

## Configuration

| Variable | Required | Description |
|----------|----------|-------------|
| `OPENAI_API_KEY` | ✅ Yes | OpenAI API key |
| `OPENAI_MODEL_NAME` | No | Default: `gpt-4o-mini` |
| `TAVILY_API_KEY` | No | Better news search (falls back to DuckDuckGo) |
| `OUTPUT_DIR` | No | Default: `outputs/` |

---

## Roadmap — "Vitaminas" 🚀

- [ ] **Vector Memory** — ChromaDB integration so the Sentiment Analyst remembers news context across runs (`crews/financial_crew.py` → `memory=True`)
- [ ] **Hallucination Check** — Ragas evaluation module to verify financial data accuracy
- [ ] **Multi-ticker Batch** — Compare 3-5 tickers side by side
- [ ] **Scheduled Reports** — GitHub Actions cron to auto-generate weekly reports
- [ ] **Earnings Calendar** — Pre-earnings and post-earnings analysis modes

---

## Project Structure

```
financial-research-agents/
├── main.py                 # CLI entry point
├── dashboard.py            # Streamlit UI
├── requirements.txt
├── .env.example
├── config/
│   └── settings.py         # Central config & env vars
├── agents/
│   ├── fundamental_analyst.py
│   ├── sentiment_analyst.py
│   ├── risk_strategist.py
│   └── report_writer.py
├── tools/
│   ├── financial_tools.py  # Yahoo Finance wrappers
│   ├── search_tools.py     # Tavily / DuckDuckGo
│   └── report_tools.py     # Markdown save
├── tasks/
│   └── research_tasks.py   # Task graph with validation gate
├── crews/
│   └── financial_crew.py   # Crew assembly
└── outputs/                # Generated reports (gitignored)
```

---

## Disclaimer

This system is for **educational and informational purposes only**. It does not constitute financial advice. Always conduct your own research before making investment decisions.
