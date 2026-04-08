"""
Smoke test for the CLI experiment runner.
"""

from __future__ import annotations

import subprocess
import sys


def test_cli_runs_without_error():
    result = subprocess.run(
        [sys.executable, "-m", "src.cli.run_experiment"],
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0
    assert "Monte Carlo Results" in result.stdout
