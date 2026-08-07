"""Run the repository validation contract used locally and by agents."""

from __future__ import annotations

import subprocess
import sys


def run(command: list[str]) -> None:
    print("+", " ".join(command), flush=True)
    subprocess.run(command, check=True)


def main() -> int:
    run([sys.executable, "-m", "compileall", "-q", "src", "tests", "examples", "scripts"])
    run([sys.executable, "-m", "pytest", "-q"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
