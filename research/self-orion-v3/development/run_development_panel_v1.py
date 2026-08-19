from __future__ import annotations

import argparse
import json
from pathlib import Path

from orion.study.p5.revision_level_v3_development import derive_development_summary

ROOT = Path(__file__).resolve().parents[3]
DEFAULT_SUITE = ROOT / "research" / "self-orion-v3" / "development" / "PROTECTED_DEVELOPMENT_SUITE_V1.json"
EXPECTED_TERMINAL = "T8_PROSPECTIVE_EXPERIMENT_IMPLEMENTED_CANNOT_CHECK_OUTCOME"


def derive(path: Path = DEFAULT_SUITE) -> dict[str, object]:
    suite = json.loads(path.read_text(encoding="utf-8"))
    return derive_development_summary(suite)


def main() -> None:
    parser = argparse.ArgumentParser(description="Replay the development-only Self-ORION V3 instrumentation panel.")
    parser.add_argument("--suite", type=Path, default=DEFAULT_SUITE)
    parser.add_argument("--output", type=Path)
    parser.add_argument("--check", action="store_true", help="Fail unless the bounded implementation-only terminal is reached.")
    args = parser.parse_args()

    summary = derive(args.suite)
    rendered = json.dumps(summary, indent=2, sort_keys=True) + "\n"
    if args.output is not None:
        args.output.write_text(rendered, encoding="utf-8")
    else:
        print(rendered, end="")

    if args.check:
        if summary.get("terminal") != EXPECTED_TERMINAL:
            raise SystemExit(f"development instrumentation terminal is {summary.get('terminal')!r}, expected {EXPECTED_TERMINAL!r}")
        if summary.get("scientific_result") != "NOT_RUN":
            raise SystemExit("development runner must never emit a scientific result")
        if summary.get("confirmatory_preflight", {}).get("status") != "CANNOT_CHECK":
            raise SystemExit("development runner expected current confirmatory preflight to remain CANNOT_CHECK")


if __name__ == "__main__":
    main()
