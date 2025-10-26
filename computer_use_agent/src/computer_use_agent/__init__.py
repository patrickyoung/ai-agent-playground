"""Computer Use Agent - A production-ready desktop automation agent.

This package provides an AI-powered agent that can understand natural language
commands and execute them in a simulated desktop environment.

The agent demonstrates:
- Natural language processing for command interpretation
- Task execution with multiple operation types
- Virtual desktop environment simulation
- Production-ready code structure with type hints and logging

Example:
    >>> from computer_use_agent import DesktopAgent
    >>> agent = DesktopAgent()
    >>> task = agent.process_command("open the browser")
    >>> print(task.result)
"""

from computer_use_agent.core.agent import DesktopAgent
from computer_use_agent.core.desktop import VirtualDesktop
from computer_use_agent.models.task import Task, TaskStatus, TaskType

__version__ = '1.0.0'
__author__ = 'Computer Use Agent Team'

__all__ = [
    'DesktopAgent',
    'VirtualDesktop',
    'Task',
    'TaskStatus',
    'TaskType',
]
