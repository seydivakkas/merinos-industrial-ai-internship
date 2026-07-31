"""
test_cli.py - Unit test for CLI interface execution.
"""

import subprocess
import sys


def test_cli_runs():
    """Verify that CLI module executes and outputs usage information cleanly."""
    result = subprocess.run(
        [sys.executable, "-m", "day10.mini_project.src.cli", "--help"],
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0
    assert "Merinos Carpet Perspective Rectification" in result.stdout
