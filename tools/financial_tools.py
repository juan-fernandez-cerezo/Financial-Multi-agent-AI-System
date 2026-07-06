"""Yahoo Finance tools — wrapped as CrewAI BaseTool for agent use."""
from __future__ import annotations

from typing import Type
import yfinance as yf
import pandas as pd
from pydantic import BaseModel, Field
from crewai.tools import BaseTool


# ── Input schemas ──────────────────────────────────────────────────────────────

class TickerInput(BaseModel):
    ticker: str = Field(..., description="Stock ticker symbol, e.g. AAPL")


# ── Tools ──────────────────────────────────────────────────────────────────────

class FundamentalDataTool(BaseTool):
    name: str = "fundamental_data"
    description: str = (
        "Fetches key fundamental financial data for a given ticker from Yahoo Finance. "
        "Returns income statement, balance sheet, cash flow metrics and key ratios."
    )
    args_schema: Type[BaseModel] = TickerInput

    def _run(self, ticker: str) -> str:
        try:
            stock = yf.Ticker(ticker.upper())
            info = stock.info

            # ── Key ratios ────────────────────────────────────────────────────
            pe_ratio      = info.get("trailingPE", "N/A")
            forward_pe    = info.get("forwardPE", "N/A")
            roe           = info.get("returnOnEquity", "N/A")
            roa           = info.get("returnOnAssets", "N/A")
            debt_equity   = info.get("debtToEquity", "N/A")
            ebitda        = info.get("ebitda", "N/A")
            total_debt    = info.get("totalDebt", "N/A")
            revenue       = info.get("totalRevenue", "N/A")
            net_income    = info.get("netIncomeToCommon", "N/A")
            free_cashflow = info.get("freeCashflow", "N/A")
            gross_margins = info.get("grossMargins", "N/A")
            op_margins    = info.get("operatingMargins", "N/A")
            market_cap    = info.get("marketCap", "N/A")
            price         = info.get("currentPrice", "N/A")
            52w_high      = info.get("fiftyTwoWeekHigh", "N/A")
            52w_low       = info.get("fiftyTwoWeekLow", "N/A")
            beta          = info.get("beta", "N/A")
            dividend_yield = info.get("dividendYield", "N/A")
            sector        = info.get("sector", "N/A")
            industry      = info.get("industry", "N/A")

            # ── Debt/EBITDA (manual calc) ──────────────────────────────────────
            try:
                debt_ebitda = round(float(total_debt) / float(ebitda), 2)
            except (TypeError, ZeroDivisionError):
                debt_ebitda = "N/A"

            # ── Format helpers ─────────────────────────────────────────────────
            def fmt_pct(v):
                return f"{round(float(v)*100, 2)}%" if v != "N/A" else "N/A"

            def fmt_b(v):
                return f"${round(float(v)/1e9, 2)}B" if v != "N/A" else "N/A"

            return f"""
## Fundamental Data — {ticker.upper()}

**Company Profile**
- Sector: {sector}
- Industry: {industry}
- Market Cap: {fmt_b(market_cap)}

**Valuation**
- Current Price: ${price}
- 52W High / Low: ${52w_high} / ${52w_low}
- Trailing P/E: {pe_ratio}
- Forward P/E: {forward_pe}
- Beta: {beta}
- Dividend Yield: {fmt_pct(dividend_yield)}

**Profitability**
- ROE: {fmt_pct(roe)}
- ROA: {fmt_pct(roa)}
- Gross Margin: {fmt_pct(gross_margins)}
- Operating Margin: {fmt_pct(op_margins)}

**Financial Health**
- Total Revenue: {fmt_b(revenue)}
- Net Income: {fmt_b(net_income)}
- EBITDA: {fmt_b(ebitda)}
- Free Cash Flow: {fmt_b(free_cashflow)}
- Total Debt: {fmt_b(total_debt)}
- Debt/Equity: {debt_equity}
- **Debt/EBITDA: {debt_ebitda}x**
"""
        except Exception as e:
            return f"Error fetching fundamental data for {ticker}: {e}"


class PriceHistoryTool(BaseTool):
    name: str = "price_history"
    description: str = (
        "Returns 6-month price history and moving average context for a ticker."
    )
    args_schema: Type[BaseModel] = TickerInput

    def _run(self, ticker: str) -> str:
        try:
            stock = yf.Ticker(ticker.upper())
            hist = stock.history(period="6mo")

            if hist.empty:
                return f"No price history found for {ticker}."

            current = round(hist["Close"].iloc[-1], 2)
            ma50    = round(hist["Close"].tail(50).mean(), 2)
            ma200   = round(hist["Close"].mean(), 2)
            vol_avg = round(hist["Volume"].mean(), 0)
            chg_6m  = round((current / hist["Close"].iloc[0] - 1) * 100, 2)

            trend = "BULLISH (price > MA50 > MA200)" if current > ma50 > ma200 else \
                    "BEARISH (price < MA50)" if current < ma50 else "MIXED"

            return f"""
## Price Context — {ticker.upper()}

- Current: ${current}
- 50-Day MA: ${ma50}
- 200-Day MA: ${ma200}
- 6-Month Change: {chg_6m}%
- Avg Daily Volume: {int(vol_avg):,}
- Trend Signal: **{trend}**
"""
        except Exception as e:
            return f"Error fetching price history for {ticker}: {e}"
