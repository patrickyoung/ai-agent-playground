"""Virtual desktop environment simulation.

This module provides a simulated desktop environment with applications,
file system, and system state management.
"""

import random
from dataclasses import dataclass, field
from typing import Dict, List, Set, Tuple


@dataclass
class SystemInfo:
    """System resource information.

    Attributes:
        cpu_usage: Current CPU utilization percentage.
        memory_usage: Current memory utilization percentage.
        disk_usage: Current disk utilization percentage.
    """

    cpu_usage: float = 0.0
    memory_usage: float = 0.0
    disk_usage: float = 0.0

    def update(self) -> None:
        """Simulate system resource usage with random values."""
        self.cpu_usage = round(random.uniform(10.0, 80.0), 1)
        self.memory_usage = round(random.uniform(30.0, 70.0), 1)
        self.disk_usage = round(random.uniform(40.0, 60.0), 1)


@dataclass
class Application:
    """Represents a desktop application.

    Attributes:
        name: The name of the application.
        is_running: Whether the application is currently running.
        window_title: The title of the application window when running.
    """

    name: str
    is_running: bool = False
    window_title: str = ''


class VirtualDesktop:
    """Simulates a desktop environment with applications and file system.

    This class provides a sandboxed environment for testing automation agents
    without affecting the real system. It maintains state for applications,
    files, screen position, and clipboard.

    Attributes:
        applications: Dictionary of available applications.
        file_system: Hierarchical file system structure.
        running_apps: Set of currently running application names.
        active_window: Name of the currently active application window.
        mouse_position: Current mouse cursor coordinates.
        clipboard: Current clipboard contents.
        system_info: System resource usage information.
    """

    def __init__(self) -> None:
        """Initialize the virtual desktop with default applications and files."""
        self.applications: Dict[str, Application] = {
            'browser': Application('browser', window_title='Web Browser'),
            'file_manager': Application('file_manager', window_title='File Manager'),
            'text_editor': Application('text_editor', window_title='Text Editor'),
            'email': Application('email', window_title='Email Client'),
            'terminal': Application('terminal', window_title='Terminal'),
        }

        self.file_system: Dict[str, List[str]] = {
            'documents': ['report.pdf', 'notes.txt', 'presentation.pptx'],
            'downloads': ['setup.exe', 'image.jpg', 'archive.zip'],
            'desktop': ['readme.txt', 'shortcut.lnk'],
        }

        self.running_apps: Set[str] = set()
        self.active_window: str = ''
        self.mouse_position: Tuple[int, int] = (0, 0)
        self.clipboard: str = ''
        self.system_info: SystemInfo = SystemInfo()

    def launch_application(self, app_name: str) -> bool:
        """Launch an application if it exists.

        Args:
            app_name: The name of the application to launch.

        Returns:
            True if the application was launched successfully, False otherwise.
        """
        if app_name not in self.applications:
            return False

        app = self.applications[app_name]
        app.is_running = True
        self.running_apps.add(app_name)
        self.active_window = app.window_title
        return True

    def close_application(self, app_name: str) -> bool:
        """Close a running application.

        Args:
            app_name: The name of the application to close.

        Returns:
            True if the application was closed successfully, False otherwise.
        """
        if app_name not in self.applications:
            return False

        app = self.applications[app_name]
        app.is_running = False
        self.running_apps.discard(app_name)

        if self.active_window == app.window_title:
            self.active_window = ''

        return True

    def get_running_applications(self) -> List[str]:
        """Get list of currently running application names.

        Returns:
            List of running application names.
        """
        return list(self.running_apps)

    def list_files(self, directory: str = 'documents') -> List[str]:
        """List files in a directory.

        Args:
            directory: The directory to list files from.

        Returns:
            List of filenames in the directory, or empty list if not found.
        """
        return self.file_system.get(directory, [])

    def file_exists(self, filename: str, directory: str = 'documents') -> bool:
        """Check if a file exists in a directory.

        Args:
            filename: The name of the file to check.
            directory: The directory to check in.

        Returns:
            True if the file exists, False otherwise.
        """
        return filename in self.file_system.get(directory, [])

    def create_file(self, filename: str, directory: str = 'documents') -> bool:
        """Create a new file in a directory.

        Args:
            filename: The name of the file to create.
            directory: The directory to create the file in.

        Returns:
            True if the file was created, False if it already exists.
        """
        if directory not in self.file_system:
            self.file_system[directory] = []

        if filename in self.file_system[directory]:
            return False

        self.file_system[directory].append(filename)
        return True

    def delete_file(self, filename: str, directory: str = 'documents') -> bool:
        """Delete a file from a directory.

        Args:
            filename: The name of the file to delete.
            directory: The directory containing the file.

        Returns:
            True if the file was deleted, False if not found.
        """
        if directory not in self.file_system:
            return False

        if filename not in self.file_system[directory]:
            return False

        self.file_system[directory].remove(filename)
        return True

    def move_mouse(self, x: int, y: int) -> None:
        """Move the mouse cursor to coordinates.

        Args:
            x: The x coordinate.
            y: The y coordinate.
        """
        self.mouse_position = (x, y)

    def set_clipboard(self, content: str) -> None:
        """Set the clipboard contents.

        Args:
            content: The text to copy to clipboard.
        """
        self.clipboard = content

    def get_clipboard(self) -> str:
        """Get the current clipboard contents.

        Returns:
            The current clipboard text.
        """
        return self.clipboard

    def update_system_info(self) -> SystemInfo:
        """Update and return current system resource information.

        Returns:
            Updated system information with current resource usage.
        """
        self.system_info.update()
        return self.system_info

    def get_state_summary(self) -> Dict[str, Any]:
        """Get a summary of the current desktop state.

        Returns:
            Dictionary containing current state information.
        """
        return {
            'running_applications': list(self.running_apps),
            'active_window': self.active_window,
            'mouse_position': self.mouse_position,
            'clipboard_length': len(self.clipboard),
            'system_info': {
                'cpu_usage': self.system_info.cpu_usage,
                'memory_usage': self.system_info.memory_usage,
                'disk_usage': self.system_info.disk_usage,
            },
        }
