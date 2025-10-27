# Computer Use Agent - Usage Guide

This guide provides detailed information on using the Computer Use Agent.

## Table of Contents

1. [Getting Started](#getting-started)
2. [Command Examples](#command-examples)
3. [CLI Modes](#cli-modes)
4. [Python API](#python-api)
5. [Configuration](#configuration)
6. [Advanced Usage](#advanced-usage)

## Getting Started

### Installation

```bash
pip install computer-use-agent
```

### First Run

Start the agent in interactive mode:

```bash
computer-use-agent --interactive
```

You'll see the welcome banner and command prompt:

```
agent>
```

Try your first command:

```
agent> open the browser
```

## Command Examples

### File Operations

```bash
# Create a file
create a file called report.txt

# Open a file
open report.pdf

# List files in a directory
list files in documents
list files in downloads

# Delete a file
delete notes.txt
```

### Browser Actions

```bash
# Open browser
open the browser
launch browser

# Navigate to URL
open https://www.example.com
navigate to www.python.org

# Search
search for python tutorials
google machine learning
find best practices
```

### System Commands

```bash
# Check system status
check system status
show system info

# Check specific components
check cpu usage
show memory status
display disk usage
```

### Application Tasks

```bash
# Launch applications
open text editor
launch file manager
start email client

# Close applications
close browser
quit text editor
exit terminal
```

## CLI Modes

### Interactive Mode

The default mode for exploring and testing:

```bash
computer-use-agent --interactive
```

Special commands in interactive mode:

- `status` - Display agent dashboard
- `clear` - Clear history and statistics
- `demo` - Run demonstration
- `help` - Show help message
- `exit` - Quit the application

### Single Command Mode

Execute one command and exit:

```bash
computer-use-agent --command "open the browser"
```

### Batch Mode

Execute multiple commands in sequence:

```bash
computer-use-agent --batch "open the browser" "check system status" "list files"
```

### Demo Mode

Run a pre-configured demonstration:

```bash
computer-use-agent --demo
```

## Python API

### Basic Usage

```python
from computer_use_agent import DesktopAgent

# Create agent
agent = DesktopAgent()

# Execute command
task = agent.process_command("open the browser")

# Check result
print(f"Status: {task.status.value}")
print(f"Result: {task.result}")
```

### Task Properties

Each task has these properties:

```python
task.task_id          # Unique identifier
task.command          # Original command
task.task_type        # Type of operation
task.status           # Current status
task.result           # Success message
task.error            # Error message (if failed)
task.confidence       # Recognition confidence (0-1)
task.parameters       # Extracted parameters
task.execution_time   # Time taken (seconds)
```

### Batch Processing

```python
commands = [
    "open the browser",
    "create a file called notes.txt",
    "check system status"
]

tasks = agent.process_batch(commands)

for task in tasks:
    print(f"{task.command}: {task.status.value}")
```

### Statistics

```python
# Get statistics summary
stats = agent.get_statistics_summary()

print(f"Total tasks: {stats['total_tasks']}")
print(f"Success rate: {stats['success_rate']}%")
print(f"Avg time: {stats['average_execution_time']}s")
```

### Desktop State

```python
# Get current desktop state
state = agent.get_desktop_state()

print(f"Running apps: {state['running_applications']}")
print(f"Active window: {state['active_window']}")
print(f"CPU: {state['system_info']['cpu_usage']}%")
```

### Recent Tasks

```python
# Get recent task history
recent = agent.get_recent_tasks(count=5)

for task in recent:
    print(f"{task.command} - {task.status.value}")
```

## Configuration

### Environment Variables

Configure the agent using environment variables:

```bash
# Logging level
export AGENT_LOG_LEVEL=DEBUG

# Log file location
export AGENT_LOG_FILE=/var/log/agent.log

# Console logging
export AGENT_CONSOLE_LOG=true

# Task history limit
export AGENT_MAX_HISTORY=100

# Simulation delay
export AGENT_SIM_DELAY=0.1
```

### Programmatic Configuration

```python
from computer_use_agent.config import setup_logging
from pathlib import Path

# Setup custom logging
setup_logging(
    level='DEBUG',
    log_file=Path('agent.log'),
    enable_console=True
)
```

### Settings Object

```python
from computer_use_agent.config import get_settings

settings = get_settings()

print(f"Log level: {settings.log_level}")
print(f"Max history: {settings.max_task_history}")
```

## Advanced Usage

### Custom Virtual Desktop

Create a custom desktop instance:

```python
from computer_use_agent import DesktopAgent, VirtualDesktop

# Create custom desktop
desktop = VirtualDesktop()

# Customize the environment
desktop.create_file('custom.txt', 'documents')
desktop.launch_application('browser')

# Create agent with custom desktop
agent = DesktopAgent(desktop=desktop)
```

### Task Filtering

Filter tasks by status:

```python
from computer_use_agent.models import TaskStatus

agent = DesktopAgent()

# Execute commands
agent.process_command("open the browser")
agent.process_command("open nonexistent.txt")

# Filter tasks
completed = [t for t in agent.task_history if t.status == TaskStatus.COMPLETED]
failed = [t for t in agent.task_history if t.status == TaskStatus.FAILED]

print(f"Completed: {len(completed)}")
print(f"Failed: {len(failed)}")
```

### Error Handling

```python
from computer_use_agent import DesktopAgent
from computer_use_agent.models import TaskStatus

agent = DesktopAgent()

task = agent.process_command("some command")

if task.status == TaskStatus.COMPLETED:
    print(f"Success: {task.result}")
elif task.status == TaskStatus.FAILED:
    print(f"Error: {task.error}")
    print(f"Confidence: {task.confidence}")
```

### Dashboard Integration

```python
# Get formatted dashboard
dashboard = agent.display_dashboard()
print(dashboard)

# Or build custom dashboard
stats = agent.get_statistics_summary()
state = agent.get_desktop_state()

print(f"Tasks: {stats['total_tasks']}")
print(f"Success: {stats['success_rate']}%")
print(f"Apps: {len(state['running_applications'])}")
```

### Logging

```python
import logging

# Enable debug logging
logging.basicConfig(level=logging.DEBUG)

# Use agent (will output debug logs)
agent = DesktopAgent()
task = agent.process_command("open the browser")
```

## Best Practices

### 1. Always Check Task Status

```python
task = agent.process_command(command)
if task.status == TaskStatus.COMPLETED:
    # Handle success
else:
    # Handle failure
```

### 2. Use Batch for Multiple Commands

```python
# Good: Batch processing
tasks = agent.process_batch(commands)

# Less efficient: Individual calls
for cmd in commands:
    task = agent.process_command(cmd)
```

### 3. Monitor Statistics

```python
# Periodically check success rate
stats = agent.get_statistics_summary()
if stats['success_rate'] < 80:
    print("Warning: Low success rate")
```

### 4. Configure Logging Appropriately

```python
# Production: INFO or WARNING
setup_logging(level='INFO')

# Development: DEBUG
setup_logging(level='DEBUG')
```

### 5. Clean Up Periodically

```python
# Clear old history
if len(agent.task_history) > 1000:
    agent.clear_history()
    agent.reset_statistics()
```

## Troubleshooting

### Command Not Recognized

If a command isn't recognized well (low confidence):

- Make the command more specific
- Use exact keywords like "open", "create", "check"
- Check supported task types in documentation

### High Failure Rate

If many tasks fail:

- Check command syntax
- Verify file/directory names
- Review error messages in task.error

### Slow Performance

If execution is slow:

- Reduce simulation delay in settings
- Use batch processing for multiple commands
- Clear history periodically

## Examples

See the `examples/` directory for complete working examples:

- `basic_usage.py` - Common usage patterns
- More examples to come...

## Further Reading

- [README.md](../README.md) - Project overview
- [Architecture documentation](ARCHITECTURE.md) - System design
- [API documentation](API.md) - Complete API reference
