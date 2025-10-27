"""Unit tests for VirtualDesktop.

Tests the simulated desktop environment functionality.
"""

import pytest

from computer_use_agent.core.desktop import VirtualDesktop


class TestVirtualDesktop:
    """Test suite for VirtualDesktop."""

    def test_desktop_initialization(self):
        """Test desktop initializes with default applications and files."""
        desktop = VirtualDesktop()

        assert 'browser' in desktop.applications
        assert 'file_manager' in desktop.applications
        assert 'text_editor' in desktop.applications
        assert 'email' in desktop.applications
        assert 'terminal' in desktop.applications

        assert 'documents' in desktop.file_system
        assert 'downloads' in desktop.file_system
        assert 'desktop' in desktop.file_system

    def test_launch_application(self):
        """Test launching an application."""
        desktop = VirtualDesktop()

        result = desktop.launch_application('browser')

        assert result is True
        assert 'browser' in desktop.running_apps
        assert desktop.applications['browser'].is_running is True
        assert desktop.active_window == 'Web Browser'

    def test_launch_nonexistent_application(self):
        """Test launching a non-existent application fails."""
        desktop = VirtualDesktop()

        result = desktop.launch_application('nonexistent')

        assert result is False
        assert 'nonexistent' not in desktop.running_apps

    def test_close_application(self):
        """Test closing a running application."""
        desktop = VirtualDesktop()
        desktop.launch_application('browser')

        result = desktop.close_application('browser')

        assert result is True
        assert 'browser' not in desktop.running_apps
        assert desktop.applications['browser'].is_running is False

    def test_close_nonrunning_application(self):
        """Test closing a non-running application."""
        desktop = VirtualDesktop()

        result = desktop.close_application('browser')

        # Should still succeed (idempotent)
        assert result is True

    def test_get_running_applications(self):
        """Test retrieving list of running applications."""
        desktop = VirtualDesktop()
        desktop.launch_application('browser')
        desktop.launch_application('text_editor')

        running = desktop.get_running_applications()

        assert len(running) == 2
        assert 'browser' in running
        assert 'text_editor' in running

    def test_list_files(self):
        """Test listing files in a directory."""
        desktop = VirtualDesktop()

        files = desktop.list_files('documents')

        assert isinstance(files, list)
        assert len(files) > 0
        assert 'report.pdf' in files

    def test_list_files_nonexistent_directory(self):
        """Test listing files in non-existent directory."""
        desktop = VirtualDesktop()

        files = desktop.list_files('nonexistent')

        assert files == []

    def test_file_exists(self):
        """Test checking if a file exists."""
        desktop = VirtualDesktop()

        assert desktop.file_exists('report.pdf', 'documents') is True
        assert desktop.file_exists('nonexistent.txt', 'documents') is False

    def test_create_file(self):
        """Test creating a new file."""
        desktop = VirtualDesktop()

        result = desktop.create_file('newfile.txt', 'documents')

        assert result is True
        assert 'newfile.txt' in desktop.file_system['documents']

    def test_create_duplicate_file(self):
        """Test creating a file that already exists fails."""
        desktop = VirtualDesktop()
        desktop.create_file('test.txt', 'documents')

        result = desktop.create_file('test.txt', 'documents')

        assert result is False

    def test_delete_file(self):
        """Test deleting an existing file."""
        desktop = VirtualDesktop()
        desktop.create_file('todelete.txt', 'documents')

        result = desktop.delete_file('todelete.txt', 'documents')

        assert result is True
        assert 'todelete.txt' not in desktop.file_system['documents']

    def test_delete_nonexistent_file(self):
        """Test deleting a non-existent file fails."""
        desktop = VirtualDesktop()

        result = desktop.delete_file('nonexistent.txt', 'documents')

        assert result is False

    def test_mouse_operations(self):
        """Test mouse position tracking."""
        desktop = VirtualDesktop()

        desktop.move_mouse(100, 200)

        assert desktop.mouse_position == (100, 200)

    def test_clipboard_operations(self):
        """Test clipboard set and get."""
        desktop = VirtualDesktop()

        test_text = 'Hello, World!'
        desktop.set_clipboard(test_text)

        assert desktop.get_clipboard() == test_text

    def test_system_info_update(self):
        """Test system information updates."""
        desktop = VirtualDesktop()

        sys_info = desktop.update_system_info()

        assert sys_info.cpu_usage > 0
        assert sys_info.memory_usage > 0
        assert sys_info.disk_usage > 0

    def test_get_state_summary(self):
        """Test getting desktop state summary."""
        desktop = VirtualDesktop()
        desktop.launch_application('browser')
        desktop.move_mouse(50, 75)

        state = desktop.get_state_summary()

        assert 'running_applications' in state
        assert 'browser' in state['running_applications']
        assert state['mouse_position'] == (50, 75)
        assert 'system_info' in state
