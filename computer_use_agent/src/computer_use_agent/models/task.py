"""Task model definitions.

This module defines the core task types and data structures for agent operations.
Following PEP 484 (type hints) and PEP 257 (docstrings).
"""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Dict, Optional
from uuid import uuid4


class TaskType(Enum):
    """Enumeration of supported task types.

    Each task type corresponds to a specific category of desktop operations
    that the agent can perform.
    """

    FILE_OPERATION = 'file_operation'
    BROWSER_ACTION = 'browser_action'
    SYSTEM_COMMAND = 'system_command'
    APPLICATION_TASK = 'application_task'
    WORKFLOW = 'workflow'


class TaskStatus(Enum):
    """Enumeration of possible task states.

    Tasks transition through these states during their lifecycle.
    """

    PENDING = 'pending'
    IN_PROGRESS = 'in_progress'
    COMPLETED = 'completed'
    FAILED = 'failed'
    CANCELLED = 'cancelled'


@dataclass
class Task:
    """Represents a single executable task for the desktop agent.

    A task encapsulates all information needed to execute a user command,
    track its progress, and record results.

    Attributes:
        command: The natural language command to execute.
        task_type: The category of operation this task performs.
        task_id: Unique identifier for the task.
        status: Current execution status of the task.
        result: Output or result message from task execution.
        error: Error message if the task failed.
        confidence: Confidence score of intent recognition (0.0 to 1.0).
        parameters: Extracted parameters from the command.
        created_at: Timestamp when the task was created.
        started_at: Timestamp when execution began.
        completed_at: Timestamp when execution finished.
        execution_time: Duration of execution in seconds.
    """

    command: str
    task_type: TaskType
    task_id: str = field(default_factory=lambda: str(uuid4()))
    status: TaskStatus = TaskStatus.PENDING
    result: str = ''
    error: str = ''
    confidence: float = 0.0
    parameters: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.now)
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    execution_time: float = 0.0

    def mark_started(self) -> None:
        """Mark the task as started and record the start time."""
        self.status = TaskStatus.IN_PROGRESS
        self.started_at = datetime.now()

    def mark_completed(self, result: str = '') -> None:
        """Mark the task as completed successfully.

        Args:
            result: Optional result message from the task execution.
        """
        self.status = TaskStatus.COMPLETED
        self.completed_at = datetime.now()
        self.result = result
        if self.started_at:
            self.execution_time = (self.completed_at - self.started_at).total_seconds()

    def mark_failed(self, error: str) -> None:
        """Mark the task as failed with an error message.

        Args:
            error: Description of what went wrong during execution.
        """
        self.status = TaskStatus.FAILED
        self.completed_at = datetime.now()
        self.error = error
        if self.started_at:
            self.execution_time = (self.completed_at - self.started_at).total_seconds()

    def to_dict(self) -> Dict[str, Any]:
        """Convert the task to a dictionary representation.

        Returns:
            Dictionary containing all task attributes.
        """
        return {
            'task_id': self.task_id,
            'command': self.command,
            'task_type': self.task_type.value,
            'status': self.status.value,
            'result': self.result,
            'error': self.error,
            'confidence': self.confidence,
            'parameters': self.parameters,
            'created_at': self.created_at.isoformat(),
            'started_at': self.started_at.isoformat() if self.started_at else None,
            'completed_at': self.completed_at.isoformat() if self.completed_at else None,
            'execution_time': self.execution_time,
        }
