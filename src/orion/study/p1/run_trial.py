from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
from collections.abc import Sequence
from pathlib import Path

from .arm_validity import assess_arm_discrimination
from .baselines import baseline_systems
from .cases import Split, load_cases, suite_fingerprint
from .execution_freeze import build_manifest
from .harness import run_study
from .orion_system import orion_systems
from .provider import CREDENTIAL_ENV_VAR, ProviderBackedSystem, credential_present
from .score_archive import read_runs, score_archive

REPO_ROOT = Path(__file__).resolve().parents[4]
CASES_ROOT = REPO_ROOT / "papers/orion-11-recursive-epistemic-reconstruction/protocol/cases"
RESULTS_ROOT = REPO_ROOT / "papers/orion-11-recursive-epistemic-reconstruction/results"

EXIT_OK = 0
EXIT_ERROR = 2
EXIT_CANNOT_CHECK = 3


def _systems(*, live: bool, transcript_path: Path | None = None) -> list:
    """The compared systems.

    The live arm is one additional system, not a replacement: the mechanical
    arm still runs, so a live failure degrades the study rather than voiding it.

    `transcript_path` is where the live arm archives its raw completions. A
    campaign that parses model answers without keeping the text it parsed
    cannot be audited after the fact — that was half of issue #985 — so the
    path is wired here rather than left to the caller to remember.
    """

    systems = [*baseline_systems(), *orion_systems()]
    if live:
        systems.append(ProviderBackedSystem(transcript_path=transcript_path))
    return systems


def run(
    split: Split,
    *,
    live: bool,
    seeds: Sequence[int] | None = None,
    out_root: Path = RESULTS_ROOT,
) -> int:
    cases = load_cases(CASES_ROOT, split=split)
    if not cases:
        print(f"no cases found for split {split.value}", file=sys.stderr)
        return EXIT_ERROR

    fingerprint = suite_fingerprint(cases)
    transcript_path = out_root / "raw" / f"{split.value.lower()}_live_transcripts.jsonl"
    systems = _systems(live=live, transcript_path=transcript_path)
    print(f"split          : {split.value}  ({len(cases)} cases)")
    print(f"suite          : {fingerprint}")
    print(f"systems        : {len(systems)}")
    print(f"live arm       : {'ON' if live else 'off'}")
    if live and not credential_present():
        # Refused before any case runs. Starting a trial that will record
        # CANNOT_CHECK on every live cell wastes the mechanical arm's run too,
        # and a partially-live archive is harder to reason about than none.
        print(
            f"\nrefusing to start: --live was requested but {CREDENTIAL_ENV_VAR} is not set.\n"
            "Every live cell would record CANNOT_CHECK. Export the credential and re-run.",
            file=sys.stderr,
        )
        return EXIT_CANNOT_CHECK

    # The frozen TEST split may not be run until every scientific identity is
    # bound. Once outcomes are visible, each remaining design choice — which
    # margin, which comparator, whether the suite is large enough — can be made
    # knowing which answer flatters the result, so the freeze is what makes
    # `outcome_accessed: false` mean anything.
    #
    # PILOT is deliberately exempt: the protocol designates it for debugging and
    # variance estimation, and gating it would make the freeze impossible to
    # reach, since the pilot is how the machinery gets working in the first
    # place.
    if split is Split.TEST:
        manifest = build_manifest()
        print(f"execution freeze: {manifest.status.value}")
        if not manifest.permits_outcome_access:
            print(
                "\nrefusing to run the frozen TEST split: "
                + ", ".join(manifest.unresolved or ("outcomes already accessed",)),
                file=sys.stderr,
            )
            return EXIT_CANNOT_CHECK

    raw = out_root / "raw"
    raw.mkdir(parents=True, exist_ok=True)
    archive_path = raw / f"{split.value.lower()}_runs.jsonl"
    scored_path = raw / f"{split.value.lower()}_scored.jsonl"

    archive = run_study(cases, systems, seeds=seeds, archive_path=archive_path)
    print(f"\nran            : {len(archive.records)} records -> {archive_path}")
    if live:
        print(f"live transcripts: {transcript_path}")

    # The validated reader, not a second local one. run_trial grew its own
    # `_reload` while score_archive already had a reader that checks the full
    # harness key set — so the one-command path, the one anyone actually uses,
    # skipped the validation entirely and would half-read a truncated archive
    # into confident numbers. Two readers, one validated, and the unvalidated
    # one on the hot path.
    records = score_archive(read_runs(archive_path), cases)
    scored_path.write_text(
        "".join(json.dumps(item, sort_keys=True) + "\n" for item in records)
    )
    print(f"scored         : {len(records)} records -> {scored_path}")

    # Arm validity before any comparison is reported. A study whose systems all
    # behaved identically has measured nothing, and a paired bootstrap over
    # identical vectors returns zero by construction rather than by observation.
    outcomes: dict[str, list] = {}
    for record in records:
        outcomes.setdefault(record["system_id"], []).append(
            (record["case_id"], record.get("seed"), record.get("root_success"))
        )
    arm = assess_arm_discrimination(
        {key: [str(item) for item in sorted(value)] for key, value in outcomes.items()}
    )
    print(f"arm validity   : {arm.verdict.value} ({arm.distinct_behaviour_groups} behaviour groups)")
    if not arm.permits_system_comparison:
        print(f"                 {arm.reasons[0] if arm.reasons else ''}", file=sys.stderr)

    print("\ngenerating tables...")
    result = subprocess.run(
        [
            sys.executable, "-m", "orion.study.p1.tables",
            "--archive", str(scored_path),
            "--out", str(out_root),
        ],
        cwd=REPO_ROOT,
        env={**os.environ, "PYTHONPATH": str(REPO_ROOT / "src")},
    )
    if result.returncode == EXIT_CANNOT_CHECK:
        print("\ntables: CANNOT_CHECK — no publishable numbers yet.", file=sys.stderr)
        return EXIT_CANNOT_CHECK
    if result.returncode != 0:
        return EXIT_ERROR
    print(f"\ndone. tables in {out_root}")
    return EXIT_OK


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Run the ORION-P1 trial end to end: systems -> archive -> scores -> tables."
    )
    parser.add_argument("--split", choices=[item.value for item in Split], default=Split.PILOT.value)
    parser.add_argument(
        "--live",
        action="store_true",
        help=f"include the live provider arm; requires {CREDENTIAL_ENV_VAR}",
    )
    parser.add_argument("--seeds", type=int, nargs="*", default=None)
    parser.add_argument("--out", type=Path, default=RESULTS_ROOT)
    args = parser.parse_args(argv)
    return run(Split(args.split), live=args.live, seeds=args.seeds, out_root=args.out)


__all__ = ["run"]


if __name__ == "__main__":
    raise SystemExit(main())
