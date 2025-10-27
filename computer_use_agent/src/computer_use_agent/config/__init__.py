"""Configuration management for the computer use agent.

This module provides configuration settings and logging setup.
"""

from computer_use_agent.config.logging_config import setup_logging
from computer_use_agent.config.settings import Settings, get_settings

__all__ = ['setup_logging', 'Settings', 'get_settings']
