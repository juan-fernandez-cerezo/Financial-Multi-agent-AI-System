"""
Streamlit Dashboard — Financial Research Crew
=============================================
Run with:
    streamlit run dashboard.py
"""
import sys
import threading
import queue
from pathlib import Path
from datetime import datetime

import streamlit as st

sys.path.insert(0, str(Path(__file__).parent))

from config.settings import OUTPUT_DIR

# ── Page config ────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="AI Financial Research Crew",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Sidebar ────────────────────────────────────────────────────────────────────
with st.sidebar:
    st.title("📊 AI Research Crew")
    st.markdown("---")
    ticker_input = st.text_input(
        "Enter Ticker Symbol",
        placeholder="e.g. AAPL, NVDA, MSFT",
        max_chars=10,
    ).strip().upper()

    run_button = st.button("🚀 Generate Report", use_container_width=True, type="primary")

    st.markdown("---")
    st.markdown("### Agent Pipeline")
    st.markdown(
        "1. 📈 **Fundamental Analyst**\n"
        "2. 📰 **Sentiment Analyst**\n"
        "3. 🛡️ **Risk Strategist** *(validation gate)*\n"
        "4. ✍️ **Report Writer**"
    )

    st.markdown("---")
    st.markdown("### Previous Reports")
    reports = sorted(OUTPUT_DIR.glob("*.md"), key=lambda p: p.stat().st_mtime, reverse=True)
    for rpt in reports[:5]:
        if st.button(f"📄 {rpt.name}", use_container_width=True):
            st.session_state["preview_report"] = rpt

# ── Main area ──────────────────────────────────────────────────────────────────
st.title("AI Financial Research System")
st.caption("Multi-agent investment research powered by CrewAI")

# Status containers
status_placeholder   = st.empty()
progress_placeholder = st.empty()
log_placeholder      = st.container()
report_placeholder   = st.empty()

# Show a previously selected report
if "preview_report" in st.session_state:
    rpt = st.session_state["preview_report"]
    st.markdown("---")
    st.subheader(f"📄 {rpt.stem}")
    st.markdown(rpt.read_text(encoding="utf-8"))

# ── Run pipeline ───────────────────────────────────────────────────────────────
if run_button and ticker_input:
    st.session_state.pop("preview_report", None)

    log_queue: "queue.Queue[str]" = queue.Queue()
    result_holder: dict = {}

    def run_crew():
        from crews.financial_crew import run_financial_research
        try:
            result = run_financial_research(ticker_input)
            result_holder["output"] = result
            result_holder["error"]  = None
        except Exception as e:
            result_holder["output"] = None
            result_holder["error"]  = str(e)

    thread = threading.Thread(target=run_crew, daemon=True)
    thread.start()

    agent_steps = [
        ("📈", "Fundamental Analyst",  "Reading balance sheets and computing ratios…"),
        ("📰", "Sentiment Analyst",    "Searching 48-hour news and scoring catalysts…"),
        ("🛡️", "Risk Strategist",     "Challenging bull case — building risk matrix…"),
        ("✍️", "Report Writer",        "Synthesizing report and saving Markdown file…"),
    ]

    progress_bar = progress_placeholder.progress(0, text="Pipeline starting…")

    for i, (icon, name, desc) in enumerate(agent_steps):
        if not thread.is_alive() and i > 0:
            break
        pct = int((i / len(agent_steps)) * 100)
        progress_bar.progress(pct, text=f"{icon} {name}: {desc}")
        with log_placeholder:
            with st.status(f"{icon} {name}", state="running", expanded=(i == len(agent_steps)-1)):
                st.write(desc)
        thread.join(timeout=120)

    thread.join()
    progress_bar.progress(100, text="✅ Pipeline complete!")

    if result_holder.get("error"):
        st.error(f"Pipeline error: {result_holder['error']}")
    else:
        # Find the latest report for this ticker
        ticker_reports = sorted(
            OUTPUT_DIR.glob(f"{ticker_input}_*.md"),
            key=lambda p: p.stat().st_mtime,
            reverse=True,
        )
        latest = OUTPUT_DIR / f"{ticker_input}_latest_report.md"

        with report_placeholder.container():
            st.markdown("---")
            st.success(f"Report generated for **{ticker_input}**")

            col1, col2 = st.columns([3, 1])
            with col1:
                st.subheader(f"📊 {ticker_input} Investment Research Report")
            with col2:
                if latest.exists():
                    st.download_button(
                        "⬇️ Download .md",
                        data=latest.read_text(encoding="utf-8"),
                        file_name=latest.name,
                        mime="text/markdown",
                        use_container_width=True,
                    )

            if latest.exists():
                st.markdown(latest.read_text(encoding="utf-8"))
            else:
                st.markdown(str(result_holder["output"]))

elif run_button and not ticker_input:
    st.warning("Please enter a ticker symbol in the sidebar.")

else:
    st.info("Enter a ticker symbol in the sidebar and click **Generate Report** to begin.")
    st.markdown(
        """
        ### How it works
        | Step | Agent | Action |
        |------|-------|--------|
        | 1 | 📈 Fundamental Analyst | Pulls Yahoo Finance data, computes P/E, ROE, Debt/EBITDA |
        | 2 | 📰 Sentiment Analyst   | Searches 48-hour news, identifies catalysts |
        | 3 | 🛡️ Risk Strategist    | **Validation gate** — builds risk matrix, challenges bull case |
        | 4 | ✍️ Report Writer       | Synthesizes everything into a structured Markdown report |
        """
    )
