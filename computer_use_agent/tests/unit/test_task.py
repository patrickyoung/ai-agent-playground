"""Unit tests for Task model.

Following pytest best practices with clear test names and assertions.
"""

import pytest
from datetime import datetime

from computer_use_agent.models.task import Task, TaskType, TaskStatus


class TestTask:
    """Test suite for Task model."""

    def test_task_creation(self):
        """Test basic task creation with required fields."""
        task = Task(command='test command', task_type=TaskType.FILE_OPERATION)

        assert task.command == 'test command'
        assert task.task_type == TaskType.FILE_OPERATION
        assert task.status == TaskStatus.PENDING
        assert task.result == ''
        assert task.error == ''
        assert isinstance(task.task_id, str)
        assert len(task.task_id) > 0

    def test_task_mark_started(self):
        """Test marking a task as started updates status and timestamp."""
        task = Task(command='test', task_type=TaskType.FILE_OPERATION)

        task.mark_started()

        assert task.status == TaskStatus.IN_PROGRESS
        assert task.started_at is not None
        assert isinstance(task.started_at, datetime)

    def test_task_mark_completed(self):
        """Test marking a task as completed with result."""
        task = Task(command='test', task_type=TaskType.FILE_OPERATION)
        task.mark_started()

        result_message = 'Task completed successfully'
        task.mark_completed(result_message)

        assert task.status == TaskStatus.COMPLETED
        assert task.result == result_message
        assert task.completed_at is not None
        assert task.execution_time > 0

    def test_task_mark_failed(self):
        """Test marking a task as failed with error message."""
        task = Task(command='test', task_type=TaskType.FILE_OPERATION)
        task.mark_started()

        error_message = 'Task failed due to error'
        task.mark_failed(error_message)

        assert task.status == TaskStatus.FAILED
        assert task.error == error_message
        assert task.completed_at is not None
        assert task.execution_time > 0

    def test_task_to_dict(self):
        """Test task serialization to dictionary."""
        task = Task(
            command='test command',
            task_type=TaskType.BROWSER_ACTION,
            confidence=0.95,
            parameters={'url': 'http://example.com'},
        )

        task_dict = task.to_dict()

        assert task_dict['command'] == 'test command'
        assert task_dict['task_type'] == 'browser_action'
        assert task_dict['status'] == 'pending'
        assert task_dict['confidence'] == 0.95
        assert task_dict['parameters'] == {'url': 'http://example.com'}
        assert 'task_id' in task_dict

    def test_execution_time_calculation(self):
        """Test execution time is calculated correctly."""
        import time

        task = Task(command='test', task_type=TaskType.SYSTEM_COMMAND)
        task.mark_started()

        # Simulate some work
        time.sleep(0.05)

        task.mark_completed('Done')

        assert task.execution_time >= 0.05
        assert task.execution_time < 1.0  # Should be quick


class TestTaskType:
    """Test suite for TaskType enum."""

    def test_task_type_values(self):
        """Test all task type enumeration values."""
        assert TaskType.FILE_OPERATION.value == 'file_operation'
        assert TaskType.BROWSER_ACTION.value == 'browser_action'
        assert TaskType.SYSTEM_COMMAND.value == 'system_command'
        assert TaskType.APPLICATION_TASK.value == 'application_task'
        assert TaskType.WORKFLOW.value == 'workflow'


class TestTaskStatus:
    """Test suite for TaskStatus enum."""

    def test_task_status_values(self):
        """Test all task status enumeration values."""
        assert TaskStatus.PENDING.value == 'pending'
        assert TaskStatus.IN_PROGRESS.value == 'in_progress'
        assert TaskStatus.COMPLETED.value == 'completed'
        assert TaskStatus.FAILED.value == 'failed'
        assert TaskStatus.CANCELLED.value == 'cancelled'
