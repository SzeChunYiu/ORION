from __future__ import annotations

import json
import pathlib
from collections.abc import Sequence
from dataclasses import dataclass
from enum import Enum


class ConformanceVerdict(str, Enum):
    """Whether the artifacts on disk satisfy a quantity the protocol declared.

    Four defects found in one session shared a shape, and none of them was
    missing code:

    - the Phase-2 gate required ten frozen attacks and counted caller strings,
      while the canonical registry sat ten lines above it;
    - the trial runner grew a second archive reader while a validated one
      already existed in the module it called;
    - the support and influence axes were recorded on every grading and
      consulted by nothing;
    - P3's protocol requires two independent annotators, the agreement function
      takes two, and the corpus contains one.

    In each case the requirement was stated, the machinery to satisfy it
    existed, and nothing compared the two. A passing test suite cannot see this:
    every component is correct in isolation, and the fault is the absence of a
    comparison rather than the presence of a bug.
    """

    SATISFIED = "SATISFIED"
    VIOLATED = "VIOLATED"
    #: The protocol declares the quantity but the artifacts it would be checked
    #: against do not exist yet. Distinct from VIOLATED: nothing is wrong, and
    #: nothing is confirmed either.
    CANNOT_CHECK = "CANNOT_CHECK"


@dataclass(frozen=True)
class ConformanceFinding:
    paper_id: str
    requirement: str
    declared: object
    observed: object
    verdict: ConformanceVerdict
    detail: str


def _protocol(path: pathlib.Path) -> dict:
    try:
        return json.loads(path.read_text())
    except (OSError, json.JSONDecodeError):
        return {}


def check_annotator_independence(paper_root: pathlib.Path, paper_id: str) -> ConformanceFinding | None:
    """Distinct annotator identities present in the corpus.

    A protocol asking for independent labels is asking for disagreement to be
    observable. One annotator's labels record one reading, and the agreement
    statistic cannot be recovered afterwards from adjudicated output, because
    adjudication has already collapsed the disagreement it would measure.
    """

    annotations = paper_root / "gold" / "annotations"
    if not annotations.is_dir():
        return None
    identities = set()
    for path in annotations.glob("*.json"):
        marker = "annotator-"
        if marker in path.name:
            identities.add(path.name.split(marker, 1)[1].split(".", 1)[0])
    if not identities:
        return ConformanceFinding(
            paper_id, "independent_annotators", 2, 0, ConformanceVerdict.CANNOT_CHECK,
            "no annotator-tagged files found; nothing to compare",
        )
    satisfied = len(identities) >= 2
    return ConformanceFinding(
        paper_id, "independent_annotators", 2, len(identities),
        ConformanceVerdict.SATISFIED if satisfied else ConformanceVerdict.VIOLATED,
        f"annotator identities present: {sorted(identities)}"
        + ("" if satisfied else "; agreement is not computable on this corpus"),
    )


def check_stochastic_repeats(paper_root: pathlib.Path, paper_id: str, declared: int) -> ConformanceFinding | None:
    """Seeds actually present per (case, system) in an archived run."""

    archives = list((paper_root / "results" / "raw").glob("*_runs.jsonl")) if (
        paper_root / "results" / "raw"
    ).is_dir() else []
    if not archives:
        return ConformanceFinding(
            paper_id, "stochastic_repeats", declared, None, ConformanceVerdict.CANNOT_CHECK,
            "no archived run found; the declared repeat count has nothing to check against",
        )
    seeds: dict[tuple[str, str], set] = {}
    for archive in archives:
        for line in archive.read_text().splitlines():
            if not line.strip():
                continue
            try:
                record = json.loads(line)
            except json.JSONDecodeError:
                continue
            key = (record.get("case_id", ""), record.get("system_id", ""))
            seeds.setdefault(key, set()).add(record.get("seed"))
    if not seeds:
        return ConformanceFinding(
            paper_id, "stochastic_repeats", declared, 0, ConformanceVerdict.CANNOT_CHECK,
            "archive present but contains no run records",
        )
    observed = min(len(item) for item in seeds.values())
    return ConformanceFinding(
        paper_id, "stochastic_repeats", declared, observed,
        ConformanceVerdict.SATISFIED if observed >= declared else ConformanceVerdict.VIOLATED,
        f"minimum distinct seeds across {len(seeds)} (case, system) cells: {observed}",
    )


def check_papers(papers_root: pathlib.Path) -> tuple[ConformanceFinding, ...]:
    """Every declared quantity checked against what is on disk."""

    findings: list[ConformanceFinding] = []
    for protocol_path in sorted(papers_root.glob("*/protocol/PROTOCOL_V1.json")):
        paper_root = protocol_path.parent.parent
        protocol = _protocol(protocol_path)
        paper_id = protocol.get("paper_id") or paper_root.name
        declared_repeats = protocol.get("statistics", {}).get("stochastic_repeats")
        if declared_repeats is None:
            declared_repeats = protocol.get("stochastic_repeats")
        for finding in (
            check_annotator_independence(paper_root, paper_id),
            check_stochastic_repeats(paper_root, paper_id, declared_repeats)
            if isinstance(declared_repeats, int)
            else None,
        ):
            if finding is not None:
                findings.append(finding)
    return tuple(findings)


#: Violations that are known, owned and blocked on something outside this
#: repository. Keyed (paper_id, requirement) -> reason.
#:
#: A permanently red check gets ignored, and a silent waiver is worse than no
#: check at all. So a waiver behaves like a strict xfail: it suppresses the
#: failure while the violation persists, and FAILS THE RUN the moment the
#: violation clears — forcing the waiver to be deleted rather than left to rot
#: into a lie about the current state.
KNOWN_VIOLATIONS: dict[tuple[str, str], str] = {
    ("P3", "independent_annotators"): (
        "the corpus carries one annotator; a second independent pass is an "
        "external input this repository cannot generate for itself without "
        "inventing the disagreement it is meant to measure. Recorded on #158 "
        "and #100 as an external blocker."
    ),
}


def violations(findings: Sequence[ConformanceFinding]) -> tuple[ConformanceFinding, ...]:
    """Violations that are not waived."""

    return tuple(
        item
        for item in findings
        if item.verdict is ConformanceVerdict.VIOLATED
        and (item.paper_id, item.requirement) not in KNOWN_VIOLATIONS
    )


def stale_waivers(findings: Sequence[ConformanceFinding]) -> tuple[tuple[str, str], ...]:
    """Waivers whose violation no longer occurs.

    A waiver for something that is now satisfied misdescribes the repository,
    so it fails the run. This is what stops the waiver list becoming a place
    where fixed problems go to be remembered as broken.
    """

    violated = {
        (item.paper_id, item.requirement)
        for item in findings
        if item.verdict is ConformanceVerdict.VIOLATED
    }
    checked = {(item.paper_id, item.requirement) for item in findings}
    return tuple(sorted(key for key in KNOWN_VIOLATIONS if key in checked and key not in violated))


def main(argv: Sequence[str] | None = None) -> int:
    """Report every declared quantity against the artifacts on disk.

    Exit 0 when nothing is violated, 1 when something is. CANNOT_CHECK does not
    fail the run: a declared quantity with no artifact yet is unknown, not
    wrong, and failing on it would make every unstarted paper block the build
    and get this switched off within a day.
    """

    import argparse

    parser = argparse.ArgumentParser(description="Check declared protocol quantities.")
    parser.add_argument("--papers", type=pathlib.Path, default=pathlib.Path("papers"))
    args = parser.parse_args(argv)

    findings = check_papers(args.papers)
    if not findings:
        print(f"no protocols found under {args.papers}", flush=True)
        return 1
    for item in sorted(findings, key=lambda f: (f.paper_id, f.requirement)):
        print(f"[{item.verdict.value:12s}] {item.paper_id:4s} {item.requirement:24s} "
              f"declared={item.declared} observed={item.observed}")
        print(f"               {item.detail}")
    failed = violations(findings)
    waived = [
        item
        for item in findings
        if item.verdict is ConformanceVerdict.VIOLATED
        and (item.paper_id, item.requirement) in KNOWN_VIOLATIONS
    ]
    for item in waived:
        print(f"[WAIVED      ] {item.paper_id:4s} {item.requirement}")
        print(f"               {KNOWN_VIOLATIONS[(item.paper_id, item.requirement)]}")
    stale = stale_waivers(findings)
    for key in stale:
        print(f"[STALE WAIVER] {key[0]} {key[1]} is satisfied; delete its waiver")
    print(
        f"\n{len(findings)} checked, {len(failed)} violated, "
        f"{len(waived)} waived, {len(stale)} stale",
        flush=True,
    )
    return 1 if (failed or stale) else 0


__all__ = [
    "ConformanceFinding",
    "ConformanceVerdict",
    "check_annotator_independence",
    "check_papers",
    "KNOWN_VIOLATIONS",
    "check_stochastic_repeats",
    "stale_waivers",
    "main",
    "violations",
]


if __name__ == "__main__":
    raise SystemExit(main())
