"""Desktop automation agent coordinator.

This module implements the main agent that coordinates all components
to process and execute user commands.
"""

import logging
from typing import Dict, List, Optional

from computer_use_agent.core.desktop import VirtualDesktop
from computer_use_agent.executors.task_executor import TaskExecutor
from computer_use_agent.models.task import Task, TaskStatus
from computer_use_agent.processors.nlp_processor import NLPProcessor

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
    """Main agent coordinator for desktop automation.

    The DesktopAgent orchestrates the entire automation pipeline:
    1. Accepts natural language commands from users
    2. Uses NLP processor to extract intent and parameters
    3. Delegates execution to the task executor
    4. Maintains history and statistics

    Attributes:
        desktop: Virtual desktop environment.
        nlp_processor: Natural language processor.
        task_executor: Task execution engine.
        task_history: List of all processed tasks.
        statistics: Performance statistics tracker.
    """

    def __init__(self, desktop: Optional[VirtualDesktop] = None) -> None:
        """Initialize the desktop agent.

        Args:
            desktop: Optional pre-configured virtual desktop.
                    If not provided, a new one is created.
        """
        self.desktop = desktop or VirtualDesktop()
        self.nlp_processor = NLPProcessor()
        self.task_executor = TaskExecutor(self.desktop)
        self.task_history: List[Task] = []
        self.statistics = AgentStatistics()

        logger.info('DesktopAgent initialized successfully')

    def process_command(self, command: str) -> Task:
        """Process a natural language command.

        This is the main entry point for executing user commands.
        The command is analyzed, executed, and the task is returned
        with updated status and results.

        Args:
            command: The natural language command to process.

        Returns:
            The executed task with results.
        """
        logger.info(f'Processing command: {command}')

        # Analyze command to create task
        task = self.nlp_processor.analyze_command(command)

        # Execute the task
        self.task_executor.execute(task)

        # Update history and statistics
        self.task_history.append(task)
        self._update_statistics(task)

        logger.info(
            f'Command processed - Status: {task.status.value}, '
            f'Execution time: {task.execution_time:.3f}s'
        )

        return task

    def process_batch(self, commands: List[str]) -> List[Task]:
        """Process multiple commands in sequence.

        Args:
            commands: List of natural language commands.

        Returns:
            List of executed tasks.
        """
        logger.info(f'Processing batch of {len(commands)} commands')
        tasks = [self.process_command(cmd) for cmd in commands]
        logger.info(f'Batch processing completed')
        return tasks

    def get_recent_tasks(self, count: int = 5) -> List[Task]:
        """Get the most recent tasks.

        Args:
            count: Number of recent tasks to return.

        Returns:
            List of recent tasks, most recent first.
        """
        return list(reversed(self.task_history[-count:]))

    def get_statistics_summary(self) -> Dict[str, any]:
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

    def get_desktop_state(self) -> Dict[str, any]:
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
        """Clear the task history."""
        self.task_history.clear()
        logger.info('Task history cleared')

    def display_dashboard(self) -> str:
        """Generate a formatted dashboard display.

        Returns:
            Formatted string with agent status and statistics.
        """
        stats = self.get_statistics_summary()
        state = self.get_desktop_state()

        lines = [
            '=' * 60,
            'DESKTOP AGENT DASHBOARD',
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
        ]

        # Add recent tasks
        recent_tasks = self.get_recent_tasks(3)
        if recent_tasks:
            lines.append('RECENT TASKS:')
            for i, task in enumerate(recent_tasks, 1):
                status_symbol = '✓' if task.status == TaskStatus.COMPLETED else '✗'
                lines.append(
                    f'  {i}. [{status_symbol}] {task.command[:50]} '
                    f'({task.execution_time:.3f}s)'
                )
            lines.append('')

        lines.append('=' * 60)

        return '\n'.join(lines)
