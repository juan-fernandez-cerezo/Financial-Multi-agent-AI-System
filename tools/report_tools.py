"""Tool that persists the final Markdown report to disk."""
from __future__ import annotations

import re
from datetime import datetime
from pathlib import Path
from typing import Type

from pydantic import BaseModel, Field
from crewai.tools import BaseTool

from config.settings import OUTPUT_DIR


class SaveReportInput(BaseModel):
    ticker: str = Field(..., description="Company ticker symbol")
    content: str = Field(..., description="Full Markdown content of the report")


class SaveReportTool(BaseTool):
    name: str = "save_report"
    description: str = (
        "Saves the final investment research report as a Markdown file in the "
        "outputs/ directory. Call this as the last step of the report writer."
    )
    args_schema: Type[BaseModel] = SaveReportInput

    def _run(self, ticker: str, content: str) -> str:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{ticker.upper()}_{timestamp}_report.md"
        filepath = OUTPUT_DIR / filename

        filepath.write_text(content, encoding="utf-8")
        return f"Report saved: {filepath}"
