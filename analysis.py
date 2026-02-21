#!/usr/bin/env python3
"""
Analyze topic occurrences over time.
"""

import typer
import polars as pl
from rich.console import Console

from database import get_connection

app = typer.Typer(help="Analyze topic occurrences over time.")
console = Console()


def analyze_topic_trends(db_path: str):
    """
    Analyzes topic occurrences over time and prints a summary table.
    """
    with get_connection(db_path) as conn:
        try:
            df = pl.read_database(
                "SELECT t.name, o.date FROM topic_occurrences o JOIN topics t ON o.topic_id = t.id",
                conn,
            )

            if df.is_empty():
                console.print("[warning]No topic occurrences found in the database.[/warning]")
                return

            df = df.with_columns(pl.col("date").str.to_datetime())
            df = df.group_by("name").agg(pl.count("date").alias("occurrences"))
            df = df.sort("occurrences", descending=True)

            console.print(df)

        except Exception as e:
            console.print(f"[error]Error analyzing topic trends: {e}[/error]")
            raise typer.Exit(1)


@app.command()
def main(
    db_path: str = typer.Option(
        "research_digest_state.db",
        "--db-path",
        "-db",
        help="Database path",
    ),
):
    """
    Analyze topic occurrences over time.
    """
    analyze_topic_trends(db_path)


if __name__ == "__main__":
    app()
