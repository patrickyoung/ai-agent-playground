"""OpenAI Responses API integration.

This module provides integration with OpenAI's Responses API, including
tool definitions for desktop operations and the client wrapper.
"""

from computer_use_agent.openai_integration.client import OpenAIClient
from computer_use_agent.openai_integration.tools import get_desktop_tools

__all__ = ['OpenAIClient', 'get_desktop_tools']
