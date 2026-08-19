from __future__ import annotations

import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent


def run(script: str) -> None:
    subprocess.run([sys.executable, str(HERE / script)], cwd=HERE, check=True)


def main() -> None:
    run("build_evidence_summary.py")
    run("build_result_macros.py")
    run("build_headline_tables.py")
    print(
        "P9 final evidence summary, LaTeX result macros and headline tables regenerated successfully"
    )


if __name__ == "__main__":
    main()
