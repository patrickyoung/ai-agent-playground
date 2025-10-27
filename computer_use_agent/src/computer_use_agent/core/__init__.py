"""Core components of the computer use agent.

This module contains the fundamental building blocks including the virtual
desktop environment and main agent coordinator.
"""

from computer_use_agent.core.desktop import VirtualDesktop
from computer_use_agent.core.agent import DesktopAgent

__all__ = ['VirtualDesktop', 'DesktopAgent']
