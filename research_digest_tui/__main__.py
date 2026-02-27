#!/usr/bin/env python3
"""Entry point for running Research Digest TUI as a module."""

from .app import ResearchDigestApp

if __name__ == "__main__":
    app = ResearchDigestApp()
    app.run()
