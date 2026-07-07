"""Tests for the real acquisition training entry point."""

import subprocess
import sys
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
SCRIPT_PATH = PROJECT_ROOT / "scripts" / "acquisition" / "run_acquisition_training.py"


def test_acquisition_training_help_runs():
    result = subprocess.run(
        [sys.executable, str(SCRIPT_PATH), "--help"],
        capture_output=True,
        text=True,
        check=False,
    )

    assert result.returncode == 0
    assert "Run real multimodal acquisition" in result.stdout


def test_acquisition_training_dry_run_runs():
    result = subprocess.run(
        [
            sys.executable,
            str(SCRIPT_PATH),
            "--subject-id",
            "sub-test001",
            "--session-id",
            "ses-01",
            "--movement-block",
            "Codo",
            "--total-trials",
            "4",
            "--timestamp",
            "20260706_120000",
        ],
        capture_output=True,
        text=True,
        check=False,
    )

    assert result.returncode == 0
    assert "Acquisition training plan" in result.stdout
    assert "Dry run completed" in result.stdout
    assert "sub-test001" in result.stdout
