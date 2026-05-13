#!/usr/bin/env python3
"""
Initialize the database with topics and keywords from the config file.
"""

import sqlite3
from pathlib import Path

import typer
import yaml
from rich.console import Console

from rdt.shared.database import init_db

console = Console()


def init_topics_and_keywords(config_file: str, db_path: str):
    """
    Populates the topics and keywords tables from the config file.
    """
    init_db(db_path)

    try:
        with open(config_file, "r", encoding="utf-8") as f:
            config = yaml.safe_load(f)
    except Exception as e:
        console.print(f"[error]Error loading config file '{config_file}': {e}[/error]")
        raise typer.Exit(1)

    topics = config.get("topics", {})
    if not topics:
        console.print("[warning]No topics found in the config file.[/warning]")
        return

    with sqlite3.connect(db_path) as conn:
        cursor = conn.cursor()

        for topic_name, keywords in topics.items():
            try:
                cursor.execute(
                    "INSERT OR IGNORE INTO topics (name) VALUES (?)", (topic_name,)
                )
                topic_id = cursor.lastrowid
                if topic_id == 0:
                    cursor.execute(
                        "SELECT id FROM topics WHERE name = ?", (topic_name,)
                    )
                    topic_id = cursor.fetchone()[0]

                for keyword in keywords:
                    cursor.execute(
                        "INSERT OR IGNORE INTO keywords (topic_id, keyword) VALUES (?, ?)",
                        (topic_id, keyword),
                    )
                console.print(
                    f"Topic '{topic_name}' and its keywords have been added to the database."
                )
            except sqlite3.IntegrityError as e:
                console.print(
                    f"[error]Error inserting topic '{topic_name}': {e}[/error]"
                )
                continue

        conn.commit()


def main(
    config: str = typer.Option(
        "research_config.yaml",
        "--config",
        "-c",
        help="Config file path",
    ),
    db_path: str = typer.Option(
        "research_digest_state.db",
        "--db-path",
        "-db",
        help="Database path",
    ),
):
    """
    Initialize the database with topics and keywords from the config file.
    """
    if not Path(config).exists():
        console.print(f"[error]Error: Config file '{config}' not found.[/error]")
        raise typer.Exit(1)

    init_topics_and_keywords(config, db_path)


if __name__ == "__main__":
    typer.run(main)
