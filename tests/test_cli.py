import subprocess
import sys


def test_cli_help() -> None:
    p = subprocess.run([sys.executable, "-m", "influence_detection.cli", "--help"], capture_output=True, text=True)
    assert p.returncode == 0
    assert "usage" in p.stdout.lower()