"""Desktop automation agent coordinator with OpenAI integration.

This module implements the main agent that uses OpenAI's Responses API
to intelligently process and execute user commands.

Following Guido's design: Let OpenAI handle reasoning, we handle execution.
"""

import json
import logging
from typing import Any, Dict, List, Optional

from computer_use_agent.config.settings import get_settings
from computer_use_agent.core.desktop import VirtualDesktop
from computer_use_agent.models.task import Task, TaskStatus, TaskType
from computer_use_agent.openai_integration.client import OpenAIClient

logger = logging.getLogger(__name__)


class AgentStatistics:
    """Tracks agent performance statistics.

    Attributes:
        total_tasks: Total number of tasks processed.
        completed_tasks: Number of successfully completed tasks.
        failed_tasks: Number of failed tasks.
        total_execution_time: Cumulative execution time in seconds.
    """

    def __init__(self) -> None:
        """Initialize statistics counters."""
        self.total_tasks: int = 0
        self.completed_tasks: int = 0
        self.failed_tasks: int = 0
        self.total_execution_time: float = 0.0

    @property
    def success_rate(self) -> float:
        """Calculate the success rate percentage.

        Returns:
            Success rate as a percentage (0-100).
        """
        if self.total_tasks == 0:
            return 0.0
        return round((self.completed_tasks / self.total_tasks) * 100, 1)

    @property
    def average_execution_time(self) -> float:
        """Calculate average execution time per task.

        Returns:
            Average execution time in seconds.
        """
        if self.total_tasks == 0:
            return 0.0
        return round(self.total_execution_time / self.total_tasks, 3)


class DesktopAgent:
    """OpenAI-powered desktop automation agent.

    This agent uses OpenAI's Responses API to understand user commands
    and determine which tools to use. It handles the execution of those
    tools on the virtual desktop and provides results back to OpenAI.

    Architecture:
    1. User command → OpenAI (reasoning and tool selection)
    2. OpenAI tool calls → Desktop operations
    3. Operation results → Back to OpenAI
    4. Final response → User

    Attributes:
        desktop: Virtual desktop environment for execution.
        openai_client: Client for OpenAI Responses API.
        task_history: List of all processed tasks.
        statistics: Performance statistics tracker.
    """

    def __init__(
        self,
        desktop: Optional[VirtualDesktop] = None,
        openai_client: Optional[OpenAIClient] = None,
    ) -> None:
        """Initialize the desktop agent.

        Args:
            desktop: Optional pre-configured virtual desktop.
            openai_client: Optional pre-configured OpenAI client.

        Raises:
            ValueError: If OpenAI API key is not configured.
        """
        self.desktop = desktop or VirtualDesktop()

        if openai_client is None:
            settings = get_settings()
            if not settings.openai_api_key:
                raise ValueError(
                    'OpenAI API key is required. Set OPENAI_API_KEY environment variable.'
                )
            openai_client = OpenAIClient(
                api_key=settings.openai_api_key,
                model=settings.openai_model,
                organization=settings.openai_organization,
            )

        self.openai_client = openai_client
        self.task_history: List[Task] = []
        self.statistics = AgentStatistics()

        logger.info('DesktopAgent initialized with OpenAI integration')

    def process_command(self, command: str) -> Task:
        """Process a natural language command using OpenAI.

        OpenAI analyzes the command, determines which tools to use,
        and we execute those tools on the virtual desktop.

        Args:
            command: The user's natural language command.

        Returns:
            Task object with execution results.
        """
        logger.info(f'Processing command via OpenAI: {command}')

        task = Task(
            command=command,
            task_type=TaskType.WORKFLOW,  # Let OpenAI decide the actual operations
        )
        task.mark_started()

        try:
            # Get desktop state for OpenAI context
            desktop_state = self._format_desktop_state()

            # Send command to OpenAI
            response = self.openai_client.process_command(command, desktop_state)

            # Process OpenAI response
            message = response.choices[0].message

            # Handle tool calls if OpenAI wants to use tools
            if message.tool_calls:
                results = []
                for tool_call in message.tool_calls:
                    result = self._execute_tool(tool_call)
                    results.append(result)

                    # Add tool result to OpenAI conversation
                    self.openai_client.add_tool_result(
                        tool_call_id=tool_call.id,
                        function_name=tool_call.function.name,
                        result=result,
                    )

                # Compile all results
                task.result = ' | '.join(results)
                task.mark_completed(task.result)

            elif message.content:
                # OpenAI responded without using tools
                task.mark_completed(message.content)

            else:
                task.mark_failed('No response from OpenAI')

        except Exception as e:
            logger.exception('Error processing command with OpenAI')
            task.mark_failed(f'Error: {str(e)}')

        # Update history and statistics
        self.task_history.append(task)
        self._update_statistics(task)

        logger.info(
            f'Command processed - Status: {task.status.value}, '
            f'Execution time: {task.execution_time:.3f}s'
        )

        return task

    def _execute_tool(self, tool_call: Any) -> str:
        """Execute a tool call from OpenAI on the virtual desktop.

        Args:
            tool_call: Tool call object from OpenAI.

        Returns:
            Result message from tool execution.
        """
        function_name = tool_call.function.name
        arguments = json.loads(tool_call.function.arguments)

        logger.info(f'Executing tool: {function_name} with args: {arguments}')

        try:
            # Route to appropriate desktop operation
            if function_name == 'launch_application':
                return self._tool_launch_application(arguments)
            elif function_name == 'close_application':
                return self._tool_close_application(arguments)
            elif function_name == 'create_file':
                return self._tool_create_file(arguments)
            elif function_name == 'delete_file':
                return self._tool_delete_file(arguments)
            elif function_name == 'list_files':
                return self._tool_list_files(arguments)
            elif function_name == 'open_file':
                return self._tool_open_file(arguments)
            elif function_name == 'navigate_browser':
                return self._tool_navigate_browser(arguments)
            elif function_name == 'get_system_status':
                return self._tool_get_system_status(arguments)
            elif function_name == 'get_running_applications':
                return self._tool_get_running_applications(arguments)
            else:
                return f'Unknown tool: {function_name}'

        except Exception as e:
            logger.exception(f'Error executing tool {function_name}')
            return f'Error: {str(e)}'

    # Tool implementation methods

    def _tool_launch_application(self, args: Dict[str, Any]) -> str:
        """Launch an application."""
        app = args['application']
        if self.desktop.launch_application(app):
            return f'Launched {app} successfully'
        return f'Failed to launch {app}'

    def _tool_close_application(self, args: Dict[str, Any]) -> str:
        """Close an application."""
        app = args['application']
        if self.desktop.close_application(app):
            return f'Closed {app} successfully'
        return f'{app} was not running'

    def _tool_create_file(self, args: Dict[str, Any]) -> str:
        """Create a file."""
        filename = args['filename']
        directory = args.get('directory', 'documents')
        if self.desktop.create_file(filename, directory):
            return f'Created {filename} in {directory}'
        return f'File {filename} already exists in {directory}'

    def _tool_delete_file(self, args: Dict[str, Any]) -> str:
        """Delete a file."""
        filename = args['filename']
        directory = args.get('directory', 'documents')
        if self.desktop.delete_file(filename, directory):
            return f'Deleted {filename} from {directory}'
        return f'File {filename} not found in {directory}'

    def _tool_list_files(self, args: Dict[str, Any]) -> str:
        """List files in a directory."""
        directory = args['directory']
        files = self.desktop.list_files(directory)
        if files:
            return f'Files in {directory}: {", ".join(files)}'
        return f'No files in {directory}'

    def _tool_open_file(self, args: Dict[str, Any]) -> str:
        """Open a file."""
        filename = args['filename']
        directory = args.get('directory', 'documents')
        if self.desktop.file_exists(filename, directory):
            return f'Opened {filename} from {directory}'
        return f'File {filename} not found in {directory}'

    def _tool_navigate_browser(self, args: Dict[str, Any]) -> str:
        """Navigate browser."""
        # Ensure browser is running
        if 'browser' not in self.desktop.running_apps:
            self.desktop.launch_application('browser')

        if 'url' in args:
            return f'Navigated to {args["url"]}'
        elif 'search_query' in args:
            return f'Searched for "{args["search_query"]}"'
        return 'Opened browser'

    def _tool_get_system_status(self, args: Dict[str, Any]) -> str:
        """Get system status."""
        sys_info = self.desktop.update_system_info()
        component = args.get('component', 'all')

        if component == 'cpu':
            return f'CPU usage: {sys_info.cpu_usage}%'
        elif component == 'memory':
            return f'Memory usage: {sys_info.memory_usage}%'
        elif component == 'disk':
            return f'Disk usage: {sys_info.disk_usage}%'
        else:
            return (
                f'System Status - CPU: {sys_info.cpu_usage}%, '
                f'Memory: {sys_info.memory_usage}%, '
                f'Disk: {sys_info.disk_usage}%'
            )

    def _tool_get_running_applications(self, args: Dict[str, Any]) -> str:
        """Get running applications."""
        apps = self.desktop.get_running_applications()
        if apps:
            return f'Running applications: {", ".join(apps)}'
        return 'No applications running'

    def _format_desktop_state(self) -> str:
        """Format desktop state for OpenAI context.

        Returns:
            Formatted string describing desktop state.
        """
        state = self.desktop.get_state_summary()
        lines = []

        if state['running_applications']:
            lines.append(f"Running: {', '.join(state['running_applications'])}")
        else:
            lines.append('Running: none')

        lines.append(
            f"System: CPU {state['system_info']['cpu_usage']}%, "
            f"Memory {state['system_info']['memory_usage']}%"
        )

        return ' | '.join(lines)

    # Helper methods

    def process_batch(self, commands: List[str]) -> List[Task]:
        """Process multiple commands in sequence.

        Args:
            commands: List of natural language commands.

        Returns:
            List of executed tasks.
        """
        logger.info(f'Processing batch of {len(commands)} commands')
        tasks = [self.process_command(cmd) for cmd in commands]
        logger.info('Batch processing completed')
        return tasks

    def get_recent_tasks(self, count: int = 5) -> List[Task]:
        """Get the most recent tasks.

        Args:
            count: Number of recent tasks to return.

        Returns:
            List of recent tasks, most recent first.
        """
        return list(reversed(self.task_history[-count:]))

    def get_statistics_summary(self) -> Dict[str, Any]:
        """Get a summary of agent performance statistics.

        Returns:
            Dictionary containing performance metrics.
        """
        return {
            'total_tasks': self.statistics.total_tasks,
            'completed_tasks': self.statistics.completed_tasks,
            'failed_tasks': self.statistics.failed_tasks,
            'success_rate': self.statistics.success_rate,
            'average_execution_time': self.statistics.average_execution_time,
        }

    def get_desktop_state(self) -> Dict[str, Any]:
        """Get the current state of the virtual desktop.

        Returns:
            Dictionary containing desktop state information.
        """
        return self.desktop.get_state_summary()

    def _update_statistics(self, task: Task) -> None:
        """Update statistics based on task execution.

        Args:
            task: The completed task.
        """
        self.statistics.total_tasks += 1
        self.statistics.total_execution_time += task.execution_time

        if task.status == TaskStatus.COMPLETED:
            self.statistics.completed_tasks += 1
        elif task.status == TaskStatus.FAILED:
            self.statistics.failed_tasks += 1

    def reset_statistics(self) -> None:
        """Reset all statistics counters."""
        self.statistics = AgentStatistics()
        logger.info('Statistics reset')

    def clear_history(self) -> None:
        """Clear the task history and OpenAI conversation."""
        self.task_history.clear()
        self.openai_client.clear_history()
        logger.info('Task history and OpenAI conversation cleared')

    def display_dashboard(self) -> str:
        """Generate a formatted dashboard display.

        Returns:
            Formatted string with agent status and statistics.
        """
        stats = self.get_statistics_summary()
        state = self.get_desktop_state()

        lines = [
            '=' * 60,
            'OPENAI-POWERED DESKTOP AGENT DASHBOARD',
            '=' * 60,
            '',
            'STATISTICS:',
            f"  Total Tasks: {stats['total_tasks']}",
            f"  Completed: {stats['completed_tasks']}",
            f"  Failed: {stats['failed_tasks']}",
            f"  Success Rate: {stats['success_rate']}%",
            f"  Avg Execution Time: {stats['average_execution_time']}s",
            '',
            'DESKTOP STATE:',
            f"  Active Window: {state['active_window'] or 'None'}",
            f"  Running Apps: {', '.join(state['running_applications']) or 'None'}",
            f"  Mouse Position: {state['mouse_position']}",
            '',
            'SYSTEM INFO:',
            f"  CPU Usage: {state['system_info']['cpu_usage']}%",
            f"  Memory Usage: {state['system_info']['memory_usage']}%",
            f"  Disk Usage: {state['system_info']['disk_usage']}%",
            '',
            'OPENAI INFO:',
            f"  Conversation Messages: {self.openai_client.get_history_length()}",
            f"  Model: {self.openai_client.model}",
            '',
        ]

        # Add recent tasks
        recent_tasks = self.get_recent_tasks(3)
        if recent_tasks:
            lines.append('RECENT TASKS:')
            for i, task in enumerate(recent_tasks, 1):
                status_symbol = '✓' if task.status == TaskStatus.COMPLETED else '✗'
                lines.append(
                    f'  {i}. [{status_symbol}] {task.command[:45]} '
                    f'({task.execution_time:.3f}s)'
                )
            lines.append('')

        lines.append('=' * 60)

        return '\n'.join(lines)
