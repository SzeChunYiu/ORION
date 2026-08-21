"""Shared apparatus for the papers' machine-checked cores.

P6, P7 and P8 each carry a formal core whose current authority is exhaustive
enumeration over an authored finite state space, and each has a terminal asking
for a theorem instead. The three lifts differ in what they say and agree on how
a proof is reported, so the reporting lives here rather than three times over.

Two decisions are load-bearing and are the reason this is a module rather than a
convention.

**Proof outcomes are three-valued.** A solver returning ``unknown`` has not
agreed with the claim; it has given up. Collapsing that into a boolean makes "the
theorem holds" and "the solver timed out" print the same character, which is the
``VACUOUS_GUARD_ZERO_DENOMINATOR`` shape with a proof obligation in place of a
test. Two theorems in P8's lift genuinely came back ``UNKNOWN`` before its axioms
were right, and that is how the missing axiom was found.

**A proof about the wrong sentence proves nothing.** Every lift here is a
transcription of an executable model into logic, and a transcription can be
wrong. :class:`DifferentialReport` exists so that agreement between the two is
measured rather than assumed --- including whether the corpus it was measured on
exercised more than one verdict, because agreement on a corpus where both sides
always refuse is agreement about the constant ``False``.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Any

try:  # pragma: no cover - exercised by the import guard test
    import z3
except ImportError as _error:  # pragma: no cover
    z3 = None  # type: ignore[assignment]
    _IMPORT_ERROR: ImportError | None = _error
else:
    _IMPORT_ERROR = None


class ProofOutcome(str, Enum):
    """Three-valued, because a solver that gave up is not a solver that agreed."""

    PROVED = "PROVED"
    COUNTEREXAMPLE = "COUNTEREXAMPLE"
    UNKNOWN = "UNKNOWN"


class Z3Unavailable(RuntimeError):
    """Raised when a proof is requested without the solver installed.

    Raised rather than returned, for the reason the rest of this programme raises
    on an absent measurement: a ``False`` from a checker that could not run is
    indistinguishable from a checker that ran and disagreed.
    """


def require_z3() -> Any:
    if z3 is None:  # pragma: no cover - exercised by the import guard test
        raise Z3Unavailable(
            "this proof needs the z3-solver package; without it no theorem here has "
            f"been checked, which is not the same as passing ({_IMPORT_ERROR})"
        )
    return z3


@dataclass(frozen=True)
class Theorem:
    """One claim, with the reason it is worth stating kept beside it."""

    name: str
    statement: str
    why_it_matters: str

    def __post_init__(self) -> None:
        for field in ("name", "statement", "why_it_matters"):
            if not str(getattr(self, field)).strip():
                raise ValueError(f"a theorem requires a non-blank {field}")


@dataclass(frozen=True)
class ProofResult:
    theorem: Theorem
    outcome: ProofOutcome
    detail: str

    @property
    def discharged(self) -> bool:
        return self.outcome is ProofOutcome.PROVED

    def as_json(self) -> dict[str, object]:
        return {
            "name": self.theorem.name,
            "statement": self.theorem.statement,
            "why_it_matters": self.theorem.why_it_matters,
            "outcome": self.outcome.value,
            "detail": self.detail,
        }


def discharge(theorem: Theorem, axioms: list[Any], claim: Any, *, timeout_ms: int = 20000) -> ProofResult:
    """Prove ``claim`` by refuting its negation under ``axioms``.

    ``unsat`` on the negation is the proof. ``sat`` is a countermodel and is
    reported as one --- a countermodel to a claim a paper makes is a finding, not
    an error to retry with different settings. ``unknown`` is reported as
    ``unknown``.
    """

    solver_module = require_z3()
    solver = solver_module.Solver()
    solver.set("timeout", timeout_ms)
    for axiom in axioms:
        solver.add(axiom)
    solver.add(solver_module.Not(claim))
    verdict = solver.check()
    if verdict == solver_module.unsat:
        return ProofResult(theorem, ProofOutcome.PROVED, "negation is unsatisfiable under the axioms")
    if verdict == solver_module.sat:
        return ProofResult(
            theorem,
            ProofOutcome.COUNTEREXAMPLE,
            f"the negation is satisfiable; countermodel: {solver.model()}",
        )
    return ProofResult(
        theorem,
        ProofOutcome.UNKNOWN,
        f"solver returned unknown ({solver.reason_unknown()}); the theorem is NOT discharged",
    )


@dataclass(frozen=True)
class DifferentialReport:
    """Agreement between an executable model and the formula proved about it."""

    trials: int
    agreements: int
    disagreements: tuple[str, ...]
    positive_trials: int

    def __post_init__(self) -> None:
        if self.trials < 0 or self.agreements < 0 or self.positive_trials < 0:
            raise ValueError("differential counts cannot be negative")
        if self.positive_trials > self.trials:
            raise ValueError("more positive trials than trials")

    @property
    def agreed(self) -> bool:
        return not self.disagreements and self.trials > 0

    @property
    def exercised_both_verdicts(self) -> bool:
        """A corpus that only ever refuses agrees for the wrong reason.

        If every trial comes out the same way, "the formula and the code agree"
        is a claim about a constant. The differential is informative only when
        both verdicts occur, and this is reported alongside the agreement count
        so a one-sided corpus cannot be read as a clean result.
        """

        return 0 < self.positive_trials < self.trials

    @property
    def informative(self) -> bool:
        return self.agreed and self.exercised_both_verdicts

    def as_json(self) -> dict[str, object]:
        return {
            "trials": self.trials,
            "agreements": self.agreements,
            "positive_trials": self.positive_trials,
            "disagreements": list(self.disagreements),
            "agreed": self.agreed,
            "exercised_both_verdicts": self.exercised_both_verdicts,
            "informative": self.informative,
        }


def load_executable_model(path: Any, module_name: str) -> Any:
    """Load a committed checker that is not on an importable package path."""

    import importlib.util
    import sys
    from pathlib import Path

    target = Path(path)
    if not target.is_file():
        raise FileNotFoundError(f"the executable model is not at {target}")
    spec = importlib.util.spec_from_file_location(module_name, target)
    if spec is None or spec.loader is None:  # pragma: no cover - defensive
        raise ImportError(f"could not load {target}")
    module = importlib.util.module_from_spec(spec)
    # Registered before execution: `@dataclass` resolves annotations through
    # `sys.modules[cls.__module__]`, which is None while a module is still
    # executing and not yet registered.
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


__all__ = [
    "DifferentialReport",
    "ProofOutcome",
    "ProofResult",
    "Theorem",
    "Z3Unavailable",
    "discharge",
    "load_executable_model",
    "require_z3",
]
