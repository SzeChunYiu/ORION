"""A failure class recorded against one paper is not a failure class that was swept.

The programme records what it got wrong. ``research/failures/`` holds 51 classes,
each a README that names the defect, proves it from the artifact, and says what
was done about it. That discipline is why the same mistake is rarely made twice
*in the same paper*.

It says nothing about the other fourteen.

``2026-08-unfalsifiable-check-zero-refutation-capacity`` is the worked example
and it is not hypothetical. The class was recorded on 2026-08 against **P6**,
whose certificate-lifting checker counted ``x != x`` 1,536 times and published
the zero as a theorem. The README is thorough: it quotes the two definitions
written twice, it counts the enumerated space, and it names the repair.

The same guard was in **P7**::

    projected_native = native_valid
    if projected_native != native_valid:
        donor_conservativity_violations += 1

and in **P8**, three times over. Both published
``donor_conservativity_violations: 0`` and both exited 0. They were found on
2026-08-22 by reading P7 and P8 for that shape, months of programme-time after
the class was named --- not by any mechanism, because no mechanism was pointed at
them. Nothing had gone wrong with the failure record. Nobody had swept it.

Measured across the whole directory, that is the normal case rather than the
exception:

- **40 of 51** classes name at most one paper.
- **36 of 51** name no detector module at all, so there is nothing to re-run
  against a second paper even if someone decided to.
- **P13 and P15 are named by no class whatsoever.** That is not a clean bill;
  it is an unswept one, and the difference is the whole point of this module.

The gap is not knowledge and it is not care. It is that a prose README has no
denominator. "We found this in P6" and "this does not occur in P1-P5, P7-P15"
are different claims, and only the first one is ever written down, so the second
gets read into it for free.

So this module gives the record a denominator. Every (class, paper) pair is one
of three things, and the third is the one that does the work:

``FOUND``
    The class was observed in this paper. Evidence names where.
``SWEPT_CLEAN``
    A detector ran against this paper and did not find it. Evidence names the
    detector and the run.
``NOT_SWEPT``
    Nobody looked. This is
    :data:`~orion.programme.records.Outcome.CANNOT_CHECK` and it blocks exactly
    as a failure does, because a pair nobody examined is not evidence of absence
    --- which is precisely what P7 and P8 were for as long as the record showed
    only P6.

A class with no declared detector cannot produce ``SWEPT_CLEAN`` for anybody.
That is deliberate and it is the fail-closed edge: sweeping by hand and writing
"checked" in a README is the practice this module exists to replace, so an
unmechanised class reads as 15 open cells until someone mechanises it.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import Iterable

from orion.programme.records import Outcome

__all__ = [
    "CoverageMatrix",
    "CoverageReport",
    "FailureClass",
    "PairState",
    "PaperCoverage",
    "SweepEvidence",
    "coverage_matrix",
    "load_failure_classes",
    "pair_state",
]

#: The papers the programme claims. A class is swept when every one is decided.
PAPER_IDS: tuple[int, ...] = tuple(range(1, 16))

#: Filename a failure-class directory uses to declare what it is and where it ran.
DECLARATION = "CLASS.json"

SCHEMA_VERSION = "orion.programme.failure-class-coverage.v1"


class PairState(str, Enum):
    """What is known about one failure class in one paper."""

    #: Observed here. The class exists in this paper.
    FOUND = "FOUND"
    #: A named detector ran here and did not find it.
    SWEPT_CLEAN = "SWEPT_CLEAN"
    #: Nobody looked. Not evidence of absence.
    NOT_SWEPT = "NOT_SWEPT"

    @property
    def outcome(self) -> Outcome:
        if self is PairState.SWEPT_CLEAN:
            return Outcome.PASS
        if self is PairState.FOUND:
            return Outcome.FAIL
        return Outcome.CANNOT_CHECK

    @property
    def blocks(self) -> bool:
        return self.outcome.blocks


@dataclass(frozen=True)
class SweepEvidence:
    """What was run against one paper, and what came back.

    ``detector`` is an importable dotted path, not a description. A sweep whose
    detector cannot be named is a sweep that cannot be repeated, and this record
    exists to be repeated.
    """

    paper_id: int
    detector: str
    run: str
    found: bool

    def __post_init__(self) -> None:
        if self.paper_id not in PAPER_IDS:
            raise ValueError(f"paper {self.paper_id} is not one of the programme's papers")
        if not self.detector:
            raise ValueError(f"P{self.paper_id}: a sweep must name the detector that ran")
        if not self.run:
            raise ValueError(f"P{self.paper_id}: a sweep must name where it ran")


@dataclass(frozen=True)
class FailureClass:
    """One recorded class, and the papers it has actually been decided for."""

    class_id: str
    detector: str | None
    found_in: frozenset[int]
    sweeps: tuple[SweepEvidence, ...] = ()

    def __post_init__(self) -> None:
        stray = sorted(p for p in self.found_in if p not in PAPER_IDS)
        if stray:
            raise ValueError(f"{self.class_id}: found_in names papers that do not exist: {stray}")
        for sweep in self.sweeps:
            if self.detector and sweep.detector != self.detector:
                raise ValueError(
                    f"{self.class_id}: sweep of P{sweep.paper_id} used {sweep.detector!r} "
                    f"but the class declares {self.detector!r}; two detectors that were "
                    "never shown to agree are two different questions"
                )

    @property
    def mechanised(self) -> bool:
        return self.detector is not None

    @property
    def swept_clean(self) -> frozenset[int]:
        """Papers a detector cleared. Never includes a paper the class was found in."""

        if not self.mechanised:
            return frozenset()
        return frozenset(
            s.paper_id for s in self.sweeps if not s.found and s.paper_id not in self.found_in
        )

    @property
    def not_swept(self) -> frozenset[int]:
        return frozenset(PAPER_IDS) - self.found_in - self.swept_clean

    @property
    def outcome(self) -> Outcome:
        """``PASS`` only when every paper is decided one way or the other."""

        return Outcome.CANNOT_CHECK if self.not_swept else Outcome.PASS


def pair_state(cls: FailureClass, paper_id: int) -> PairState:
    if paper_id in cls.found_in:
        return PairState.FOUND
    if paper_id in cls.swept_clean:
        return PairState.SWEPT_CLEAN
    return PairState.NOT_SWEPT


@dataclass(frozen=True)
class PaperCoverage:
    """One paper's column: how much of the recorded record has been pointed at it."""

    paper_id: int
    found: int
    swept_clean: int
    not_swept: int

    @property
    def decided(self) -> int:
        return self.found + self.swept_clean

    @property
    def decided_fraction(self) -> float:
        total = self.decided + self.not_swept
        return self.decided / total if total else 0.0


@dataclass(frozen=True)
class CoverageMatrix:
    """Every recorded class against every paper."""

    classes: tuple[FailureClass, ...]

    @property
    def pairs(self) -> int:
        return len(self.classes) * len(PAPER_IDS)

    def state(self, class_id: str, paper_id: int) -> PairState:
        for cls in self.classes:
            if cls.class_id == class_id:
                return pair_state(cls, paper_id)
        raise KeyError(class_id)

    def by_paper(self) -> tuple[PaperCoverage, ...]:
        out = []
        for paper in PAPER_IDS:
            states = [pair_state(c, paper) for c in self.classes]
            out.append(
                PaperCoverage(
                    paper_id=paper,
                    found=sum(1 for s in states if s is PairState.FOUND),
                    swept_clean=sum(1 for s in states if s is PairState.SWEPT_CLEAN),
                    not_swept=sum(1 for s in states if s is PairState.NOT_SWEPT),
                )
            )
        return tuple(out)

    @property
    def unmechanised(self) -> tuple[FailureClass, ...]:
        return tuple(c for c in self.classes if not c.mechanised)

    @property
    def single_paper_classes(self) -> tuple[FailureClass, ...]:
        """Classes decided for at most one paper -- recorded once, never swept."""

        return tuple(c for c in self.classes if len(c.found_in | c.swept_clean) <= 1)


@dataclass(frozen=True)
class CoverageReport:
    matrix: CoverageMatrix

    @property
    def not_swept_pairs(self) -> int:
        return sum(p.not_swept for p in self.matrix.by_paper())

    @property
    def outcome(self) -> Outcome:
        return Outcome.CANNOT_CHECK if self.not_swept_pairs else Outcome.PASS

    def as_json(self) -> dict[str, object]:
        return {
            "schema_version": SCHEMA_VERSION,
            "classes": len(self.matrix.classes),
            "papers": len(PAPER_IDS),
            "pairs": self.matrix.pairs,
            "not_swept_pairs": self.not_swept_pairs,
            "unmechanised_classes": [c.class_id for c in self.matrix.unmechanised],
            "single_paper_classes": [c.class_id for c in self.matrix.single_paper_classes],
            "outcome": self.outcome.value,
            "by_paper": [
                {
                    "paper_id": p.paper_id,
                    "found": p.found,
                    "swept_clean": p.swept_clean,
                    "not_swept": p.not_swept,
                    "decided_fraction": round(p.decided_fraction, 6),
                }
                for p in self.matrix.by_paper()
            ],
        }


def _load_one(path: Path) -> FailureClass:
    raw = json.loads(path.read_text())
    detector = raw.get("detector")
    return FailureClass(
        class_id=raw.get("class_id") or path.parent.name,
        detector=detector if detector else None,
        found_in=frozenset(int(p) for p in raw.get("found_in", ())),
        sweeps=tuple(
            SweepEvidence(
                paper_id=int(s["paper_id"]),
                detector=s["detector"],
                run=s["run"],
                found=bool(s["found"]),
            )
            for s in raw.get("sweeps", ())
        ),
    )


def load_failure_classes(root: Path) -> tuple[FailureClass, ...]:
    """Read every declared class under ``root``.

    A directory with no :data:`DECLARATION` is not skipped. It is loaded as an
    undeclared class -- no detector, no papers -- so that adding a failure record
    without declaring its scope shows up as 15 open cells rather than as nothing
    at all.
    """

    out = []
    for directory in sorted(p for p in root.iterdir() if p.is_dir()):
        declaration = directory / DECLARATION
        if declaration.exists():
            out.append(_load_one(declaration))
        else:
            out.append(FailureClass(class_id=directory.name, detector=None, found_in=frozenset()))
    return tuple(out)


def coverage_matrix(classes: Iterable[FailureClass]) -> CoverageMatrix:
    return CoverageMatrix(classes=tuple(classes))
