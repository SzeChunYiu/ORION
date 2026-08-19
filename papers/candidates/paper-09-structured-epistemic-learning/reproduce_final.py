from __future__ import annotations

import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent


def run(script: str) -> None:
    subprocess.run([sys.executable, str(HERE / script)], cwd=HERE, check=True)


def main() -> None:
    # Order is deliberate and fail-closed: independently compare the immutable
    # official artifacts first, then bind/render only those verified artifacts,
    # and finally audit the manuscript that consumes the generated outputs.
    run("verify_official_results.py")
    run("build_evidence_summary.py")
    run("build_result_macros.py")
    run("build_headline_tables.py")
    run("audit_final_manuscript.py")
    print(
        "P9 final official verification, evidence summary, result macros, "
        "headline tables and manuscript audit regenerated successfully"
    )


if __name__ == "__main__":
    main()
