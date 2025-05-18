#!/usr/bin/env python
"""
Entry point for Django commands executed as Python modules.
This enables commands like `python -m runserver`.
"""

import os
import sys
from pathlib import Path


def main():
    """Determine the command to run and execute it."""
    # Get the command name from the entry point
    cmd_name = Path(sys.argv[0]).stem

    # Default to 'manage.py' if no specific command
    if cmd_name == "__main__":
        # When running as `python -m dashboard_project`, just pass control to manage.py
        from dashboard_project.manage import main as manage_main

        manage_main()
        return

    # Add current directory to path if needed
    cwd = str(Path.cwd())
    if cwd not in sys.path:
        sys.path.insert(0, cwd)

    # Set Django settings module
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "dashboard_project.settings")

    # For specific commands, insert the command name at the start of argv
    if cmd_name in [
        "runserver",
        "migrate",
        "makemigrations",
        "collectstatic",
        "createsuperuser",
        "shell",
        "test",
    ]:
        sys.argv.insert(1, cmd_name)

    # Execute the Django management command
    from django.core.management import execute_from_command_line

    execute_from_command_line(sys.argv)


if __name__ == "__main__":
    main()
