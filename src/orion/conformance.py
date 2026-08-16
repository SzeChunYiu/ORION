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


def violations(findings: Sequence[ConformanceFinding]) -> tuple[ConformanceFinding, ...]:
    return tuple(item for item in findings if item.verdict is ConformanceVerdict.VIOLATED)


__all__ = [
    "ConformanceFinding",
    "ConformanceVerdict",
    "check_annotator_independence",
    "check_papers",
    "check_stochastic_repeats",
    "violations",
]
