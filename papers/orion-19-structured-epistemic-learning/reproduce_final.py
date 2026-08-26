from __future__ import annotations

import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent


def run(script: str) -> None:
    subprocess.run([sys.executable, str(HERE / script)], cwd=HERE, check=True)


def main() -> None:
    # Order is deliberate and fail-closed.  Derived statistics are regenerated
    # from the immutable D1 protected predictions before any paper artifact can
    # consume them; official artifacts are then independently compared, bound,
    # rendered, and finally audited in the manuscript.
    run("analyze_d1_paired_effects.py")
    run("verify_official_results.py")
    run("build_evidence_summary.py")
    run("build_result_macros.py")
    run("build_headline_tables.py")
    run("audit_final_manuscript.py")
    print(
        "P9 paired effects, official verification, evidence summary, result macros, "
        "headline tables and manuscript audit regenerated successfully"
    )


if __name__ == "__main__":
    main()
