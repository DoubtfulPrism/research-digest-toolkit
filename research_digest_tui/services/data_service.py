#!/usr/bin/env python3
"""DataService — Polars-powered SQLite queries for TUI screens."""

import sqlite3
from datetime import datetime, timedelta, timezone
from pathlib import Path

import polars as pl


class DataService:
    """Queries the research_digest_state.db SQLite database via Polars."""

    def __init__(self, db_path: Path) -> None:
        self._db_path = db_path

    def _conn(self) -> sqlite3.Connection | None:
        """Open a SQLite connection, returning None if file is missing."""
        if not self._db_path.exists():
            return None
        return sqlite3.connect(str(self._db_path))

    def _days_filter_clause(self, days: int | None) -> str:
        """Return a WHERE clause fragment filtering processed_at to last N days."""
        if days is None:
            return ""
        cutoff = (datetime.now(timezone.utc) - timedelta(days=days)).strftime(
            "%Y-%m-%dT%H:%M:%S"
        )
        return f" WHERE processed_at >= '{cutoff}'"

    def get_item_counts_by_source(self) -> dict[str, int]:
        """Return total item count per source from the database."""
        conn = self._conn()
        if conn is None:
            return {}
        try:
            df = pl.read_database(
                "SELECT source, COUNT(*) AS count FROM processed_items GROUP BY source",
                conn,
            )
            if df.is_empty():
                return {}
            return dict(zip(df["source"].to_list(), df["count"].to_list()))
        except Exception:
            return {}
        finally:
            conn.close()

    def get_items_timeline(
        self, source_filter: str | None = None, limit: int = 100
    ) -> list[dict]:
        """Return chronological list of processed items, most recent first."""
        conn = self._conn()
        if conn is None:
            return []
        try:
            if source_filter:
                query = (
                    f"SELECT source, unique_id, processed_at FROM processed_items "
                    f"WHERE source = '{source_filter}' "
                    f"ORDER BY processed_at DESC LIMIT {limit}"
                )
            else:
                query = (
                    f"SELECT source, unique_id, processed_at FROM processed_items "
                    f"ORDER BY processed_at DESC LIMIT {limit}"
                )
            df = pl.read_database(query, conn)
            if df.is_empty():
                return []
            return df.to_dicts()
        except Exception:
            return []
        finally:
            conn.close()

    def get_daily_counts(self, days: int = 7) -> list[dict]:
        """Return item counts per day for the last N days."""
        conn = self._conn()
        if conn is None:
            return []
        try:
            cutoff = (datetime.now(timezone.utc) - timedelta(days=days)).strftime(
                "%Y-%m-%dT%H:%M:%S"
            )
            query = (
                f"SELECT SUBSTR(processed_at, 1, 10) AS date, COUNT(*) AS count "
                f"FROM processed_items WHERE processed_at >= '{cutoff}' "
                f"GROUP BY date ORDER BY date DESC"
            )
            df = pl.read_database(query, conn)
            if df.is_empty():
                return []
            return df.to_dicts()
        except Exception:
            return []
        finally:
            conn.close()

    def get_summary_stats(self, days: int | None = None) -> dict:
        """Return summary statistics: total_items, source_count, date_range, avg_per_day."""
        conn = self._conn()
        if conn is None:
            return {
                "total_items": 0,
                "source_count": 0,
                "date_range": "No data",
                "avg_per_day": 0.0,
            }
        try:
            where = self._days_filter_clause(days)
            df = pl.read_database(
                f"SELECT source, processed_at FROM processed_items{where}", conn
            )
            if df.is_empty():
                return {
                    "total_items": 0,
                    "source_count": 0,
                    "date_range": "No data",
                    "avg_per_day": 0.0,
                }

            total = len(df)
            source_count = df["source"].n_unique()
            min_date = df["processed_at"].min()
            max_date = df["processed_at"].max()
            date_range = f"{str(min_date)[:10]} – {str(max_date)[:10]}"

            # Compute avg per day
            try:
                d_min = datetime.fromisoformat(str(min_date).replace("Z", "+00:00"))
                d_max = datetime.fromisoformat(str(max_date).replace("Z", "+00:00"))
                day_span = max((d_max - d_min).days, 1)
                avg_per_day = round(total / day_span, 1)
            except Exception:
                avg_per_day = float(total)

            return {
                "total_items": total,
                "source_count": source_count,
                "date_range": date_range,
                "avg_per_day": avg_per_day,
            }
        except Exception:
            return {
                "total_items": 0,
                "source_count": 0,
                "date_range": "No data",
                "avg_per_day": 0.0,
            }
        finally:
            conn.close()

    def get_source_distribution(self, days: int | None = None) -> list[dict]:
        """Return source distribution with count and percentage."""
        conn = self._conn()
        if conn is None:
            return []
        try:
            where = self._days_filter_clause(days)
            df = pl.read_database(
                f"SELECT source, COUNT(*) AS count FROM processed_items{where} GROUP BY source ORDER BY count DESC",
                conn,
            )
            if df.is_empty():
                return []
            total = df["count"].sum()
            if total == 0:
                return []
            result = []
            for row in df.to_dicts():
                pct = round(row["count"] / total * 100, 2)
                result.append(
                    {"source": row["source"], "count": row["count"], "percentage": pct}
                )
            return result
        except Exception:
            return []
        finally:
            conn.close()
