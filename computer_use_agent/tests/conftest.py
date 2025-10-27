"""Pytest configuration and shared fixtures.

This module provides common test fixtures and configuration.
"""

import pytest

from computer_use_agent.core.agent import DesktopAgent
from computer_use_agent.core.desktop import VirtualDesktop


@pytest.fixture
def desktop():
    """Provide a fresh VirtualDesktop instance for tests.

    Returns:
        A new VirtualDesktop instance.
    """
    return VirtualDesktop()


@pytest.fixture
def agent():
    """Provide a fresh DesktopAgent instance for tests.

    Returns:
        A new DesktopAgent instance with clean state.
    """
    return DesktopAgent()
