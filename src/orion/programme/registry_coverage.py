"""Every registry in this programme is a partial list, and the gaps are where defects live.

:mod:`orion.programme.panel_resolution` reads a comparative panel and says what
its metrics can express --- whether a hypothesis was decided on an axis that
discriminates, or on one every arm scores identically. It is a good instrument.
It runs on whatever ``PUBLISHED_PANELS``, ``PUBLISHED_MARGIN_GATES`` and
``PUBLISHED_ABLATIONS`` name, and between them those three registries name seven
artifacts.

Nobody wrote down what they leave out, so nothing could notice.

Discovering the candidates mechanically --- a result artifact carrying both a
block of three or more named arms reporting shared numeric metrics *and* a
terminal or a gate table --- finds five across the papers. Three are registered.
The two that are not both publish a **positive** terminal:

``P14B_BALANCED_GOVERNANCE_RESULT_RECEIPT_V1.json``
    ``P14B_BALANCED_GOVERNANCE_SUPERIORITY_SUPPORTED``, five arms, eight gates all
    true. P14 is the paper that *invented*
    :mod:`orion.programme.gate_attainability`, and
    ``verify_p14_gate_attainability_v1.py`` drives that instrument over P14A and
    P14C. Its ``P14_GATE_ATTAINABILITY_ADJUDICATION_V1.json`` has a ``p14a`` key
    and a ``p14c`` key. There is no ``p14b``. Its docstring says no P14B
    threshold "is edited, re-run or relabelled" --- true, and it was never
    audited either. All five of P14B's arms report ``useful_discovery_recall``
    of 1.0, and the gate ``full_discovery_recall_one`` reads exactly that.

``METHOD_AUTHORITY_BENCH_SUMMARY_V1.json``
    ``P4_METHOD_AUTHORITY_SUPPORTED``, four arms, ten cases. Both reported
    metrics come back ``SEPARATED_WITHOUT_VARIATION``: two distinct values each,
    and both of them the metric's extremes. ``duplicate_arms`` returns
    ``provenance_only_policy`` and ``visible_success_policy`` --- indistinguishable
    on every metric the artifact reports, so the panel of four decides over
    three.

Neither of those is necessarily a wrong result. A benchmark on which the right
answer is reachable and the baselines fail is informative even when every rate
is 0.0 or 1.0, and the method-authority artifact states an honest ceiling. The
finding is not that these claims are false. It is that **the instrument built to
ask whether they could have come out otherwise was never pointed at them**, and
that no artifact recorded the omission, because a registry that lists what it
covers implies nothing about what it does not.

So this module gives the registries a denominator, the same way
:mod:`orion.programme.failure_class_coverage` gives the failure record one. A
discovered panel that no registry declares is
:data:`~orion.programme.records.Outcome.CANNOT_CHECK`: not a defect, and not
clean either --- unexamined, which is a third thing and needs its own name to
stay visible.

Discovery is deliberately conservative. It requires a terminal or a gate table
alongside the panel, because a bare table of per-arm numbers is often an
intermediate rather than a decision, and a scan that reported every one of those
would bury the two that matter. The cost is that a decision recorded in a shape
this does not recognise stays invisible, which is why
:func:`coverage_report` reports the discovery rule it used rather than implying
it found everything.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable, Iterator, Mapping

from orion.programme.records import Outcome

__all__ = [
    "CoverageReport",
    "PanelCandidate",
    "SYSTEMS_KEYS",
    "TERMINAL_KEYS",
    "coverage_report",
    "declared_artifacts",
    "discover_candidates",
    "panel_block",
]

SCHEMA_VERSION = "orion.programme.registry-coverage.v1"

#: Blocks a result artifact keeps its per-arm rates under.
SYSTEMS_KEYS: tuple[str, ...] = ("summary", "systems", "arms", "by_arm", "panel")

#: Keys whose presence means the artifact decided something.
TERMINAL_KEYS: tuple[str, ...] = ("terminal", "verdict", "gates")

#: Fewer arms than this is not a panel; it is a measurement of one system.
MIN_ARMS = 3


@dataclass(frozen=True)
class PanelCandidate:
    """A published artifact that decided something over a comparative panel."""

    artifact: str
    paper_id: str
    systems_key: str
    arms: int
    metrics: tuple[str, ...]
    terminal: str | None
    declared: bool

    @property
    def outcome(self) -> Outcome:
        """Registered panels have been read; unregistered ones have not."""

        return Outcome.PASS if self.declared else Outcome.CANNOT_CHECK

    @property
    def claims_support(self) -> bool:
        """A positive terminal. An unexamined one of these is the sharper case."""

        return bool(self.terminal) and "SUPPORTED" in (self.terminal or "").upper()


def panel_block(document: Mapping[str, Any]) -> tuple[str, dict[str, Any], tuple[str, ...]] | None:
    """The artifact's per-arm block, if it has one, with the metrics all arms share.

    Metrics are intersected rather than unioned: an arm that does not report a
    metric has not scored zero on it, and a union would invent variation from
    absence.
    """

    for key in SYSTEMS_KEYS:
        block = document.get(key)
        if not isinstance(block, dict):
            continue
        arms = {name: rates for name, rates in block.items() if isinstance(rates, dict)}
        if len(arms) < MIN_ARMS:
            continue
        shared: set[str] | None = None
        for rates in arms.values():
            numeric = {
                metric
                for metric, value in rates.items()
                if isinstance(value, (int, float)) and not isinstance(value, bool)
            }
            shared = numeric if shared is None else (shared & numeric)
        if shared:
            return key, arms, tuple(sorted(shared))
    return None


def declared_artifacts() -> frozenset[str]:
    """Every artifact path the panel-resolution registries name."""

    from orion.programme import panel_resolution

    declared: set[str] = set()
    for registry in (
        panel_resolution.PUBLISHED_PANELS,
        panel_resolution.PUBLISHED_MARGIN_GATES,
        panel_resolution.PUBLISHED_ABLATIONS,
    ):
        declared.update(entry["artifact"] for entry in registry)
    return frozenset(declared)


def _paper_id(path: Path) -> str:
    for part in path.parts:
        if part.startswith("paper-"):
            pieces = part.split("-")
            if len(pieces) > 1 and pieces[1].isdigit():
                return f"P{int(pieces[1])}"
    return "UNKNOWN"


def _documents(root: Path) -> Iterator[tuple[Path, dict[str, Any]]]:
    for path in sorted(root.rglob("*.json")):
        if any(part in {"__pycache__", "figures", ".git"} for part in path.parts):
            continue
        try:
            document = json.loads(path.read_text())
        except (json.JSONDecodeError, UnicodeDecodeError, OSError):
            continue
        if isinstance(document, dict):
            yield path, document


def discover_candidates(root: Path, *, declared: Iterable[str] | None = None) -> tuple[PanelCandidate, ...]:
    """Find every artifact that decided something over a panel of arms."""

    known = frozenset(declared) if declared is not None else declared_artifacts()
    out: list[PanelCandidate] = []
    for path, document in _documents(root):
        if not any(key in document for key in TERMINAL_KEYS):
            continue
        block = panel_block(document)
        if block is None:
            continue
        key, arms, metrics = block
        terminal = document.get("terminal") or document.get("verdict")
        out.append(
            PanelCandidate(
                artifact=str(path),
                paper_id=_paper_id(path),
                systems_key=key,
                arms=len(arms),
                metrics=metrics,
                terminal=terminal if isinstance(terminal, str) else None,
                declared=str(path) in known,
            )
        )
    return tuple(out)


@dataclass(frozen=True)
class CoverageReport:
    candidates: tuple[PanelCandidate, ...]
    declared_count: int

    @property
    def unregistered(self) -> tuple[PanelCandidate, ...]:
        return tuple(c for c in self.candidates if not c.declared)

    @property
    def unregistered_positives(self) -> tuple[PanelCandidate, ...]:
        """Unexamined panels behind a claim of support."""

        return tuple(c for c in self.unregistered if c.claims_support)

    @property
    def outcome(self) -> Outcome:
        return Outcome.CANNOT_CHECK if self.unregistered else Outcome.PASS

    def as_json(self) -> dict[str, Any]:
        return {
            "schema_version": SCHEMA_VERSION,
            "discovery_rule": (
                f"a json artifact carrying one of {TERMINAL_KEYS} and a block under one of "
                f"{SYSTEMS_KEYS} mapping at least {MIN_ARMS} named arms to dicts sharing at "
                "least one numeric metric"
            ),
            "declared_by_registries": self.declared_count,
            "discovered": len(self.candidates),
            "unregistered": len(self.unregistered),
            "unregistered_claiming_support": [c.artifact for c in self.unregistered_positives],
            "outcome": self.outcome.value,
            "candidates": [
                {
                    "artifact": c.artifact,
                    "paper_id": c.paper_id,
                    "systems_key": c.systems_key,
                    "arms": c.arms,
                    "metrics": list(c.metrics),
                    "terminal": c.terminal,
                    "declared": c.declared,
                    "outcome": c.outcome.value,
                }
                for c in self.candidates
            ],
        }


def coverage_report(root: Path) -> CoverageReport:
    declared = declared_artifacts()
    return CoverageReport(
        candidates=discover_candidates(root, declared=declared),
        declared_count=len(declared),
    )
