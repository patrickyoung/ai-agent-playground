# Computer Use Agent

A production-ready AI agent for desktop automation using natural language commands.

## Overview

The Computer Use Agent is a sophisticated Python application that processes natural language commands and automates desktop tasks in a simulated environment. Built with production-quality code following Guido van Rossum's Python design principles, it demonstrates:

- **Natural Language Processing**: Pattern-based intent recognition and parameter extraction
- **Task Execution**: Multiple operation types including file operations, browser actions, system commands, and application tasks
- **Virtual Desktop Environment**: Safe, sandboxed simulation of desktop components
- **Production-Ready Architecture**: Type hints, comprehensive logging, modular design, and extensive testing

## Features

### Core Capabilities

- **File Operations**: Open, create, delete, and list files
- **Browser Actions**: Navigate URLs, perform searches, manage tabs
- **System Commands**: Monitor CPU, memory, and disk usage
- **Application Tasks**: Launch and close desktop applications
- **Workflow Automation**: Execute multi-step batch operations

### Technical Highlights

- ✅ **Type-Safe**: Full type hints following PEP 484
- ✅ **Well-Documented**: Comprehensive docstrings following PEP 257
- ✅ **Tested**: Unit and integration tests with pytest
- ✅ **Configurable**: Environment-based configuration
- ✅ **Logging**: Structured logging with multiple output options
- ✅ **CLI Interface**: Interactive and batch execution modes
- ✅ **Zero Dependencies**: Pure Python implementation

## Installation

### From Source

```bash
# Clone the repository
git clone https://github.com/example/computer-use-agent.git
cd computer-use-agent

# Install in development mode
pip install -e .

# Or install with development dependencies
pip install -e ".[dev]"
```

### From PyPI (when published)

```bash
pip install computer-use-agent
```

## Quick Start

### Interactive Mode

Launch the agent in interactive mode:

```bash
computer-use-agent --interactive
```

Or using the Python module:

```bash
python -m computer_use_agent
```

Try some commands:

```
agent> open the browser
agent> create a file called report.txt
agent> check system status
agent> list files in documents
agent> status
agent> exit
```

### Single Command

Execute a single command:

```bash
computer-use-agent --command "open the browser"
```

### Batch Mode

Execute multiple commands:

```bash
computer-use-agent --batch "open the browser" "check system status" "list files"
```

### Demo Mode

Run a demonstration:

```bash
computer-use-agent --demo
```

## Usage

### As a Python Library

```python
from computer_use_agent import DesktopAgent

# Create an agent instance
agent = DesktopAgent()

# Process a command
task = agent.process_command("open the browser")

# Check the result
if task.status.value == 'completed':
    print(f"Success: {task.result}")
else:
    print(f"Failed: {task.error}")

# View agent statistics
stats = agent.get_statistics_summary()
print(f"Success rate: {stats['success_rate']}%")

# Display dashboard
print(agent.display_dashboard())
```

### Batch Processing

```python
from computer_use_agent import DesktopAgent

agent = DesktopAgent()

commands = [
    "open the browser",
    "create a file called notes.txt",
    "check system status",
    "launch text editor",
]

tasks = agent.process_batch(commands)

for task in tasks:
    print(f"{task.command}: {task.status.value}")
```

## Configuration

Configure the agent using environment variables:

```bash
# Logging level (DEBUG, INFO, WARNING, ERROR)
export AGENT_LOG_LEVEL=INFO

# Log file path
export AGENT_LOG_FILE=/var/log/agent.log

# Enable console logging
export AGENT_CONSOLE_LOG=true

# Maximum task history size
export AGENT_MAX_HISTORY=100

# Simulation delay (seconds)
export AGENT_SIM_DELAY=0.1
```

Or programmatically:

```python
from computer_use_agent.config import setup_logging
from pathlib import Path

setup_logging(
    level='DEBUG',
    log_file=Path('agent.log'),
    enable_console=True
)
```

## Architecture

The agent follows a clean, modular architecture:

```
computer_use_agent/
├── models/           # Data models (Task, TaskType, TaskStatus)
├── core/             # Core components (DesktopAgent, VirtualDesktop)
├── processors/       # NLP processing (NLPProcessor)
├── executors/        # Task execution (TaskExecutor)
├── config/           # Configuration and logging
└── cli.py            # Command-line interface
```

### Component Overview

- **DesktopAgent**: Main coordinator orchestrating the automation pipeline
- **VirtualDesktop**: Simulated desktop environment with applications and file system
- **NLPProcessor**: Natural language command analysis and intent extraction
- **TaskExecutor**: Task execution engine routing to appropriate handlers
- **Task**: Data model representing executable commands with status tracking

## Development

### Setup Development Environment

```bash
# Clone the repository
git clone https://github.com/example/computer-use-agent.git
cd computer-use-agent

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install development dependencies
pip install -e ".[dev]"
```

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=computer_use_agent --cov-report=html

# Run specific test file
pytest tests/unit/test_task.py

# Run with verbose output
pytest -v
```

### Code Quality

```bash
# Format code with black
black src/ tests/

# Lint with ruff
ruff check src/ tests/

# Type check with mypy
mypy src/
```

### Project Structure

```
computer_use_agent/
├── src/
│   └── computer_use_agent/
│       ├── __init__.py
│       ├── __main__.py
│       ├── cli.py
│       ├── core/
│       │   ├── __init__.py
│       │   ├── agent.py
│       │   └── desktop.py
│       ├── models/
│       │   ├── __init__.py
│       │   └── task.py
│       ├── processors/
│       │   ├── __init__.py
│       │   └── nlp_processor.py
│       ├── executors/
│       │   ├── __init__.py
│       │   └── task_executor.py
│       ├── config/
│       │   ├── __init__.py
│       │   ├── settings.py
│       │   └── logging_config.py
│       └── py.typed
├── tests/
│   ├── __init__.py
│   ├── conftest.py
│   ├── unit/
│   │   ├── test_task.py
│   │   └── test_desktop.py
│   └── integration/
├── docs/
├── examples/
├── pyproject.toml
├── README.md
├── LICENSE
└── .gitignore
```

## Examples

### Example 1: File Management

```python
from computer_use_agent import DesktopAgent

agent = DesktopAgent()

# Create a file
task = agent.process_command("create a file called todo.txt")
print(task.result)  # Created todo.txt in documents directory

# List files
task = agent.process_command("list files in documents")
print(task.result)  # Files in documents: report.pdf, notes.txt, ...
```

### Example 2: Browser Automation

```python
from computer_use_agent import DesktopAgent

agent = DesktopAgent()

# Open browser and search
task = agent.process_command("search for python tutorials")
print(task.result)  # Searched for "python tutorials" in browser

# Navigate to URL
task = agent.process_command("open https://www.python.org")
print(task.result)  # Navigated to https://www.python.org in browser
```

### Example 3: System Monitoring

```python
from computer_use_agent import DesktopAgent

agent = DesktopAgent()

# Check system status
task = agent.process_command("check system status")
print(task.result)  # System Status - CPU: 45.2%, Memory: 52.1%, Disk: 48.3%
```

## Testing

The project includes comprehensive test coverage:

- **Unit Tests**: Test individual components in isolation
- **Integration Tests**: Verify components work together correctly
- **Fixtures**: Reusable test components via pytest fixtures

Run tests with:

```bash
pytest                          # Run all tests
pytest tests/unit/             # Run unit tests only
pytest -v                      # Verbose output
pytest --cov                   # With coverage report
```

## Contributing

Contributions are welcome! Please follow these guidelines:

1. **Code Style**: Follow PEP 8 and use black for formatting
2. **Type Hints**: Add type hints to all functions (PEP 484)
3. **Documentation**: Write clear docstrings (PEP 257)
4. **Testing**: Add tests for new functionality
5. **Commits**: Write clear, descriptive commit messages

## Design Principles

This project follows Guido van Rossum's Python design philosophy:

- **Explicit is better than implicit**: Clear, obvious code over clever tricks
- **Simple is better than complex**: Straightforward solutions preferred
- **Readability counts**: Code is written for humans to read
- **Flat is better than nested**: Minimal nesting, clear hierarchy
- **Type hints**: Full type annotations for clarity and safety

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- Inspired by the MarkTechPost article on building AI desktop automation agents
- Built following Python best practices and PEPs
- Designed in the style of Guido van Rossum's clean, readable Python code

## Support

- **Issues**: Report bugs at https://github.com/example/computer-use-agent/issues
- **Documentation**: See the docs/ directory for detailed guides
- **Examples**: Check the examples/ directory for more use cases

## Changelog

### Version 1.0.0 (2024-10-26)

- Initial release
- Complete virtual desktop simulation
- Natural language command processing
- File, browser, system, and application operations
- Interactive and batch CLI modes
- Comprehensive test suite
- Full type hint coverage
- Production-ready code structure
