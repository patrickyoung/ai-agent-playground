# Computer Use Agent v2.0 - OpenAI Powered

An intelligent desktop automation agent powered by OpenAI's Responses API with advanced tool calling capabilities.

## Overview

The Computer Use Agent is a sophisticated Python application that leverages OpenAI's Responses API to understand natural language commands and execute them through structured tool calling on a simulated desktop environment. Built following Guido van Rossum's Python design principles, it demonstrates production-quality integration of AI reasoning with system automation.

### What's New in v2.0

- ✨ **OpenAI Integration**: Powered by OpenAI's Responses API for intelligent command understanding
- 🛠️ **Tool Calling**: Uses OpenAI's function calling to determine which operations to execute
- 🧠 **Smarter Reasoning**: Lets OpenAI handle intent recognition and task planning
- 🔄 **Conversational Context**: Maintains conversation history for multi-turn interactions
- ⚡ **Simplified Architecture**: Removed custom NLP - OpenAI does the heavy lifting

## Key Features

### OpenAI Responses API Integration
- **Intelligent Command Processing**: OpenAI analyzes commands and determines actions
- **Tool Calling**: Structured function calling for desktop operations
- **Context-Aware**: Maintains desktop state in conversation context
- **Multi-Step Tasks**: OpenAI can orchestrate complex multi-tool workflows

### Desktop Operations
- 🗂️ **File Operations**: Create, delete, open, and list files
- 🌐 **Browser Actions**: Navigate URLs and perform web searches
- 💻 **System Monitoring**: Check CPU, memory, and disk usage
- 📱 **Application Management**: Launch and close desktop applications
- 🔄 **Batch Processing**: Execute multiple commands efficiently

### Production Quality
- ✅ **Type-Safe**: Full type hints (PEP 484)
- ✅ **Well-Documented**: Comprehensive docstrings (PEP 257)
- ✅ **Configurable**: Environment-based configuration
- ✅ **Tested**: Unit and integration test structure
- ✅ **Logged**: Structured logging throughout

## Installation

### Prerequisites

- Python 3.9 or higher
- OpenAI API key ([Get one here](https://platform.openai.com/api-keys))

### Install from Source

```bash
# Clone the repository
git clone https://github.com/example/computer-use-agent.git
cd computer-use-agent

# Install the package
pip install -e .

# Or install with development dependencies
pip install -e ".[dev]"
```

### Set Up OpenAI API Key

```bash
# Set as environment variable (Linux/Mac)
export OPENAI_API_KEY='your-api-key-here'

# Or Windows
set OPENAI_API_KEY=your-api-key-here

# Or create a .env file
echo "OPENAI_API_KEY=your-api-key-here" > .env
```

## Quick Start

### Interactive Mode

```bash
# Make sure your API key is set
export OPENAI_API_KEY='your-key'

# Launch the agent
computer-use-agent
```

Try natural language commands:
```
agent> open the browser and search for python tutorials
agent> create a file called meeting-notes.txt in documents
agent> check system status and list running applications
agent> status
agent> exit
```

### Single Command

```bash
computer-use-agent --command "create a file called report.txt"
```

### Batch Mode

```bash
computer-use-agent --batch \
  "open the browser" \
  "check system status" \
  "list files in documents"
```

### Demo Mode

```bash
computer-use-agent --demo
```

## Usage

### As a Python Library

```python
import os
from computer_use_agent import DesktopAgent

# Set API key
os.environ['OPENAI_API_KEY'] = 'your-key-here'

# Create agent (automatically uses OpenAI)
agent = DesktopAgent()

# Process a command - OpenAI determines what to do
task = agent.process_command("open the browser and search for AI agents")

# Check results
if task.status.value == 'completed':
    print(f"Success: {task.result}")
else:
    print(f"Failed: {task.error}")

# View agent dashboard
print(agent.display_dashboard())
```

### Advanced: Custom OpenAI Client

```python
from computer_use_agent import DesktopAgent, OpenAIClient

# Create custom OpenAI client
openai_client = OpenAIClient(
    api_key='your-key',
    model='gpt-4o',  # or gpt-4-turbo, etc.
    organization='your-org-id'  # optional
)

# Create agent with custom client
agent = DesktopAgent(openai_client=openai_client)

# Now use the agent
task = agent.process_command("your command")
```

### Multi-Turn Conversations

The agent maintains conversation context:

```python
agent = DesktopAgent()

# First command
agent.process_command("create a file called notes.txt")

# Second command - OpenAI remembers the context
agent.process_command("now list all files to confirm it was created")

# Third command - can reference previous actions
agent.process_command("delete the file we just created")
```

## Configuration

### Environment Variables

```bash
# Required
OPENAI_API_KEY=your-api-key              # OpenAI API key

# Optional
OPENAI_MODEL=gpt-4o                      # Model to use (default: gpt-4o)
OPENAI_ORGANIZATION=org-xxx              # Organization ID (optional)

# Agent Settings
AGENT_LOG_LEVEL=INFO                     # Logging level
AGENT_LOG_FILE=/var/log/agent.log       # Log file path
AGENT_CONSOLE_LOG=true                   # Console logging
AGENT_MAX_HISTORY=100                    # Max task history
AGENT_SIM_DELAY=0.1                      # Simulation delay
```

### Configuration File

Create a `.env` file:

```env
OPENAI_API_KEY=sk-proj-xxx...
OPENAI_MODEL=gpt-4o
AGENT_LOG_LEVEL=DEBUG
```

## Architecture

### How It Works

```
┌─────────────┐
│ User Command│
└──────┬──────┘
       │
       ▼
┌─────────────────────┐
│   OpenAI API        │
│  (Reasoning &       │
│   Tool Selection)   │
└──────┬──────────────┘
       │
       ▼
┌──────────────────────┐
│  Tool Execution      │
│ (Desktop Operations) │
└──────┬───────────────┘
       │
       ▼
┌──────────────┐
│   Results    │
└──────────────┘
```

### Project Structure

```
computer_use_agent/
├── src/computer_use_agent/
│   ├── __init__.py              # Package entry point
│   ├── cli.py                   # CLI interface
│   ├── models/
│   │   └── task.py              # Task data models
│   ├── core/
│   │   ├── agent.py             # Main agent with OpenAI
│   │   └── desktop.py           # Virtual desktop
│   ├── openai_integration/
│   │   ├── client.py            # OpenAI client wrapper
│   │   └── tools.py             # Tool definitions
│   └── config/
│       ├── settings.py          # Configuration
│       └── logging_config.py    # Logging setup
├── tests/                       # Test suite
├── examples/                    # Example scripts
└── docs/                        # Documentation
```

### OpenAI Tool Definitions

The agent defines 9 tools for OpenAI:

1. **launch_application**: Open desktop apps
2. **close_application**: Close running apps
3. **create_file**: Create new files
4. **delete_file**: Remove files
5. **list_files**: List directory contents
6. **open_file**: Open existing files
7. **navigate_browser**: Browse URLs or search
8. **get_system_status**: Check system resources
9. **get_running_applications**: List active apps

OpenAI decides which tools to call based on the user's intent.

## Examples

### Example 1: File Management

```python
from computer_use_agent import DesktopAgent
import os

os.environ['OPENAI_API_KEY'] = 'your-key'
agent = DesktopAgent()

# OpenAI understands complex commands
task = agent.process_command(
    "create three files: todo.txt, notes.txt, and ideas.txt in documents"
)
print(task.result)
```

### Example 2: Research Workflow

```python
# Multi-step task - OpenAI orchestrates the tools
task = agent.process_command(
    "open the browser, search for Python best practices, "
    "then create a file called research-notes.txt"
)
print(task.result)
```

### Example 3: System Monitoring

```python
# Natural language system checks
task = agent.process_command(
    "check if CPU usage is high and list all running applications"
)
print(task.result)
```

## CLI Reference

### Commands

```bash
computer-use-agent [OPTIONS]

Options:
  -i, --interactive           Interactive mode (default)
  -c, --command CMD          Execute a single command
  -b, --batch CMD1 CMD2...   Execute multiple commands
  -d, --demo                 Run demonstration
  --log-level LEVEL          Set logging level
  --version                  Show version
  -h, --help                 Show help
```

### Interactive Mode Commands

- `<command>` - Execute any natural language command
- `status` - Display agent dashboard
- `clear` - Clear history and conversation
- `demo` - Run demonstration
- `help` - Show help
- `exit` - Quit

## Development

### Setup Development Environment

```bash
git clone https://github.com/example/computer-use-agent.git
cd computer-use-agent

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install with dev dependencies
pip install -e ".[dev]"
```

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=computer_use_agent

# Run specific test file
pytest tests/unit/test_task.py
```

### Code Quality

```bash
# Format code
black src/ tests/

# Lint code
ruff check src/ tests/

# Type check
mypy src/
```

## Supported Models

The agent works with OpenAI models that support function calling:

- **gpt-4o** (recommended) - Best balance of speed and capability
- **gpt-4-turbo** - Fast and capable
- **gpt-4** - Most capable
- **gpt-3.5-turbo** - Faster, lower cost

Set via `OPENAI_MODEL` environment variable.

## Troubleshooting

### "OpenAI API key is required" Error

Make sure your API key is set:
```bash
export OPENAI_API_KEY='your-key-here'
```

### Rate Limits

If you hit rate limits, the agent will raise an exception. Consider:
- Using a different model tier
- Adding retry logic
- Reducing request frequency

### Conversation Context Too Long

Clear history periodically:
```python
agent.clear_history()
```

## Design Principles

Following Guido van Rossum's Python philosophy:

- **Let OpenAI handle reasoning** - Don't reinvent natural language understanding
- **Explicit tool definitions** - Clear, typed function signatures
- **Simple is better than complex** - Straightforward architecture
- **Readability counts** - Clean, well-documented code
- **Type hints everywhere** - Full PEP 484 compliance

## Contributing

Contributions are welcome! Please:

1. Follow PEP 8 style guidelines
2. Add type hints to all functions
3. Write comprehensive docstrings
4. Include tests for new features
5. Update documentation

## License

MIT License - see [LICENSE](LICENSE) file

## Changelog

### Version 2.0.0 (2024-10-26)

**Major Refactoring - OpenAI Integration**

- Added OpenAI Responses API integration
- Removed custom NLP processor (OpenAI handles this)
- Removed custom task executor (integrated into agent)
- Added OpenAI tool calling with 9 defined tools
- Added conversation context management
- Updated all documentation for OpenAI usage
- Added `openai` as dependency
- Improved error handling and logging
- Updated CLI with OpenAI-specific messages

**Breaking Changes:**
- Requires `OPENAI_API_KEY` environment variable
- Removed `NLPProcessor` class (no longer needed)
- Removed `TaskExecutor` class (integrated into agent)
- Changed from pattern matching to OpenAI reasoning

### Version 1.0.0 (2024-10-25)

- Initial release with custom NLP
- Virtual desktop simulation
- Pattern-based command processing
- Zero dependencies

## Acknowledgments

- Powered by [OpenAI's Responses API](https://platform.openai.com/docs/api-reference/responses)
- Inspired by MarkTechPost's computer use agent tutorial
- Built following Guido van Rossum's Python design principles
- Designed for production use with OpenAI integration

## Support

- **Issues**: [GitHub Issues](https://github.com/example/computer-use-agent/issues)
- **Documentation**: See `docs/` directory
- **Examples**: See `examples/` directory
- **OpenAI Docs**: [platform.openai.com/docs](https://platform.openai.com/docs)

---

**Note**: This agent runs in a simulated desktop environment. For production use with real desktop automation, consider security implications and proper sandboxing.
