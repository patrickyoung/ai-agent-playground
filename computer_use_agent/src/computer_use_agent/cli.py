"""Command-line interface for the computer use agent.

This module provides both interactive and batch command processing modes.
Following the principle of simple, clean CLI design.
"""

import argparse
import sys
from typing import List, NoReturn, Optional

from computer_use_agent import DesktopAgent
from computer_use_agent.config import get_settings, setup_logging
from computer_use_agent.models.task import TaskStatus


def print_banner() -> None:
    """Display the application banner."""
    banner = """
    ╔══════════════════════════════════════════════════════════╗
    ║         COMPUTER USE AGENT - Desktop Automation          ║
    ║              Production-Ready AI Agent System            ║
    ╚══════════════════════════════════════════════════════════╝
    """
    print(banner)


def print_task_result(task) -> None:
    """Print formatted task execution result.

    Args:
        task: The executed task to display.
    """
    status_symbol = '✓' if task.status == TaskStatus.COMPLETED else '✗'
    status_color = '\033[92m' if task.status == TaskStatus.COMPLETED else '\033[91m'
    reset_color = '\033[0m'

    print(f'\n{status_color}[{status_symbol}] Task {task.status.value.upper()}{reset_color}')
    print(f'Command: {task.command}')
    print(f'Type: {task.task_type.value}')
    print(f'Confidence: {task.confidence:.2f}')
    print(f'Execution Time: {task.execution_time:.3f}s')

    if task.status == TaskStatus.COMPLETED:
        print(f'Result: {task.result}')
    else:
        print(f'Error: {task.error}')

    if task.parameters:
        print(f'Parameters: {task.parameters}')


def run_interactive_mode(agent: DesktopAgent) -> NoReturn:
    """Run the agent in interactive mode.

    Args:
        agent: The desktop agent instance.
    """
    print('\nInteractive Mode - Type "help" for commands, "exit" to quit\n')

    while True:
        try:
            # Get user input
            command = input('agent> ').strip()

            if not command:
                continue

            # Handle special commands
            if command.lower() == 'exit':
                print('Goodbye!')
                sys.exit(0)

            elif command.lower() == 'help':
                print_help()

            elif command.lower() == 'status':
                print(agent.display_dashboard())

            elif command.lower() == 'clear':
                agent.clear_history()
                agent.reset_statistics()
                print('History and statistics cleared.')

            elif command.lower().startswith('demo'):
                run_demo(agent)

            else:
                # Process the command
                task = agent.process_command(command)
                print_task_result(task)

        except KeyboardInterrupt:
            print('\n\nGoodbye!')
            sys.exit(0)

        except Exception as e:
            print(f'\n\033[91mError: {e}\033[0m')


def print_help() -> None:
    """Print help information for interactive mode."""
    help_text = """
    Available Commands:
    -------------------
    <natural language>  - Execute a command (e.g., "open the browser")
    status              - Display agent dashboard and statistics
    clear               - Clear history and reset statistics
    demo                - Run demonstration commands
    help                - Show this help message
    exit                - Exit the application

    Example Commands:
    -----------------
    - open the browser
    - create a file called report.txt
    - check system status
    - search for python tutorials
    - list files in documents
    - launch text editor
    """
    print(help_text)


def run_demo(agent: DesktopAgent) -> None:
    """Run a demonstration with sample commands.

    Args:
        agent: The desktop agent instance.
    """
    demo_commands = [
        'open the browser',
        'create a file called demo.txt',
        'check system status',
        'launch text editor',
        'list files in documents',
        'search for python programming',
    ]

    print('\n' + '=' * 60)
    print('RUNNING DEMONSTRATION')
    print('=' * 60)

    for i, cmd in enumerate(demo_commands, 1):
        print(f'\n[{i}/{len(demo_commands)}] Executing: {cmd}')
        task = agent.process_command(cmd)
        print(f'    → {task.status.value}: {task.result or task.error}')

    print('\n' + '=' * 60)
    print('DEMONSTRATION COMPLETE')
    print('=' * 60)
    print(agent.display_dashboard())


def run_batch_mode(agent: DesktopAgent, commands: List[str]) -> None:
    """Run the agent in batch mode with a list of commands.

    Args:
        agent: The desktop agent instance.
        commands: List of commands to execute.
    """
    print(f'\nBatch Mode - Processing {len(commands)} commands\n')

    tasks = agent.process_batch(commands)

    print('\n' + '=' * 60)
    print('BATCH EXECUTION RESULTS')
    print('=' * 60)

    for i, task in enumerate(tasks, 1):
        status_symbol = '✓' if task.status == TaskStatus.COMPLETED else '✗'
        print(f'[{i}] [{status_symbol}] {task.command}')
        print(f'    → {task.result or task.error}')

    print('\n' + agent.display_dashboard())


def main() -> None:
    """Main entry point for the CLI application."""
    parser = argparse.ArgumentParser(
        description='Computer Use Agent - AI-powered desktop automation',
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )

    parser.add_argument(
        '-i',
        '--interactive',
        action='store_true',
        help='Run in interactive mode',
    )

    parser.add_argument(
        '-c',
        '--command',
        type=str,
        help='Execute a single command',
    )

    parser.add_argument(
        '-b',
        '--batch',
        type=str,
        nargs='+',
        help='Execute multiple commands in batch',
    )

    parser.add_argument(
        '-d',
        '--demo',
        action='store_true',
        help='Run demonstration mode',
    )

    parser.add_argument(
        '--log-level',
        type=str,
        choices=['DEBUG', 'INFO', 'WARNING', 'ERROR'],
        help='Set logging level',
    )

    parser.add_argument(
        '--version',
        action='version',
        version='Computer Use Agent v1.0.0',
    )

    args = parser.parse_args()

    # Setup logging
    settings = get_settings()
    log_level = args.log_level or settings.log_level
    setup_logging(
        level=log_level,
        log_file=settings.log_file,
        enable_console=settings.enable_console_log,
    )

    # Print banner
    print_banner()

    # Create agent
    agent = DesktopAgent()

    # Determine mode
    if args.demo:
        run_demo(agent)

    elif args.command:
        task = agent.process_command(args.command)
        print_task_result(task)

    elif args.batch:
        run_batch_mode(agent, args.batch)

    elif args.interactive:
        run_interactive_mode(agent)

    else:
        # Default to interactive mode
        run_interactive_mode(agent)


if __name__ == '__main__':
    main()
