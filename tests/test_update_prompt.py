#!/usr/bin/env python3
"""Tests for the UpdatePrompt TUI modal screen."""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest


@pytest.mark.unit
def test_update_prompt_displays_versions():
    """UpdatePrompt renders both local and remote version strings."""
    from rdt.tui.screens.update_prompt import UpdatePrompt

    screen = UpdatePrompt(local_version="1.0.2", remote_version="1.1.0")
    # Verify the screen stores the version info for rendering
    assert screen.local_version == "1.0.2"
    assert screen.remote_version == "1.1.0"


@pytest.mark.unit
def test_update_prompt_has_required_attributes():
    """UpdatePrompt stores version info and can be instantiated cleanly."""
    from rdt.tui.screens.update_prompt import UpdatePrompt

    screen = UpdatePrompt(local_version="1.0.2", remote_version="1.1.0")
    # Verify the screen is a ModalScreen subclass with version data
    from textual.screen import ModalScreen

    assert isinstance(screen, ModalScreen)
    assert screen.local_version == "1.0.2"
    assert screen.remote_version == "1.1.0"


@pytest.mark.unit
def test_update_prompt_skip_action():
    """Pressing Skip calls dismiss on the modal."""
    from rdt.tui.screens.update_prompt import UpdatePrompt

    screen = UpdatePrompt(local_version="1.0.2", remote_version="1.1.0")
    screen.dismiss = MagicMock()
    screen.action_skip()
    screen.dismiss.assert_called_once()
