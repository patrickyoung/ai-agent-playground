"""Natural language command processor.

This module analyzes user commands to extract intent, task type,
and relevant parameters using pattern matching.
"""

import re
from typing import Dict, List, Optional, Tuple

from computer_use_agent.models.task import Task, TaskType


class NLPProcessor:
    """Processes natural language commands to extract structured task information.

    The processor uses pattern matching to identify task types and extract
    parameters from user commands. It assigns confidence scores to indicate
    the reliability of the interpretation.

    Attributes:
        patterns: Dictionary mapping task types to regex patterns.
    """

    def __init__(self) -> None:
        """Initialize the NLP processor with pattern definitions."""
        self.patterns: Dict[TaskType, List[str]] = {
            TaskType.FILE_OPERATION: [
                r'(open|create|delete|list|find|show)\s+(file|document|folder)',
                r'(open|read|edit|save|remove)\s+([a-zA-Z0-9_\-\.]+\.\w+)',
                r'(list|show)\s+(files|documents|folders)',
            ],
            TaskType.BROWSER_ACTION: [
                r'(open|navigate|go to|visit|browse)\s+(http|https|www)',
                r'(search|google|look up|find)\s+(.+)',
                r'(open|close|refresh)\s+(tab|browser|window)',
            ],
            TaskType.SYSTEM_COMMAND: [
                r'(check|show|display|get)\s+(system|cpu|memory|disk|status)',
                r'(shutdown|restart|sleep|hibernate)',
                r'(check|show)\s+(time|date|calendar)',
            ],
            TaskType.APPLICATION_TASK: [
                r'(open|launch|start|run)\s+(application|app|program)',
                r'(close|quit|exit|stop)\s+(application|app|program)',
                r'(open|launch)\s+([a-zA-Z]+\s?(editor|browser|mail|email))',
            ],
            TaskType.WORKFLOW: [
                r'(automate|run|execute)\s+(workflow|sequence|batch)',
                r'(perform|execute|do)\s+(multiple|several|batch)',
            ],
        }

    def analyze_command(self, command: str) -> Task:
        """Analyze a natural language command and create a task.

        Args:
            command: The user's natural language command.

        Returns:
            A Task object with extracted type, parameters, and confidence.
        """
        command_lower = command.lower().strip()

        # Identify task type and confidence
        task_type, confidence = self._identify_task_type(command_lower)

        # Extract parameters based on task type
        parameters = self._extract_parameters(command_lower, task_type)

        # Create and return task
        task = Task(
            command=command,
            task_type=task_type,
            confidence=confidence,
            parameters=parameters,
        )

        return task

    def _identify_task_type(self, command: str) -> Tuple[TaskType, float]:
        """Identify the task type from a command.

        Args:
            command: The lowercase command text.

        Returns:
            Tuple of (TaskType, confidence_score).
        """
        best_match: Optional[TaskType] = None
        best_confidence = 0.0

        for task_type, pattern_list in self.patterns.items():
            for pattern in pattern_list:
                match = re.search(pattern, command)
                if match:
                    # Calculate confidence based on match quality
                    match_length = len(match.group(0))
                    command_length = len(command)
                    confidence = min(0.95, (match_length / command_length) * 1.2)

                    if confidence > best_confidence:
                        best_confidence = confidence
                        best_match = task_type

        # Default to workflow with low confidence if no match
        if best_match is None:
            return TaskType.WORKFLOW, 0.3

        return best_match, round(best_confidence, 2)

    def _extract_parameters(
        self, command: str, task_type: TaskType
    ) -> Dict[str, str]:
        """Extract parameters from command based on task type.

        Args:
            command: The lowercase command text.
            task_type: The identified task type.

        Returns:
            Dictionary of extracted parameters.
        """
        parameters: Dict[str, str] = {}

        if task_type == TaskType.FILE_OPERATION:
            parameters.update(self._extract_file_params(command))
        elif task_type == TaskType.BROWSER_ACTION:
            parameters.update(self._extract_browser_params(command))
        elif task_type == TaskType.SYSTEM_COMMAND:
            parameters.update(self._extract_system_params(command))
        elif task_type == TaskType.APPLICATION_TASK:
            parameters.update(self._extract_application_params(command))

        # Extract common action verb
        action_match = re.search(
            r'^(open|close|create|delete|search|check|show|list|run|execute|start|stop)',
            command,
        )
        if action_match:
            parameters['action'] = action_match.group(1)

        return parameters

    def _extract_file_params(self, command: str) -> Dict[str, str]:
        """Extract file-related parameters.

        Args:
            command: The lowercase command text.

        Returns:
            Dictionary with file-related parameters.
        """
        params: Dict[str, str] = {}

        # Extract filename
        filename_match = re.search(r'([a-zA-Z0-9_\-\.]+\.\w+)', command)
        if filename_match:
            params['filename'] = filename_match.group(1)

        # Extract directory
        dir_match = re.search(r'in\s+(documents|downloads|desktop|folder)', command)
        if dir_match:
            params['directory'] = dir_match.group(1)
        else:
            params['directory'] = 'documents'

        return params

    def _extract_browser_params(self, command: str) -> Dict[str, str]:
        """Extract browser-related parameters.

        Args:
            command: The lowercase command text.

        Returns:
            Dictionary with browser-related parameters.
        """
        params: Dict[str, str] = {}

        # Extract URL
        url_match = re.search(
            r'(https?://[^\s]+|www\.[^\s]+)', command
        )
        if url_match:
            params['url'] = url_match.group(1)

        # Extract search query (everything after search/google/find)
        search_match = re.search(
            r'(?:search|google|look up|find)\s+(?:for\s+)?(.+)', command
        )
        if search_match:
            params['query'] = search_match.group(1).strip()

        return params

    def _extract_system_params(self, command: str) -> Dict[str, str]:
        """Extract system command parameters.

        Args:
            command: The lowercase command text.

        Returns:
            Dictionary with system-related parameters.
        """
        params: Dict[str, str] = {}

        # Extract system component
        component_match = re.search(
            r'(cpu|memory|disk|system|time|date|status)', command
        )
        if component_match:
            params['component'] = component_match.group(1)

        return params

    def _extract_application_params(self, command: str) -> Dict[str, str]:
        """Extract application-related parameters.

        Args:
            command: The lowercase command text.

        Returns:
            Dictionary with application-related parameters.
        """
        params: Dict[str, str] = {}

        # Extract application name
        app_match = re.search(
            r'(browser|text editor|file manager|email|terminal|editor|mail)',
            command,
        )
        if app_match:
            app_name = app_match.group(1)
            # Normalize application names
            app_mapping = {
                'text editor': 'text_editor',
                'file manager': 'file_manager',
                'mail': 'email',
                'editor': 'text_editor',
            }
            params['application'] = app_mapping.get(app_name, app_name)

        return params
