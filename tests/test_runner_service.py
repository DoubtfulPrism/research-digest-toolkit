#!/usr/bin/env python3
"""Unit tests for RunnerService."""

import sys
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest
import yaml

sys.path.insert(0, str(Path(__file__).parent.parent))


@pytest.mark.unit
def test_runner_service_builds_correct_command(tmp_path):
    """run_scraper builds the correct subprocess command."""
    from research_digest_tui.services.runner_service import RunnerService

    config_path = tmp_path / "config.yaml"
    svc = RunnerService(config_path)

    lines = []
    completed = []

    mock_proc = MagicMock()
    mock_proc.stdout = iter([])
    mock_proc.wait.return_value = 0

    with patch(
        "research_digest_tui.services.runner_service.subprocess.Popen"
    ) as mock_popen:
        mock_popen.return_value = mock_proc
        svc.run_scraper("hackernews", lines.append, completed.append)

        mock_popen.assert_called_once()
        cmd = mock_popen.call_args[0][0]
        assert "research_digest.py" in cmd
        assert "--config" in cmd
        assert str(config_path) in cmd
        assert "--scraper" in cmd
        assert "hackernews" in cmd


@pytest.mark.unit
def test_runner_service_streams_lines_to_callback(tmp_path):
    """run_scraper calls on_line for each output line from the process."""
    from research_digest_tui.services.runner_service import RunnerService

    config_path = tmp_path / "config.yaml"
    svc = RunnerService(config_path)

    received_lines = []
    mock_proc = MagicMock()
    mock_proc.stdout = iter(["line one\n", "line two\n", "line three\n"])
    mock_proc.wait.return_value = 0

    with patch(
        "research_digest_tui.services.runner_service.subprocess.Popen"
    ) as mock_popen:
        mock_popen.return_value = mock_proc
        svc.run_scraper("rss", received_lines.append, lambda _: None)

    assert received_lines == ["line one", "line two", "line three"]


@pytest.mark.unit
def test_runner_service_calls_on_complete_true_on_success(tmp_path):
    """run_scraper calls on_complete(True) when the process exits with 0."""
    from research_digest_tui.services.runner_service import RunnerService

    config_path = tmp_path / "config.yaml"
    svc = RunnerService(config_path)

    complete_results = []
    mock_proc = MagicMock()
    mock_proc.stdout = iter([])
    mock_proc.wait.return_value = 0

    with patch(
        "research_digest_tui.services.runner_service.subprocess.Popen"
    ) as mock_popen:
        mock_popen.return_value = mock_proc
        svc.run_scraper("arxiv", lambda _: None, complete_results.append)

    assert complete_results == [True]


@pytest.mark.unit
def test_runner_service_calls_on_complete_false_on_failure(tmp_path):
    """run_scraper calls on_complete(False) when the process exits non-zero."""
    from research_digest_tui.services.runner_service import RunnerService

    config_path = tmp_path / "config.yaml"
    svc = RunnerService(config_path)

    complete_results = []
    mock_proc = MagicMock()
    mock_proc.stdout = iter([])
    mock_proc.wait.return_value = 1

    with patch(
        "research_digest_tui.services.runner_service.subprocess.Popen"
    ) as mock_popen:
        mock_popen.return_value = mock_proc
        svc.run_scraper("rss", lambda _: None, complete_results.append)

    assert complete_results == [False]


@pytest.mark.unit
def test_research_digest_scraper_flag_filters_scrapers(tmp_path):
    """--scraper flag causes run_scrapers to skip all non-matching scrapers."""
    config_data = {
        "scrapers": {
            "hackernews": {"enabled": True, "min_points": 50, "search_topics": []},
            "rss": {"enabled": True, "feeds": []},
        },
        "output": {"base_dir": "research_digest"},
        "processing": {},
        "topics": {},
        "formats": {},
        "report": {},
    }
    config_file = tmp_path / "config.yaml"
    config_file.write_text(yaml.dump(config_data))

    from research_digest import ResearchDigest

    digest = ResearchDigest(str(config_file), verbose=False)

    # Replace with mock scrapers whose names match config keys
    hn_scraper = MagicMock()
    hn_scraper.name = "hackernews"
    rss_scraper = MagicMock()
    rss_scraper.name = "rss"
    digest.scrapers = [hn_scraper, rss_scraper]

    output_dir = tmp_path / "output"
    output_dir.mkdir()

    digest.run_scrapers(output_dir, target_scraper="rss")

    hn_scraper.run.assert_not_called()
    rss_scraper.run.assert_called_once()
