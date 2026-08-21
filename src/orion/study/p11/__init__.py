"""P11 instruments that make a survived hostile attack report what it measured.

P11G is the paper's ``SUPPORTED / HOSTILE NONLINEAR / PRIMARY`` evidence. Its
terminal is a live conjunction, its seed is published, its estimator seeds are
pinned, and a two-subprocess byte-identical replay sits inside the terminal
decision path. Two of its four scientific gates are the hostile test, and the
96-tree ExtraTrees arm they read sits at chance --- ``0.5376`` at ``n=64``
against a ``0.5`` floor --- in every world the frozen protocol admits. Over 48
fresh seeds the gates hold 48 times, so ``GAP_SUPPORTED`` is the only terminal
the artifact could have printed.

The arm is not broken: shrink the bank it must search from 2,380 columns to 5
and the same conjunction prints ``GAP_NOT_MET``. And the register was not empty:
``P11C_STRONGER_DECODER_ATTACK_PROTOCOL_V1.md`` froze three universal arms and
the rule "the earliest threshold reached by any", and running that rule on
P11G's own frozen data gives thresholds of 128 and 256 against a gate of
``>= 256`` --- which fails, in 12 of 12 seeds.

:mod:`decoder_attack_reach` registers the shipped runner, the four gates, and
two registers of worlds: ones the freeze admits, for attainability, and ones it
does not, for capability. :mod:`attack_audit` runs them and blocks when a
survived attack turns out to have had no reachable win. The mechanism itself is
:mod:`orion.programme.gate_attainability`, unchanged and pointed at the losing
arm instead of the winning one; it builds its verdict from
:class:`orion.programme.guard_exercise.GuardExercise`.

The failure they close is recorded under
``research/failures/2026-08-unwinnable-attack-predetermined-survival/``.
"""

from __future__ import annotations

from .decoder_attack_reach import (
    ALL_ARMS,
    DECODER_CONTROL_ARM,
    DEFENCE_ARM,
    GATES,
    NOT_MET_TERMINAL,
    REGISTERED_UNIVERSAL_ARMS,
    REPORTED_ARM,
    SHIPPED_SCIENTIFIC_SHA256,
    SHIPPED_TERMINAL,
    AttackSpec,
    CellReading,
    P11GFidelityError,
    admissible_worlds,
    arm_axis,
    attack_responsiveness,
    best_of_arms_gate,
    best_of_arms_thresholds,
    capability_cases,
    closest_refuting_margin,
    decoder_family_share,
    gate_booleans,
    gate_reaches,
    gate_values,
    measure,
    nuisance_ladder,
    receipt,
    registered_pool,
    require_fidelity,
    seed_sweep,
    shipped_curves_match,
    shipped_scientific_sha256,
    shipped_spec,
    terminal_of,
    terminal_reach,
    terminal_under_arm,
)

__all__ = [
    "ALL_ARMS",
    "DECODER_CONTROL_ARM",
    "DEFENCE_ARM",
    "GATES",
    "NOT_MET_TERMINAL",
    "REGISTERED_UNIVERSAL_ARMS",
    "REPORTED_ARM",
    "SHIPPED_SCIENTIFIC_SHA256",
    "SHIPPED_TERMINAL",
    "AttackSpec",
    "CellReading",
    "P11GFidelityError",
    "admissible_worlds",
    "arm_axis",
    "attack_responsiveness",
    "best_of_arms_gate",
    "best_of_arms_thresholds",
    "capability_cases",
    "closest_refuting_margin",
    "decoder_family_share",
    "gate_booleans",
    "gate_reaches",
    "gate_values",
    "measure",
    "nuisance_ladder",
    "receipt",
    "registered_pool",
    "require_fidelity",
    "seed_sweep",
    "shipped_curves_match",
    "shipped_scientific_sha256",
    "shipped_spec",
    "terminal_of",
    "terminal_reach",
    "terminal_under_arm",
]
