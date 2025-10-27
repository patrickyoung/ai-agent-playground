"""Basic usage examples for the Computer Use Agent.

This script demonstrates common use cases and patterns.
"""

from computer_use_agent import DesktopAgent


def example_basic_commands() -> None:
    """Demonstrate basic command execution."""
    print('=' * 60)
    print('EXAMPLE 1: Basic Commands')
    print('=' * 60)

    agent = DesktopAgent()

    # Execute various commands
    commands = [
        'open the browser',
        'create a file called meeting-notes.txt',
        'check system status',
        'list files in documents',
    ]

    for cmd in commands:
        print(f'\nExecuting: {cmd}')
        task = agent.process_command(cmd)
        print(f'Status: {task.status.value}')
        print(f'Result: {task.result or task.error}')


def example_statistics() -> None:
    """Demonstrate statistics tracking."""
    print('\n' + '=' * 60)
    print('EXAMPLE 2: Statistics Tracking')
    print('=' * 60)

    agent = DesktopAgent()

    # Execute multiple commands
    agent.process_command('open the browser')
    agent.process_command('launch text editor')
    agent.process_command('check system status')

    # Get statistics
    stats = agent.get_statistics_summary()

    print(f'\nTotal tasks: {stats["total_tasks"]}')
    print(f'Completed: {stats["completed_tasks"]}')
    print(f'Success rate: {stats["success_rate"]}%')
    print(f'Avg execution time: {stats["average_execution_time"]}s')


def example_desktop_state() -> None:
    """Demonstrate desktop state inspection."""
    print('\n' + '=' * 60)
    print('EXAMPLE 3: Desktop State Inspection')
    print('=' * 60)

    agent = DesktopAgent()

    # Launch some applications
    agent.process_command('launch browser')
    agent.process_command('open text editor')

    # Get desktop state
    state = agent.get_desktop_state()

    print(f'\nRunning applications: {", ".join(state["running_applications"])}')
    print(f'Active window: {state["active_window"]}')
    print(f'CPU usage: {state["system_info"]["cpu_usage"]}%')
    print(f'Memory usage: {state["system_info"]["memory_usage"]}%')


def example_error_handling() -> None:
    """Demonstrate error handling."""
    print('\n' + '=' * 60)
    print('EXAMPLE 4: Error Handling')
    print('=' * 60)

    agent = DesktopAgent()

    # Try to open a non-existent file
    task = agent.process_command('open nonexistent.txt')

    if task.status.value == 'failed':
        print(f'\nTask failed as expected')
        print(f'Error: {task.error}')
    else:
        print(f'\nTask succeeded: {task.result}')


def example_batch_processing() -> None:
    """Demonstrate batch command processing."""
    print('\n' + '=' * 60)
    print('EXAMPLE 5: Batch Processing')
    print('=' * 60)

    agent = DesktopAgent()

    commands = [
        'open the browser',
        'search for python tutorials',
        'create a file called notes.txt',
        'launch text editor',
        'check system status',
    ]

    print(f'\nProcessing {len(commands)} commands...\n')
    tasks = agent.process_batch(commands)

    for i, task in enumerate(tasks, 1):
        status_symbol = '✓' if task.status.value == 'completed' else '✗'
        print(f'{i}. [{status_symbol}] {task.command[:40]}...')


def example_dashboard() -> None:
    """Demonstrate dashboard display."""
    print('\n' + '=' * 60)
    print('EXAMPLE 6: Dashboard Display')
    print('=' * 60)

    agent = DesktopAgent()

    # Execute some commands
    agent.process_command('open the browser')
    agent.process_command('create a file called report.txt')
    agent.process_command('check system status')

    # Display dashboard
    print(agent.display_dashboard())


def main() -> None:
    """Run all examples."""
    print('\nCOMPUTER USE AGENT - USAGE EXAMPLES\n')

    example_basic_commands()
    example_statistics()
    example_desktop_state()
    example_error_handling()
    example_batch_processing()
    example_dashboard()

    print('\n' + '=' * 60)
    print('All examples completed!')
    print('=' * 60 + '\n')


if __name__ == '__main__':
    main()
