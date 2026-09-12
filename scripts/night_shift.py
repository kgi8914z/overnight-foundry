from __future__ import annotations

import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
STEPS = [
    "validate.py",
    "collect_pypi_updates.py",
    "scout.py",
    "measure.py",
    "approvals.py",
    "brief.py",
    "render_dashboard.py",
]


def main() -> int:
    for name in STEPS:
        print(f"== {name}")
        proc = subprocess.run([sys.executable, str(Path(__file__).with_name(name))], cwd=ROOT)
        if proc.returncode != 0:
            return proc.returncode
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
