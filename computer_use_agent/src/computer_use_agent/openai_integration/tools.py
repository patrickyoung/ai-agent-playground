"""OpenAI tool definitions for desktop operations.

This module defines the desktop automation operations as OpenAI function tools,
following the Responses API specification. Each tool represents an action the
agent can perform on the virtual desktop.

Following Guido's principle: explicit tool definitions over implicit behavior.
"""

from typing import Any, Dict, List


def get_desktop_tools() -> List[Dict[str, Any]]:
    """Get the list of desktop operation tools for OpenAI.

    These tools are defined according to OpenAI's function calling specification.
    Each tool includes a name, description, and parameter schema.

    Returns:
        List of tool definition dictionaries for the OpenAI API.
    """
    return [
        {
            'type': 'function',
            'function': {
                'name': 'launch_application',
                'description': 'Launch or open a desktop application',
                'parameters': {
                    'type': 'object',
                    'properties': {
                        'application': {
                            'type': 'string',
                            'enum': [
                                'browser',
                                'text_editor',
                                'file_manager',
                                'email',
                                'terminal',
                            ],
                            'description': 'The application to launch',
                        }
                    },
                    'required': ['application'],
                },
            },
        },
        {
            'type': 'function',
            'function': {
                'name': 'close_application',
                'description': 'Close a running desktop application',
                'parameters': {
                    'type': 'object',
                    'properties': {
                        'application': {
                            'type': 'string',
                            'enum': [
                                'browser',
                                'text_editor',
                                'file_manager',
                                'email',
                                'terminal',
                            ],
                            'description': 'The application to close',
                        }
                    },
                    'required': ['application'],
                },
            },
        },
        {
            'type': 'function',
            'function': {
                'name': 'create_file',
                'description': 'Create a new file in a directory',
                'parameters': {
                    'type': 'object',
                    'properties': {
                        'filename': {
                            'type': 'string',
                            'description': 'The name of the file to create',
                        },
                        'directory': {
                            'type': 'string',
                            'enum': ['documents', 'downloads', 'desktop'],
                            'description': 'The directory to create the file in',
                            'default': 'documents',
                        },
                    },
                    'required': ['filename'],
                },
            },
        },
        {
            'type': 'function',
            'function': {
                'name': 'delete_file',
                'description': 'Delete a file from a directory',
                'parameters': {
                    'type': 'object',
                    'properties': {
                        'filename': {
                            'type': 'string',
                            'description': 'The name of the file to delete',
                        },
                        'directory': {
                            'type': 'string',
                            'enum': ['documents', 'downloads', 'desktop'],
                            'description': 'The directory containing the file',
                            'default': 'documents',
                        },
                    },
                    'required': ['filename'],
                },
            },
        },
        {
            'type': 'function',
            'function': {
                'name': 'list_files',
                'description': 'List all files in a directory',
                'parameters': {
                    'type': 'object',
                    'properties': {
                        'directory': {
                            'type': 'string',
                            'enum': ['documents', 'downloads', 'desktop'],
                            'description': 'The directory to list files from',
                            'default': 'documents',
                        }
                    },
                    'required': ['directory'],
                },
            },
        },
        {
            'type': 'function',
            'function': {
                'name': 'open_file',
                'description': 'Open an existing file',
                'parameters': {
                    'type': 'object',
                    'properties': {
                        'filename': {
                            'type': 'string',
                            'description': 'The name of the file to open',
                        },
                        'directory': {
                            'type': 'string',
                            'enum': ['documents', 'downloads', 'desktop'],
                            'description': 'The directory containing the file',
                            'default': 'documents',
                        },
                    },
                    'required': ['filename'],
                },
            },
        },
        {
            'type': 'function',
            'function': {
                'name': 'navigate_browser',
                'description': (
                    'Navigate the browser to a URL or perform a web search. '
                    'Provide either url parameter for direct navigation, or '
                    'search_query parameter to search. Exactly one must be provided.'
                ),
                'parameters': {
                    'type': 'object',
                    'properties': {
                        'url': {
                            'type': 'string',
                            'description': 'The URL to navigate to (e.g., https://example.com)',
                        },
                        'search_query': {
                            'type': 'string',
                            'description': 'Search query to look up in the browser',
                        },
                    },
                    # Note: OpenAI function calling doesn't support oneOf/anyOf well,
                    # so validation is done in the implementation
                },
            },
        },
        {
            'type': 'function',
            'function': {
                'name': 'get_system_status',
                'description': 'Get current system resource usage (CPU, memory, disk)',
                'parameters': {
                    'type': 'object',
                    'properties': {
                        'component': {
                            'type': 'string',
                            'enum': ['all', 'cpu', 'memory', 'disk'],
                            'description': 'Specific component to check, or all',
                            'default': 'all',
                        }
                    },
                },
            },
        },
        {
            'type': 'function',
            'function': {
                'name': 'get_running_applications',
                'description': 'Get list of currently running applications',
                'parameters': {'type': 'object', 'properties': {}},
            },
        },
    ]


def get_tool_mapping() -> Dict[str, str]:
    """Get mapping of tool names to their descriptions.

    Useful for logging and debugging what tools are available.

    Returns:
        Dictionary mapping tool names to descriptions.
    """
    tools = get_desktop_tools()
    return {
        tool['function']['name']: tool['function']['description'] for tool in tools
    }
