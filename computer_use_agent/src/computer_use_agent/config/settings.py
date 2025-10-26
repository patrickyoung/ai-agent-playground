"""Application settings and configuration.

This module defines configuration settings for the agent system.
Following the principle of explicit configuration.
"""

import os
from dataclasses import dataclass
from pathlib import Path
from typing import Optional


@dataclass
class Settings:
    """Application configuration settings.

    Attributes:
        openai_api_key: OpenAI API key for authentication.
        openai_model: Model to use for completions.
        openai_organization: Optional OpenAI organization ID.
        log_level: Logging verbosity level.
        log_file: Optional path to log file.
        enable_console_log: Whether to log to console.
        max_task_history: Maximum number of tasks to keep in history.
        simulation_delay: Delay in seconds to simulate processing.
    """

    openai_api_key: str = ''
    openai_model: str = 'gpt-4o'
    openai_organization: Optional[str] = None
    log_level: str = 'INFO'
    log_file: Optional[Path] = None
    enable_console_log: bool = True
    max_task_history: int = 100
    simulation_delay: float = 0.1

    @classmethod
    def from_env(cls) -> 'Settings':
        """Create settings from environment variables.

        Environment variables:
            OPENAI_API_KEY: OpenAI API key (required)
            OPENAI_MODEL: Model to use (default: gpt-4o)
            OPENAI_ORGANIZATION: Optional organization ID
            AGENT_LOG_LEVEL: Logging level (DEBUG, INFO, WARNING, ERROR)
            AGENT_LOG_FILE: Path to log file
            AGENT_CONSOLE_LOG: Enable console logging (true/false)
            AGENT_MAX_HISTORY: Maximum task history size
            AGENT_SIM_DELAY: Simulation delay in seconds

        Returns:
            Settings instance with values from environment or defaults.
        """
        log_file_str = os.getenv('AGENT_LOG_FILE')
        log_file = Path(log_file_str) if log_file_str else None

        return cls(
            openai_api_key=os.getenv('OPENAI_API_KEY', ''),
            openai_model=os.getenv('OPENAI_MODEL', 'gpt-4o'),
            openai_organization=os.getenv('OPENAI_ORGANIZATION'),
            log_level=os.getenv('AGENT_LOG_LEVEL', 'INFO').upper(),
            log_file=log_file,
            enable_console_log=os.getenv('AGENT_CONSOLE_LOG', 'true').lower()
            == 'true',
            max_task_history=int(os.getenv('AGENT_MAX_HISTORY', '100')),
            simulation_delay=float(os.getenv('AGENT_SIM_DELAY', '0.1')),
        )


# Global settings instance
_settings: Optional[Settings] = None


def get_settings() -> Settings:
    """Get the global settings instance.

    Returns:
        The application settings. Creates from environment on first call.
    """
    global _settings
    if _settings is None:
        _settings = Settings.from_env()
    return _settings
