"""P1-U R6-DR1 repaired root encoding: a world in which ``DIAGNOSE`` is reachable.

Frozen by ``FREEZE_2026-08-21_DIAGNOSE_REACHABLE_V1.md`` section 2 before any arm
was executed.

Why this file exists
--------------------
``SolverLoop`` reaches ``DIAGNOSE`` once per *material* residual, and
``DetectOperator`` emits one only for an unsearched candidate domain, an absent
``VERIFIED`` claim, or a contradiction. The R6 campaign's root encoding entered
``DETECT`` with the episode's one domain already searched and its one claim already
``VERIFIED``; no branch could fire, so ``DIAGNOSE`` never ran and the
``ORION_NATIVE_BASE`` ablation returned ``UNRESOLVED`` on 48/48 episodes without
ever executing the mechanism it was added to ablate.

The repair restores what ``development/p1-u-gpt-r6-native-runtime/DEVELOPMENT_PACKET.md``
specified: the root host begins *without a verified claim*, so ``DETECT`` exposes a
material evidence residual. Crucially it does so **with evidence present** --- the
dossier is planned for, retrieved, absorbed and reconstructed --- because the thing
that broke the campaign was reachability collapsing as soon as the world stopped
being empty.

Nothing in the scientific decision function is touched. The provider host, keyword
table, native-to-P1 mapping, probe priority, budget, responsibility/interface/gate
logic and every threshold are used byte-identically from the frozen
``gpt_r6/native_orion.py`` / ``native_orion_core_v1.py``. Only the root world
changes, and it changes reachability alone.
"""

from __future__ import annotations

import importlib.util
import json
import sys
from contextlib import contextmanager
from pathlib import Path
from typing import Any, Iterator, Mapping

from orion.core.problem import Problem
from orion.core.search import RetrievedItem
from orion.providers.retrieval import InMemoryRetrievalProvider
from orion.providers.verification import InMemoryVerificationProvider

HERE = Path(__file__).resolve().parent
R6 = HERE.parent / "gpt_r6"
REPO = HERE.parents[3]
HARNESS_SRC = REPO / "packages" / "orion-research-harness" / "src"

# The research harness is a sibling package with its own pyproject; the repository
# test path exposes only `src`. Adding it here rather than requiring an install
# keeps the precondition gate available wherever this module is imported from ---
# and the gate is the whole point of the module, so it must not be optional.
if str(HARNESS_SRC) not in sys.path:  # pragma: no cover - import bootstrap
    sys.path.insert(0, str(HARNESS_SRC))

from orion_research_harness.operator_coverage import (  # noqa: E402
    require_operators_exercised,
    run_operator_coverage,
)

#: Operators every scored native root run must have executed before it is scored.
REQUIRED_ROOT_OPERATORS = frozenset({"DIAGNOSE"})

ROOT_DOMAIN_ROUTE_KIND = "CURRENT_VOCABULARY"


def load_frozen_native() -> Any:
    """Import the frozen R6 native adapter without mutating it."""

    name = "p1_u_r6_dr1_native_adapter"
    spec = importlib.util.spec_from_file_location(name, R6 / "native_orion.py")
    if spec is None or spec.loader is None:
        raise RuntimeError("cannot load frozen P1-R6 native adapter")
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    try:
        spec.loader.exec_module(module)
    except Exception:
        sys.modules.pop(name, None)
        raise
    return module


class RepairedRootHost:
    """The frozen root provider host, plus one planned domain-hinted query.

    Subclassing keeps ``interpret``/``reconstruct``/``diagnose``/``compose_answer``
    exactly as frozen; only ``plan_search`` differs, and only so that the dossier
    actually enters the world through the canonical SEARCH/ABSORB path.
    """

    def __init__(self, core: Any, *, episode_id: str, domain: str) -> None:
        self._inner = core.FrozenNativeProviderHost(mode="root")
        self._episode_id = str(episode_id)
        self._domain = str(domain)

    @property
    def last_native_responsibilities(self) -> tuple[str, ...]:
        return self._inner.last_native_responsibilities

    @property
    def calls(self) -> list[tuple[str, str]]:
        return self._inner.calls

    def query_text(self) -> str:
        return f"p1-r6-dr1-root:{self._episode_id}"

    def __call__(self, request: Any) -> str:
        if str(request.task) == "plan_search":
            self._inner.calls.append((str(request.task), str(request.user)))
            return json.dumps(
                {
                    "queries": [
                        {
                            "query_id": f"p1-r6-dr1-root-query:{self._episode_id}",
                            "text": self.query_text(),
                            "route_id": "p1-r6-dr1-root-route",
                            "route_kind": ROOT_DOMAIN_ROUTE_KIND,
                            "domain_hint": self._domain,
                        }
                    ]
                }
            )
        return self._inner(request)


class RootCoverageLedger:
    """Per-episode operator-coverage reports for the runs this campaign scored."""

    def __init__(self) -> None:
        self.reports: list[dict[str, Any]] = []

    def record(self, *, arm: str, episode_id: str, report: Mapping[str, Any]) -> None:
        self.reports.append(
            {"arm": str(arm), "episode_id": str(episode_id), "coverage": dict(report)}
        )

    def diagnose_reached(self, arm: str | None = None) -> int:
        return sum(
            1
            for row in self.reports
            if (arm is None or row["arm"] == arm)
            and "DIAGNOSE" in row["coverage"]["executed"]
        )

    def count(self, arm: str | None = None) -> int:
        return sum(1 for row in self.reports if arm is None or row["arm"] == arm)


def build_repaired_root(core: Any, *, arm: str, ledger: RootCoverageLedger | None = None):
    """Return a ``run_root_runtime`` replacement that executes the repaired world."""

    def run_root_runtime(*, episode_id: str, dossier: str, domain: str):
        host = RepairedRootHost(core, episode_id=episode_id, domain=domain)
        cfg = core.PROTOCOL["root_runtime"]
        item_id = f"evidence:p1-r6-dr1:{episode_id}"
        item = RetrievedItem(
            item_id=item_id,
            content=str(dossier),
            source_uri=f"p1-r6-dr1://{episode_id}/dossier",
            domain_ids=(str(domain),),
        )
        runtime = core._runtime(
            provider_host=host,
            retrieval=InMemoryRetrievalProvider({host.query_text(): (item,)}),
            # Certifies nothing: the absorbed dossier claim carries
            # SOURCE_PROJECTION authority, so DETECT sees no VERIFIED claim and
            # emits a material MISSING_EVIDENCE residual. This is the repair.
            verification=InMemoryVerificationProvider(frozenset()),
            max_iterations=int(cfg["max_iterations"]),
        )
        result = runtime.solve(
            Problem(
                problem_id=f"p1-r6-dr1-root:{episode_id}",
                question=(
                    "What is the narrowest scientifically responsible next action "
                    "for this unresolved episode?"
                ),
                scope=str(dossier),
                initial_domain_ids=(str(domain),),
                success_criteria=(
                    "Preserve ambiguity when responsibility is not identified.",
                    "Do not create scientific authority from diagnosis alone.",
                ),
            ),
            evaluation_epoch_id=str(cfg["evaluation_epoch_id"]),
            split_id=str(cfg["split_id"]),
        )

        # The precondition gate, on episode one. It raises naming what never ran.
        sequence = [item.value for item in result.trace.operator_sequence]
        coverage = require_operators_exercised(
            sequence, REQUIRED_ROOT_OPERATORS, label=f"{arm}:{episode_id}"
        )
        if ledger is not None:
            ledger.record(arm=arm, episode_id=episode_id, report=coverage)

        core._require_operator_ids(result, tuple(cfg["required_operator_ids"]))
        if not host.last_native_responsibilities:
            raise AssertionError("repaired root runtime produced no native diagnosis")
        return core.NativeRootExecution(
            result=result,
            provider_responsibilities=host.last_native_responsibilities,
            operator_ids=core._trace_operator_ids(result),
            receipt_ids=core._trace_receipt_ids(result),
        )

    return run_root_runtime


@contextmanager
def repaired_root(core: Any, *, arm: str, ledger: RootCoverageLedger | None = None) -> Iterator[None]:
    """Install the repaired root on the frozen core for the duration of one call.

    Scoped rather than global so that importing this module cannot change the
    behaviour of the frozen R6 modules for anything else in the process.
    """

    original = core.run_root_runtime
    core.run_root_runtime = build_repaired_root(core, arm=arm, ledger=ledger)
    try:
        yield
    finally:
        core.run_root_runtime = original


def run_base_dr1(
    core: Any,
    episode: Mapping[str, Any],
    *,
    ledger: RootCoverageLedger | None = None,
) -> dict[str, Any]:
    """``ORION_NATIVE_BASE_DR1``: the frozen BASE decision on the repaired root."""

    with repaired_root(core, arm="ORION_NATIVE_BASE_DR1", ledger=ledger):
        return core.run_native_base(episode)


def run_ard_dr1(
    core: Any,
    episode: Mapping[str, Any],
    *,
    evidence_note: str,
    ledger: RootCoverageLedger | None = None,
) -> dict[str, Any]:
    """``ORION_NATIVE_ARD_DR1``: the frozen ARD decision on the repaired root."""

    with repaired_root(core, arm="ORION_NATIVE_ARD_DR1", ledger=ledger):
        return core.run_native_ard(episode, evidence_note=evidence_note)


def root_operator_coverage(root_execution: Any) -> dict[str, Any]:
    """Coverage report for an already-executed root run."""

    return run_operator_coverage(
        [item.value for item in root_execution.result.trace.operator_sequence]
    )


__all__ = [
    "REQUIRED_ROOT_OPERATORS",
    "RepairedRootHost",
    "RootCoverageLedger",
    "build_repaired_root",
    "load_frozen_native",
    "repaired_root",
    "root_operator_coverage",
    "run_ard_dr1",
    "run_base_dr1",
]
