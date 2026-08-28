"""Typed-versus-flat analysis and first-mixing detection.

Two evaluations of the same rule system:

* **typed** - the powerset-license least fixed point. A claim's label is the set
  of authorities (licenses) each of which independently carries the whole
  derivation. Authorized means the label is non-empty.
* **flat** - the same operator over a one-element license universe, i.e. the
  license-erased reading: derivable at all, with no record of which authority
  carried it.

A claim is a **first-mixing** (hybrid) authorization when it is flat-authorized
but has an empty typed label: the merged system derives it, yet no single
constituent authority does. That is the whole distinction the calculus makes.
"""

from __future__ import annotations

from typing import Any, Dict, FrozenSet, List, Mapping, Optional, Tuple

from .core import (
    FLAT_TOKEN,
    Evaluation,
    Instance,
    Rule,
    flat_projection,
    least_fixed_point,
    proof_tree,
    retraction,
)
from .model import Problem


def flat_instance(problem: Problem) -> Instance:
    """Build the license-erased instance, honouring `flat_seeded_claims`.

    This overrides seeds only. Claims in `refuted` are refuted in both readings:
    `flat_projection` carries the refutation set through unchanged, so a directly
    refuted claim is bottom in the flat view too.

    `flat_seeded_claims` exists because a flat merge can be *less* faithful than
    simply forgetting licenses: a textual concatenation may also lose the
    retraction material that the typed view still honours (for example
    concatenating certificate bundles drops the CRL side-files that accompany
    them). When the field is absent the flat seed set is exactly the claims with
    a non-empty typed seed, so the two views differ only by license erasure.
    """
    base = flat_projection(problem.instance)
    if problem.flat_seeded_claims is None:
        return base
    seeds = {
        claim: (frozenset({FLAT_TOKEN}) if claim in problem.flat_seeded_claims else frozenset())
        for claim in problem.claims
    }
    return Instance(
        licenses=base.licenses,
        claims=base.claims,
        seeds=seeds,
        rules=base.rules,
        refuted=base.refuted,
    )


class Report:
    """Evaluation of one SCHEMA_V1 problem."""

    def __init__(self, problem: Problem) -> None:
        self.problem = problem
        self.typed: Evaluation = least_fixed_point(problem.instance)
        self.flat: Evaluation = least_fixed_point(flat_instance(problem))

    def typed_label(self, claim: str) -> FrozenSet[str]:
        return self.typed.label(claim)

    def typed_authorized(self, claim: str) -> bool:
        return self.typed.is_authorized(claim)

    def flat_authorized(self, claim: str) -> bool:
        return self.flat.is_authorized(claim)

    def first_mixing(self, claim: str) -> bool:
        """Flat derives it, no single authority does."""
        return self.flat_authorized(claim) and not self.typed_authorized(claim)

    def witness_tree(self, claim: str, license: str) -> Optional[dict]:
        return proof_tree(self.problem.instance, self.typed, claim, license)

    def as_dict(self) -> Dict[str, Any]:
        targets = self.problem.targets or tuple(sorted(self.problem.claims))
        rows = {}
        for target in targets:
            label = sorted(self.typed_label(target))
            rows[target] = {
                "typed_authorized": self.typed_authorized(target),
                "typed_licenses": label,
                "flat_authorized": self.flat_authorized(target),
                "first_mixing": self.first_mixing(target),
                "witness": self.witness_tree(target, label[0]) if label else None,
            }
        return {
            "schema": "ORION.TypedMerge.Report.v1",
            "id": self.problem.id,
            "title": self.problem.title,
            "rounds": {"typed": self.typed.rounds, "flat": self.flat.rounds},
            "targets": rows,
            "first_mixing_targets": sorted(t for t in targets if self.first_mixing(t)),
        }


def retraction_report(problem: Problem, refute: List[str]) -> Dict[str, Any]:
    """Theorem 5 retraction: the pairs lost when `refute` is added to R."""
    pre, post, lost = retraction(problem.instance, refute)
    return {
        "refuted": sorted(refute),
        "pairs": sorted([list(p) for p in lost]),
        "pre_pairs": len(pre.pairs),
        "post_pairs": len(post.pairs),
        "retained_pairs": sorted([list(p) for p in post.pairs]),
    }


def check_expectations(problem: Problem, report: Report) -> List[str]:
    """Compare a report against the document's `expect` block.

    Returns a list of human-readable mismatches; empty means every declared
    expectation held exactly.
    """
    failures: List[str] = []
    expect = problem.expect
    for field, getter in (
        ("typed_authorized", report.typed_authorized),
        ("flat_authorized", report.flat_authorized),
        ("first_mixing", report.first_mixing),
    ):
        for claim, want in (expect.get(field) or {}).items():
            got = getter(claim)
            if got != want:
                failures.append(f"{field}[{claim}]: expected {want}, got {got}")
    for claim, want in (expect.get("typed_licenses") or {}).items():
        got = sorted(report.typed_label(claim))
        if got != sorted(want):
            failures.append(f"typed_licenses[{claim}]: expected {sorted(want)}, got {got}")
    expected_retraction = expect.get("retraction")
    if expected_retraction:
        actual = retraction_report(problem, expected_retraction.get("refute", []))
        want_pairs = sorted([list(p) for p in expected_retraction.get("pairs", [])])
        if actual["pairs"] != want_pairs:
            failures.append(
                f"retraction pairs: expected {want_pairs}, got {actual['pairs']}"
            )
    return failures
