"""OpenAI client wrapper for Responses API.

This module provides a clean interface to OpenAI's Responses API,
handling authentication, tool calling, and response processing.

Following Guido's principles:
- Explicit configuration over implicit defaults
- Clear error messages
- Type-safe interfaces
"""

import logging
import time
from typing import Any, Dict, List, Optional

from openai import APIError, OpenAI, RateLimitError
from openai.types.chat import ChatCompletion, ChatCompletionMessage

from computer_use_agent.openai_integration.tools import get_desktop_tools

logger = logging.getLogger(__name__)

# Maximum number of messages to keep in conversation history
MAX_HISTORY_MESSAGES = 20

# Rate limit retry configuration
MAX_RETRIES = 3
INITIAL_RETRY_DELAY = 2  # seconds


class OpenAIClient:
    """Client for interacting with OpenAI's Responses API.

    This client wraps the OpenAI API with desktop automation-specific
    functionality, handling tool definitions and response parsing.

    Attributes:
        client: The OpenAI client instance.
        model: The model to use for completions.
        tools: Desktop operation tool definitions.
        conversation_history: Message history for context.
    """

    def __init__(
        self,
        api_key: str,
        model: str = 'gpt-4o',
        organization: Optional[str] = None,
    ) -> None:
        """Initialize the OpenAI client.

        Args:
            api_key: OpenAI API key for authentication.
            model: Model name to use (default: gpt-4o for tool calling).
            organization: Optional organization ID.

        Raises:
            ValueError: If api_key is empty or None.
        """
        # Validate API key
        if not api_key:
            raise ValueError('OpenAI API key is required')

        if not api_key.startswith('sk-'):
            raise ValueError(
                'OpenAI API key must start with "sk-". '
                'Get your key at https://platform.openai.com/api-keys'
            )

        # Initialize client
        try:
            self.client = OpenAI(api_key=api_key, organization=organization)
        except Exception as e:
            raise ValueError(f'Failed to initialize OpenAI client: {e}') from e

        self.model = model
        self.tools = get_desktop_tools()
        self.conversation_history: List[Dict[str, Any]] = []

        logger.info(f'OpenAI client initialized with model: {model}')

    def process_command(
        self, command: str, system_context: Optional[str] = None
    ) -> ChatCompletion:
        """Process a user command through OpenAI.

        Sends the command to OpenAI with tool definitions, allowing the model
        to reason about which tools to call and in what sequence.

        Args:
            command: The user's natural language command.
            system_context: Optional system context about desktop state.

        Returns:
            ChatCompletion response from OpenAI.
        """
        logger.info(f'Processing command: {command}')

        # Build messages
        messages: List[Dict[str, Any]] = []

        # Add system message with desktop context
        system_message = self._build_system_message(system_context)
        messages.append({'role': 'system', 'content': system_message})

        # Trim conversation history to prevent context overflow
        self._trim_history()

        # Add conversation history for context
        messages.extend(self.conversation_history)

        # Add user command
        messages.append({'role': 'user', 'content': command})

        # Call OpenAI with tools (with retry logic for rate limits)
        try:
            response = self._call_openai_with_retry(messages)

            # Update conversation history
            self.conversation_history.append({'role': 'user', 'content': command})

            # Add complete assistant response to history (including tool_calls if present)
            assistant_message = response.choices[0].message
            history_entry: Dict[str, Any] = {
                'role': 'assistant',
                'content': assistant_message.content,
            }

            # CRITICAL: Include tool calls in history if present
            if assistant_message.tool_calls:
                history_entry['tool_calls'] = [
                    {
                        'id': tc.id,
                        'type': 'function',
                        'function': {
                            'name': tc.function.name,
                            'arguments': tc.function.arguments,
                        },
                    }
                    for tc in assistant_message.tool_calls
                ]

            self.conversation_history.append(history_entry)

            logger.info('Command processed successfully')
            return response

        except Exception as e:
            logger.exception('Error calling OpenAI API')
            raise

    def _build_system_message(self, context: Optional[str] = None) -> str:
        """Build the system message with desktop automation context.

        Args:
            context: Optional additional context about current desktop state.

        Returns:
            System message string.
        """
        base_message = (
            'You are a desktop automation agent. Your purpose is to help users '
            'automate tasks on their virtual desktop environment. '
            '\n\n'
            'You have access to the following capabilities:\n'
            '- Launch and close applications (browser, text editor, file manager, email, terminal)\n'
            '- Create, delete, open, and list files in directories\n'
            '- Navigate browser to URLs or perform web searches\n'
            '- Check system resource usage (CPU, memory, disk)\n'
            '- Get list of running applications\n'
            '\n'
            'When a user gives you a command:\n'
            '1. Analyze what they want to accomplish\n'
            '2. Determine which tools to use\n'
            '3. Call the appropriate tools in the right sequence\n'
            '4. Provide clear feedback about what was done\n'
            '\n'
            'Always be helpful, accurate, and efficient.'
        )

        if context:
            base_message += f'\n\nCurrent desktop state:\n{context}'

        return base_message

    def _call_openai_with_retry(self, messages: List[Dict[str, Any]]) -> ChatCompletion:
        """Call OpenAI API with exponential backoff retry for rate limits.

        Args:
            messages: List of conversation messages.

        Returns:
            ChatCompletion response from OpenAI.

        Raises:
            RateLimitError: If max retries exceeded.
            APIError: If API call fails for non-rate-limit reasons.
        """
        for attempt in range(MAX_RETRIES):
            try:
                response = self.client.chat.completions.create(
                    model=self.model,
                    messages=messages,
                    tools=self.tools,
                    tool_choice='auto',
                )

                # Log token usage
                if response.usage:
                    logger.info(
                        f'OpenAI usage: {response.usage.total_tokens} tokens '
                        f'(prompt: {response.usage.prompt_tokens}, '
                        f'completion: {response.usage.completion_tokens})'
                    )

                return response

            except RateLimitError as e:
                if attempt == MAX_RETRIES - 1:
                    logger.error('Max retries exceeded for rate limit')
                    raise

                wait_time = INITIAL_RETRY_DELAY * (2**attempt)  # Exponential backoff
                logger.warning(
                    f'Rate limited (attempt {attempt + 1}/{MAX_RETRIES}), '
                    f'waiting {wait_time}s before retry'
                )
                time.sleep(wait_time)

            except APIError as e:
                logger.error(f'OpenAI API error: {e}')
                raise

    def _trim_history(self) -> None:
        """Trim conversation history to prevent context window overflow.

        Keeps only the most recent messages up to MAX_HISTORY_MESSAGES.
        This prevents hitting OpenAI's context length limits.
        """
        if len(self.conversation_history) > MAX_HISTORY_MESSAGES:
            messages_to_remove = len(self.conversation_history) - MAX_HISTORY_MESSAGES
            logger.info(
                f'Trimming conversation history: removing {messages_to_remove} '
                f'old messages (keeping last {MAX_HISTORY_MESSAGES})'
            )
            self.conversation_history = self.conversation_history[-MAX_HISTORY_MESSAGES:]

    def add_tool_result(
        self, tool_call_id: str, function_name: str, result: str
    ) -> None:
        """Add a tool execution result to conversation history.

        This allows OpenAI to see the results of tool calls and continue
        the conversation with that context.

        Args:
            tool_call_id: ID of the tool call from OpenAI.
            function_name: Name of the function that was called.
            result: Result message from the tool execution.
        """
        self.conversation_history.append(
            {
                'role': 'tool',
                'tool_call_id': tool_call_id,
                'name': function_name,
                'content': result,
            }
        )

    def clear_history(self) -> None:
        """Clear the conversation history.

        Useful for starting fresh or preventing context window overflow.
        """
        self.conversation_history.clear()
        logger.info('Conversation history cleared')

    def get_history_length(self) -> int:
        """Get the number of messages in conversation history.

        Returns:
            Number of messages in history.
        """
        return len(self.conversation_history)
