"""P8's authority receipts, and the words in them the run cannot withhold.

Three shipped artifacts are registered here, all loaded from the repository
rather than re-implemented, so the instrument is pointed at what P8 actually
publishes.

``research/extensions/p8-method-authority/run_anti_laundering_bench.py`` is the
primary. It scores fifteen frozen coercion and revocation cases against
:mod:`orion.transfer.v2.p8_method_authority` and emits four rates, a
``terminal`` and a declared ceiling. Until 2026-08-21 the rates were computed
and the terminal was the string literal ``P8_P9_P10_ANTI_LAUNDERING_CLEAR``
written into the dict beside them, with ``claim_ceiling`` being
``panel['claim_ceiling']`` echoed back. The bench now derives its terminal from
the four rates as ``worst_outcome`` over four
:class:`~orion.programme.guard_exercise.GuardExercise` assessments, and names
the echoed bound ``declared_claim_ceiling_from_input``.
:func:`withholding_cases` is the register of inputs under which that terminal
must not be ``CLEAR``: a panel with every expectation inverted, and --- the one
that matters --- the untouched panel scored against an authority table that
launders every capability output into every authority coordinate. It is what
turns "the terminal is derived" from a claim about the source text into a
measurement, and the shipped verdict is unchanged because the shipped rates
really are 1.0.

The panel itself is the second artifact. Its fifteen ``expected`` labels are the
shipped ``LEGAL`` and ``DEFEATER_COORDS`` tables read off, so
:func:`panel_gold_divergence` asks the question
:func:`~orion.programme.refutation_capacity.divergence_of` was written for: on
how many of the fifteen cases could the declared gold disagree with the
mechanism it grades? A gold that agrees everywhere grades a transcription.

``research/claim_expansion/p8/check_p8_x4_authority_lifting.py`` is the third,
and it is the one the superiority ledger names for P8-U-T1. Its rule
``scientific_terminal`` takes seven arguments and the donor family is not among
them, while the script loops over thirteen donors and then over thirteen-by-
thirteen donor pairs. :func:`x4_donor_axis` measures what that loop is worth.

The failure class is recorded under
``research/failures/2026-08-unconditional-terminal-self-issued-authority/``.
"""

from __future__ import annotations

import importlib.util
import itertools
import json
import sys
from dataclasses import dataclass, field
from functools import lru_cache
from pathlib import Path
from types import ModuleType
from typing import Any, Hashable, Mapping

from orion.programme.refutation_capacity import (
    AxisSensitivity,
    ModelPoint,
    TheoryDivergence,
    axis_sensitivity,
    divergence_of,
)
from orion.programme.terminal_responsiveness import (
    DeclaredBound,
    ReceiptResponsiveness,
    WithholdingCase,
    measure_declared_bound,
    measure_receipt_responsiveness,
    overridden,
)
from orion.transfer.v2 import p8_method_authority as authority

REPO_ROOT = Path(__file__).resolve().parents[4]
BENCH_SCRIPT = REPO_ROOT / "research/extensions/p8-method-authority/run_anti_laundering_bench.py"
BENCH_PANEL = (
    REPO_ROOT / "research/extensions/p8-method-authority/P9_P10_ANTI_LAUNDERING_CASES_V1.json"
)
BENCH_SUMMARY = (
    REPO_ROOT / "research/extensions/p8-method-authority/P9_P10_ANTI_LAUNDERING_SUMMARY_V1.json"
)
X4_CHECKER = REPO_ROOT / "research/claim_expansion/p8/check_p8_x4_authority_lifting.py"

#: The terminal the shipped summary publishes. It was once the only one the
#: emitter could publish; it is now the ``PASS`` branch of a derived three-valued
#: verdict, and :func:`withholding_cases` names inputs that reach the other two.
SHIPPED_TERMINAL = "P8_P9_P10_ANTI_LAUNDERING_CLEAR"

#: The shipped summary's own ``result_digest``. The fidelity anchor: the emitter
#: registered here reproduces the committed receipt byte for byte, so a failure
#: reported below is about P8 and not about a fixture written to fail. Rotated
#: from ``sha256:45f359f5...`` on 2026-08-21 when the terminal became derived and
#: ``claim_ceiling`` was renamed to ``declared_claim_ceiling_from_input``.
SHIPPED_RESULT_DIGEST = "sha256:f7544712668544528b4d6dfd69d070273fde9405d901b3f908df35a083ca0617"

#: The four rates the bench computes. Traced as evidence rather than as verdicts:
#: they are what separates "the emitter was never perturbed" from "the emitter
#: was perturbed, its numbers moved and its terminal did not".
BENCH_RATES: tuple[str, ...] = (
    "contract_accuracy",
    "illicit_coercion_block_rate",
    "clean_legal_coverage",
    "revocation_accuracy",
)

#: A ceiling no bounded synthetic contract suite could earn, for
#: :func:`bench_declared_ceiling` to inject. Repeating it is unambiguous.
OVERREACHING_CEILING = "This suite establishes real method validity, novelty, utility and adoption."

#: The field the bench emits its input-supplied ceiling under. Renamed from
#: ``claim_ceiling`` on 2026-08-21: the value is still whatever the panel says,
#: so the receipt states in the field name where the bound came from rather than
#: publishing it where a reader would take it for one the run established.
DECLARED_CEILING_FIELD = "claim_ceiling"


def _load(path: Path, module_name: str) -> ModuleType:
    """Import a shipped script by path without putting it on the import graph."""

    spec = importlib.util.spec_from_file_location(module_name, path)
    if spec is None or spec.loader is None:
        raise ImportError(f"cannot load {path}")
    module = importlib.util.module_from_spec(spec)
    # Registered before execution so dataclasses and enums defined inside resolve
    # their own module, which `spec_from_file_location` alone does not arrange.
    sys.modules.setdefault(module_name, module)
    spec.loader.exec_module(module)
    return module


@lru_cache(maxsize=None)
def bench_module() -> ModuleType:
    return _load(BENCH_SCRIPT, "orion_p8_anti_laundering_bench")


@lru_cache(maxsize=None)
def x4_module() -> ModuleType:
    return _load(X4_CHECKER, "orion_p8_x4_authority_lifting")


def shipped_panel() -> dict[str, Any]:
    return json.loads(BENCH_PANEL.read_text())


def shipped_summary() -> dict[str, Any]:
    return json.loads(BENCH_SUMMARY.read_text())


@dataclass(frozen=True)
class BenchInput:
    """One input to the anti-laundering bench: a panel, and the rules grading it.

    The panel is what a reviewer is shown. ``legal`` and ``defeater_coords`` are
    the shipped authority tables, overridable because the question the receipt
    invites is what its terminal would say if the mechanism were wrong --- and a
    wrong mechanism cannot be expressed as a different panel.
    """

    panel: Mapping[str, Any]
    legal: Mapping[Any, Any] | None = None
    defeater_coords: Mapping[Any, Any] | None = None
    note: str = field(default="", compare=False)


def bench_emitter(payload: BenchInput) -> Mapping[str, object]:
    """Run the shipped bench's own ``run()`` under the payload's authority tables."""

    overrides: dict[str, Any] = {}
    if payload.legal is not None:
        overrides["LEGAL"] = dict(payload.legal)
    if payload.defeater_coords is not None:
        overrides["DEFEATER_COORDS"] = dict(payload.defeater_coords)
    if not overrides:
        return bench_module().run(dict(payload.panel))
    with overridden(authority, **overrides):
        return bench_module().run(dict(payload.panel))


def _inverted_panel() -> dict[str, Any]:
    """The frozen panel with every expectation replaced by one the run contradicts.

    Derived from the shipped ``AuthorityState`` rather than from a transcribed
    table of its members, so a fourth state would be perturbed too.
    """

    states = tuple(item.value for item in authority.AuthorityState)
    panel = shipped_panel()
    for case in panel["cases"]:
        case["expected"] = next(value for value in states if value != case["expected"])
    return panel


def _total_laundering() -> dict[Any, Any]:
    """An authority table under which every capability may set every coordinate."""

    return {
        kind: frozenset(authority.AuthorityCoordinate) for kind in authority.CapabilityKind
    }


def _no_revocation() -> dict[Any, Any]:
    """A defeater table under which no defeater touches any coordinate."""

    return {defeater: () for defeater in authority.DefeaterKind}


def withholding_cases() -> tuple[WithholdingCase, ...]:
    """Inputs under which ``P8_P9_P10_ANTI_LAUNDERING_CLEAR`` must be withheld."""

    return (
        WithholdingCase(
            case_id="every-expectation-inverted",
            withholds=(
                "each of the fifteen frozen cases now declares the outcome the suite says is "
                "wrong; a suite that agrees with none of its own panel is not clear"
            ),
            payload=BenchInput(panel=_inverted_panel()),
        ),
        WithholdingCase(
            case_id="authority-table-launders-everything",
            withholds=(
                "the panel is untouched and the graded mechanism permits every "
                "capability-to-authority coercion, so all seven named laundering attacks "
                "succeed; that is the exact failure the suite is named after"
            ),
            payload=BenchInput(panel=shipped_panel(), legal=_total_laundering()),
        ),
        WithholdingCase(
            case_id="defeaters-propagate-nowhere",
            withholds=(
                "the panel is untouched and no defeater revokes any coordinate, so prior art "
                "and a fresh counterexample leave a method's authority standing"
            ),
            payload=BenchInput(panel=shipped_panel(), defeater_coords=_no_revocation()),
        ),
    )


def bench_responsiveness() -> ReceiptResponsiveness:
    """Measure whether the bench's terminal is a function of anything it reports."""

    return measure_receipt_responsiveness(
        bench_emitter,
        label="P8.P9P10AntiLaundering.v1/terminal",
        baseline=BenchInput(panel=shipped_panel()),
        verdict_field="terminal",
        evidence_fields=BENCH_RATES,
        cases=withholding_cases(),
    )


def bench_declared_ceiling() -> DeclaredBound:
    """Measure whether the bench's declared ceiling is one its input supplied.

    The previous version of this docstring said "only deriving the bound would
    change this verdict", and that is what happened. The bench now keys its
    ceiling off the terminal --- which is itself derived from the graded
    assessments --- and records the input's own ``claim_ceiling`` as a digest
    rather than reproducing its text. An injected overreaching ceiling therefore
    cannot come back, because nothing echoes it.

    The measurement is unchanged: the same overreaching sentence is still
    injected and the same field is still read. Only the bench moved.
    """

    panel = shipped_panel()
    panel["claim_ceiling"] = OVERREACHING_CEILING
    return measure_declared_bound(
        bench_emitter,
        label=f"P8.P9P10AntiLaundering.v1/{DECLARED_CEILING_FIELD}",
        field=DECLARED_CEILING_FIELD,
        overreaching_payload=BenchInput(panel=panel),
        overreaching_bound=OVERREACHING_CEILING,
    )


#: Defeaters whose propagation reopens a coordinate rather than closing it. Read
#: off ``p8_method_authority.revoke``, which inlines this set as a literal.
REOPENING_DEFEATERS = frozenset(
    {
        authority.DefeaterKind.SUBJECT_IDENTITY_CHANGED,
        authority.DefeaterKind.EVALUATOR_CHANGED,
        authority.DefeaterKind.REPRESENTATION_CHANGED,
    }
)


def mechanism_verdict(point: ModelPoint) -> Hashable:
    """The label the shipped authority tables give one panel case.

    Two table lookups and nothing else --- no digest, no evidence, no scientific
    content --- because that is all the graded mechanism consults.
    """

    state = authority.AuthorityState
    coordinate = authority.AuthorityCoordinate(point["coordinate"])
    if point["kind"] == "coercion":
        source = authority.CapabilityKind(point["source"])
        legal = coordinate in authority.LEGAL[source]
        return state.SUPPORTED.value if legal else state.BLOCKED.value
    defeater = authority.DefeaterKind(point["defeater"])
    if coordinate not in authority.DEFEATER_COORDS[defeater]:
        return state.SUPPORTED.value
    return (state.CANNOT_CHECK if defeater in REOPENING_DEFEATERS else state.BLOCKED).value


def declared_gold(point: ModelPoint) -> Hashable:
    """The label the frozen panel declares for one case."""

    return point["expected"]


def panel_space() -> tuple[ModelPoint, ...]:
    """The fifteen frozen cases, as points a rule can be evaluated on."""

    return tuple(
        {
            "case_id": case["id"],
            "kind": case["kind"],
            "source": case.get("source", ""),
            "defeater": case.get("defeater", ""),
            "coordinate": case["coordinate"],
            "expected": case["expected"],
        }
        for case in shipped_panel()["cases"]
    )


def panel_gold_divergence() -> TheoryDivergence:
    """Count the frozen cases where the declared gold could disagree with the tables."""

    return divergence_of(
        declared_gold,
        theory_id="P8.P9P10AntiLaundering.v1/declared-gold",
        reference=mechanism_verdict,
        space=panel_space(),
    )


def x4_reference(point: ModelPoint) -> Hashable:
    """The shipped X4 rule, evaluated on one point of its own enumerated space."""

    return x4_module().scientific_terminal(
        point["native_valid"],
        point["scientific_type"],
        point["narrowing_ok"],
        point["blocker"],
        point["support_a"],
        point["support_b"],
        point["protected_coercion"],
    )


@lru_cache(maxsize=None)
def x4_space() -> tuple[ModelPoint, ...]:
    """The 39,936 points the shipped X4 checker enumerates, in its own loop order."""

    module = x4_module()
    points: list[ModelPoint] = []
    for donor in module.DONORS:
        for native in (False, True):
            for flags in itertools.product((False, True), repeat=5):
                for narrowing in (False, True):
                    for blocker in module.BLOCKERS:
                        for support_a in (False, True):
                            for support_b in (False, True):
                                for coercion in (False, True):
                                    points.append(
                                        {
                                            "donor": donor,
                                            "native_valid": native,
                                            "scientific_type": flags,
                                            "narrowing_ok": narrowing,
                                            "blocker": blocker,
                                            "support_a": support_a,
                                            "support_b": support_b,
                                            "protected_coercion": coercion,
                                        }
                                    )
    return tuple(points)


def x4_donor_axis() -> AxisSensitivity:
    """Measure whether the thirteen donor families change any X4 verdict."""

    return axis_sensitivity("donor", reference=x4_reference, space=x4_space())


__all__ = [
    "BENCH_PANEL",
    "BENCH_RATES",
    "BENCH_SCRIPT",
    "BENCH_SUMMARY",
    "DECLARED_CEILING_FIELD",
    "OVERREACHING_CEILING",
    "REOPENING_DEFEATERS",
    "SHIPPED_RESULT_DIGEST",
    "SHIPPED_TERMINAL",
    "X4_CHECKER",
    "BenchInput",
    "bench_declared_ceiling",
    "bench_emitter",
    "bench_module",
    "bench_responsiveness",
    "declared_gold",
    "mechanism_verdict",
    "panel_gold_divergence",
    "panel_space",
    "shipped_panel",
    "shipped_summary",
    "withholding_cases",
    "x4_donor_axis",
    "x4_module",
    "x4_reference",
    "x4_space",
]
