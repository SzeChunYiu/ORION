#!/usr/bin/env python3
"""Deterministic falsifiers for CROSS_PAPER_PRESERVATION_THEORY_V1.

The checker instantiates non-implication pairs across computational support,
semantic evidence, target-obligation discharge and commit authority. It is a
small theorem-boundary fixture, not a proof that the ladder is novel or complete.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class PreservationCase:
    name: str
    identity: bool
    support: bool
    semantic_evidence: bool
    target_obligation: bool
    commit_authority: bool


def can_transport(case: PreservationCase, required_levels: tuple[int, ...]) -> bool:
    level_state = {
        0: case.identity,
        1: case.support,
        2: case.semantic_evidence,
        3: case.target_obligation,
        4: case.commit_authority,
    }
    return all(level_state[level] for level in required_levels)


def main() -> int:
    cases = (
        PreservationCase(
            "computational_reuse_but_obligation_open",
            identity=True,
            support=True,
            semantic_evidence=True,
            target_obligation=False,
            commit_authority=False,
        ),
        PreservationCase(
            "evidence_survives_but_new_objective_not_closed",
            identity=True,
            support=True,
            semantic_evidence=True,
            target_obligation=False,
            commit_authority=False,
        ),
        PreservationCase(
            "source_local_discharge_not_foreign_discharge",
            identity=True,
            support=True,
            semantic_evidence=True,
            target_obligation=False,
            commit_authority=False,
        ),
        PreservationCase(
            "obligation_satisfied_but_authority_stale",
            identity=True,
            support=True,
            semantic_evidence=True,
            target_obligation=True,
            commit_authority=False,
        ),
        PreservationCase(
            "fully_preserved_positive_control",
            identity=True,
            support=True,
            semantic_evidence=True,
            target_obligation=True,
            commit_authority=True,
        ),
    )

    computational = cases[0]
    assert can_transport(computational, (0, 1))
    assert not can_transport(computational, (0, 1, 2, 3))

    evidence_only = cases[1]
    assert can_transport(evidence_only, (0, 2))
    assert not can_transport(evidence_only, (0, 2, 3))

    foreign_domain = cases[2]
    assert can_transport(foreign_domain, (0, 1, 2))
    assert not can_transport(foreign_domain, (0, 1, 2, 3))

    stale_authority = cases[3]
    assert can_transport(stale_authority, (0, 1, 2, 3))
    assert not can_transport(stale_authority, (0, 1, 2, 3, 4))

    positive = cases[4]
    assert can_transport(positive, (0, 1, 2, 3, 4))

    print("P6-P8 preservation ladder V1: PASS")
    print("  computational/support preservation !-> target obligation: confirmed")
    print("  semantic evidence preservation !-> closure/discharge: confirmed")
    print("  source-valid judgment !-> target-domain discharge: confirmed")
    print("  target obligation satisfied !-> current commit authority: confirmed")
    print("  all-required-levels positive transport control: confirmed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
