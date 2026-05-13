"""Tests that verify shared modules are importable from the rdt.tui package."""

import pytest


@pytest.mark.unit
def test_config_models_importable_from_package():
    from rdt.shared.config_models import ResearchDigestConfig  # noqa: F401


@pytest.mark.unit
def test_rich_utils_importable_from_package():
    from rdt.shared.rich_utils import get_console  # noqa: F401


@pytest.mark.unit
def test_scheduler_utils_importable_from_package():
    from rdt.shared.scheduler_utils import ScheduleError  # noqa: F401


@pytest.mark.unit
def test_scheduler_utils_uses_package_internal_rich_import():
    """scheduler_utils must import print_info from the package rich_utils, not top-level."""
    from rdt.shared.rich_utils import print_info as ru_print_info
    from rdt.shared.scheduler_utils import print_info as su_print_info

    assert su_print_info is ru_print_info
