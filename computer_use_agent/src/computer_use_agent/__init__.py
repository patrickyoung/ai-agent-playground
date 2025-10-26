"""Computer Use Agent - OpenAI-powered desktop automation.

This package provides an intelligent agent powered by OpenAI's Responses API
that can understand natural language commands and execute them through
structured tool calling on a simulated desktop environment.

Key Features:
- OpenAI Responses API integration with tool calling
- Intelligent command understanding and task planning
- Virtual desktop environment for safe execution
- Production-ready code with full type hints
- Comprehensive logging and error handling

Example:
    >>> import os
    >>> os.environ['OPENAI_API_KEY'] = 'your-api-key'
    >>> from computer_use_agent import DesktopAgent
    >>> agent = DesktopAgent()
    >>> task = agent.process_command("open the browser and search for python")
    >>> print(task.result)

Architecture:
    User Command → OpenAI (reasoning) → Tool Selection → Desktop Execution → Results
"""

from computer_use_agent.core.agent import DesktopAgent
from computer_use_agent.core.desktop import VirtualDesktop
from computer_use_agent.models.task import Task, TaskStatus, TaskType
from computer_use_agent.openai_integration.client import OpenAIClient

__version__ = '2.0.0'
__author__ = 'Computer Use Agent Team'

__all__ = [
    'DesktopAgent',
    'VirtualDesktop',
    'Task',
    'TaskStatus',
    'TaskType',
    'OpenAIClient',
]
