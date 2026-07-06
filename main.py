#!/usr/bin/env python3
"""
Financial Research Multi-Agent System
======================================
Entry point — run from project root:

    python main.py --ticker AAPL
    python main.py --ticker NVDA --verbose
"""
import argparse
import sys
from pathlib import Path

from rich.console import Console
from rich.panel import Panel
from rich.text import Text

# Ensure project root is on the path
sys.path.insert(0, str(Path(__file__).parent))

from crews.financial_crew import run_financial_research
from config.settings import OUTPUT_DIR

console = Console()


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="AI-powered financial research report generator",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python main.py --ticker AAPL
  python main.py --ticker NVDA
  python main.py --ticker MSFT
        """,
    )
    parser.add_argument(
        "--ticker", "-t",
        type=str,
        required=True,
        help="Stock ticker symbol (e.g. AAPL, NVDA, MSFT)",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    ticker = args.ticker.strip().upper()

    console.print(
        Panel(
            Text.from_markup(
                f"[bold cyan]Financial Research Crew[/bold cyan]\n"
                f"Analyzing: [bold yellow]{ticker}[/bold yellow]\n"
                f"Output directory: [dim]{OUTPUT_DIR}[/dim]"
            ),
            title="[bold]AI Investment Research System[/bold]",
            border_style="cyan",
        )
    )

    console.print(f"\n[bold green]▶ Starting research pipeline for {ticker}...[/bold green]\n")

    try:
        result = run_financial_research(ticker)

        console.print(
            Panel(
                f"[bold green]✓ Research complete![/bold green]\n\n"
                f"Report saved to: [cyan]{OUTPUT_DIR}/{ticker}_latest_report.md[/cyan]\n\n"
                f"[dim]Final crew output preview:[/dim]\n{str(result)[:500]}...",
                title="[bold]Pipeline Complete[/bold]",
                border_style="green",
            )
        )

    except KeyboardInterrupt:
        console.print("\n[yellow]Research interrupted by user.[/yellow]")
        sys.exit(0)
    except Exception as e:
        console.print(f"\n[bold red]Pipeline error:[/bold red] {e}")
        raise


if __name__ == "__main__":
    main()
