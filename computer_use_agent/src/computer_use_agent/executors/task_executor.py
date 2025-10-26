"""Task execution engine.

This module implements the execution logic for different types of tasks
in the virtual desktop environment.
"""

import logging
import time
from typing import List

from computer_use_agent.core.desktop import VirtualDesktop
from computer_use_agent.models.task import Task, TaskType, TaskStatus

logger = logging.getLogger(__name__)


class TaskExecutor:
    """Executes tasks in the virtual desktop environment.

    The executor translates high-level task commands into specific
    actions on the virtual desktop, handling different task types
    with appropriate execution strategies.

    Attributes:
        desktop: The virtual desktop environment to operate on.
    """

    def __init__(self, desktop: VirtualDesktop) -> None:
        """Initialize the task executor.

        Args:
            desktop: The virtual desktop environment.
        """
        self.desktop = desktop

    def execute(self, task: Task) -> None:
        """Execute a task in the virtual desktop.

        Args:
            task: The task to execute. Task status and result are updated.
        """
        task.mark_started()
        logger.info(f'Executing task {task.task_id}: {task.command}')

        try:
            # Add small delay to simulate processing
            time.sleep(0.1)

            # Route to appropriate handler based on task type
            if task.task_type == TaskType.FILE_OPERATION:
                self._execute_file_operation(task)
            elif task.task_type == TaskType.BROWSER_ACTION:
                self._execute_browser_action(task)
            elif task.task_type == TaskType.SYSTEM_COMMAND:
                self._execute_system_command(task)
            elif task.task_type == TaskType.APPLICATION_TASK:
                self._execute_application_task(task)
            elif task.task_type == TaskType.WORKFLOW:
                self._execute_workflow(task)
            else:
                task.mark_failed(f'Unknown task type: {task.task_type}')

        except Exception as e:
            logger.exception(f'Task {task.task_id} failed with exception')
            task.mark_failed(f'Execution error: {str(e)}')

    def _execute_file_operation(self, task: Task) -> None:
        """Execute file operations.

        Args:
            task: The file operation task to execute.
        """
        action = task.parameters.get('action', '')
        filename = task.parameters.get('filename', '')
        directory = task.parameters.get('directory', 'documents')

        if action in ('open', 'read'):
            if self.desktop.file_exists(filename, directory):
                task.mark_completed(
                    f'Opened {filename} from {directory} directory'
                )
            else:
                task.mark_failed(f'File {filename} not found in {directory}')

        elif action == 'create':
            if filename:
                if self.desktop.create_file(filename, directory):
                    task.mark_completed(
                        f'Created {filename} in {directory} directory'
                    )
                else:
                    task.mark_failed(f'File {filename} already exists')
            else:
                task.mark_failed('No filename specified')

        elif action == 'delete':
            if self.desktop.delete_file(filename, directory):
                task.mark_completed(
                    f'Deleted {filename} from {directory} directory'
                )
            else:
                task.mark_failed(f'File {filename} not found')

        elif action in ('list', 'show'):
            files = self.desktop.list_files(directory)
            if files:
                file_list = ', '.join(files)
                task.mark_completed(
                    f'Files in {directory}: {file_list}'
                )
            else:
                task.mark_completed(f'No files found in {directory}')

        else:
            task.mark_failed(f'Unknown file action: {action}')

    def _execute_browser_action(self, task: Task) -> None:
        """Execute browser actions.

        Args:
            task: The browser action task to execute.
        """
        action = task.parameters.get('action', '')
        url = task.parameters.get('url', '')
        query = task.parameters.get('query', '')

        if action in ('open', 'navigate'):
            if url:
                # Ensure browser is running
                if 'browser' not in self.desktop.running_apps:
                    self.desktop.launch_application('browser')

                task.mark_completed(f'Navigated to {url} in browser')
            else:
                task.mark_failed('No URL specified')

        elif action == 'search':
            if query:
                # Ensure browser is running
                if 'browser' not in self.desktop.running_apps:
                    self.desktop.launch_application('browser')

                task.mark_completed(f'Searched for "{query}" in browser')
            else:
                task.mark_failed('No search query specified')

        elif action == 'close':
            if 'browser' in self.desktop.running_apps:
                self.desktop.close_application('browser')
                task.mark_completed('Closed browser')
            else:
                task.mark_failed('Browser is not running')

        else:
            # Default to opening browser
            self.desktop.launch_application('browser')
            if query:
                task.mark_completed(f'Opened browser and searched for "{query}"')
            else:
                task.mark_completed('Opened browser')

    def _execute_system_command(self, task: Task) -> None:
        """Execute system commands.

        Args:
            task: The system command task to execute.
        """
        component = task.parameters.get('component', 'status')

        # Update system info
        sys_info = self.desktop.update_system_info()

        if component in ('cpu', 'system', 'status'):
            result = (
                f'System Status - '
                f'CPU: {sys_info.cpu_usage}%, '
                f'Memory: {sys_info.memory_usage}%, '
                f'Disk: {sys_info.disk_usage}%'
            )
            task.mark_completed(result)

        elif component == 'memory':
            task.mark_completed(f'Memory usage: {sys_info.memory_usage}%')

        elif component == 'disk':
            task.mark_completed(f'Disk usage: {sys_info.disk_usage}%')

        else:
            task.mark_completed(f'Checked {component} status')

    def _execute_application_task(self, task: Task) -> None:
        """Execute application tasks.

        Args:
            task: The application task to execute.
        """
        action = task.parameters.get('action', '')
        app_name = task.parameters.get('application', '')

        if action in ('open', 'launch', 'start', 'run'):
            if app_name and app_name in self.desktop.applications:
                if self.desktop.launch_application(app_name):
                    task.mark_completed(f'Launched {app_name}')
                else:
                    task.mark_failed(f'Failed to launch {app_name}')
            else:
                task.mark_failed(f'Unknown application: {app_name}')

        elif action in ('close', 'quit', 'exit', 'stop'):
            if app_name and app_name in self.desktop.applications:
                if self.desktop.close_application(app_name):
                    task.mark_completed(f'Closed {app_name}')
                else:
                    task.mark_failed(f'{app_name} is not running')
            else:
                task.mark_failed(f'Unknown application: {app_name}')

        else:
            task.mark_failed(f'Unknown application action: {action}')

    def _execute_workflow(self, task: Task) -> None:
        """Execute workflow tasks (batch operations).

        Args:
            task: The workflow task to execute.
        """
        # For workflow tasks, we simulate a multi-step process
        steps: List[str] = []

        # Example workflow: launch multiple apps
        for app_name in ['browser', 'text_editor', 'file_manager']:
            if app_name not in self.desktop.running_apps:
                self.desktop.launch_application(app_name)
                steps.append(f'Launched {app_name}')

        if steps:
            result = 'Workflow completed: ' + '; '.join(steps)
            task.mark_completed(result)
        else:
            task.mark_completed('Workflow completed: No actions needed')
