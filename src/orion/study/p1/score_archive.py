from __future__ import annotations

import argparse
import json
from collections.abc import Sequence
from pathlib import Path

from .cases import HiddenShiftCase, Split, load_cases
from .harness import RunStatus
from .systems import ResourceUse, SystemTrace
from .metrics import SystemRole, case_score_to_record, score_case
from .orion_system import ABLATION_IDS, FULL_ORION_ID

RUN_SCHEMA = "orion.p1.run-record.v1"
CASE_SCHEMA = "orion.p1.case-record.v1"


def _role(system_id: str) -> SystemRole:
    if system_id == FULL_ORION_ID:
        return SystemRole.SUBJECT
    if system_id in set(ABLATION_IDS):
        return SystemRole.ABLATION
    return SystemRole.BASELINE


def score_archive(
    run_records: Sequence[dict],
    cases: Sequence[HiddenShiftCase],
) -> list[dict]:
    """Turn raw run records into scored case records.

    This is the seam between the harness, which archives what each system did,
    and the table generator, which reads what each system scored. The two were
    built against separate fixtures and never met: the harness emits
    `run-record.v1` and the tables require `case-record.v1`, so a real archive
    was rejected as malformed. Nothing but an end-to-end run surfaces that.

    A run that did not complete becomes a CANNOT_CHECK score carrying its
    reason, never a zero — a system that could not be measured has not failed.
    """

    by_id = {case.case_id: case for case in cases}
    out: list[dict] = []
    for record in run_records:
        case = by_id.get(record["case_id"])
        if case is None:
            # An archived run whose case is not in the supplied suite cannot be
            # scored against gold. Dropping it silently would let a mismatched
            # suite look like a complete run, so it is refused loudly instead.
            raise ValueError(
                f"archived case {record['case_id']!r} is absent from the supplied suite; "
                "the archive and the suite disagree"
            )
        trace = _trace_from_payload(record.get("trace"))
        usable = record["status"] == RunStatus.OK.value and trace is not None
        score = score_case(
            case,
            trace if usable else None,
            system_id=record["system_id"],
            seed=record["seed"],
            system_role=_role(record["system_id"]),
            suite_fingerprint=record["suite_fingerprint"],
            subject_revision=record["subject_revision"],
            cannot_check_reason="" if usable else (record.get("error") or record["status"]),
            # The harness measured this; the system's self-reported wallclock is
            # 0.0 for every mechanical system, which would put the whole cost
            # frontier at the origin.
            elapsed_seconds=record.get("elapsed_seconds"),
        )
        out.append(case_score_to_record(score))
    return out


#: Keys the harness writes for every run. The archive carries no schema tag of
#: its own, so shape is the only identity available; requiring the full key set
#: means a truncated or foreign file is refused rather than half-read.
_RUN_KEYS = frozenset(
    {
        "case_id",
        "system_id",
        "seed",
        "status",
        "trace",
        "elapsed_seconds",
        "suite_fingerprint",
        "subject_revision",
        "protocol_id",
        "budget_class",
    }
)


def _read_runs(path: Path) -> list[dict]:
    payloads: list[dict] = []
    for number, line in enumerate(path.read_text().splitlines(), start=1):
        if not line.strip():
            continue
        payload = json.loads(line)
        missing = _RUN_KEYS.difference(payload)
        if missing:
            raise ValueError(
                f"{path}:{number} is not a P1 run record; missing {sorted(missing)}"
            )
        payloads.append(payload)
    return payloads


def _trace_from_payload(payload: dict | None) -> SystemTrace | None:
    if payload is None:
        return None
    resources = payload.get("resources") or {}
    return SystemTrace(
        case_id=payload["case_id"],
        system_id=payload["system_id"],
        seed=payload["seed"],
        reframed=payload["reframed"],
        responsibility_family=payload.get("responsibility_family", ""),
        target_coordinates=tuple(payload.get("target_coordinates", ())),
        reopened=tuple(payload.get("reopened", ())),
        root_solved=payload.get("root_solved", False),
        abstained=payload.get("abstained", False),
        invariant_violations=tuple(payload.get("invariant_violations", ())),
        authority_violations=tuple(payload.get("authority_violations", ())),
        max_recursion_depth=payload.get("max_recursion_depth", 0),
        resources=ResourceUse(**resources) if resources else ResourceUse(),
        notes=payload.get("notes", ""),
    )


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Score a P1 run archive into case records.")
    parser.add_argument("--runs", type=Path, required=True)
    parser.add_argument("--cases", type=Path, required=True)
    parser.add_argument("--split", choices=[s.value for s in Split], required=True)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args(argv)

    cases = load_cases(args.cases, split=Split(args.split))
    records = score_archive(_read_runs(args.runs), cases)
    args.out.write_text("".join(json.dumps(item, sort_keys=True) + "\n" for item in records))
    print(f"scored {len(records)} records from {len(cases)} cases -> {args.out}")
    return 0


__all__ = ["CASE_SCHEMA", "RUN_SCHEMA", "score_archive"]


if __name__ == "__main__":
    raise SystemExit(main())
