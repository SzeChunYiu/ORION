#!/usr/bin/env python3
"""Real mutation controls for the merged formalization's authority half.

`check_merged_formalization_v1.py` reports `all_mutants_detected: true` for three
authority mutants, and #49's box 389 -- *"independently verify
non-amplification/domain/epoch confinement"* -- cites that result. Two of its three
mutation-control groups do exercise their model: `mutant_selective_controls` calls
`affected` and `descendants`, `mutant_donor_controls` calls `candidate_relation`
and `ideal_typed_product`.

`mutant_authority_controls` calls neither `repair_authority` nor anything else that
depends on it. Its whole body is:

    before_auth = AuthorityState(AUTHORIZED, "h0", 7, True)
    bad_cross_domain = AUTHORIZED if (before_auth.terminal == AUTHORIZED
                                      and before_auth.support_survives) else CANNOT_CHECK
    catches_domain = bad_cross_domain == AUTHORIZED
    ...
    bad_reground = AUTHORIZED
    catches_reground = auth_bit(bad_reground) > auth_bit(before_unknown.terminal)

`before_auth` is a literal with `terminal=AUTHORIZED` and `support_survives=True`,
so both conditionals are decided at authorship time, and `catches_reground` is
`1 > 0`. All three are constant `True`. The function takes no arguments, mutates
nothing, and cannot report a missed mutant under any change to the model.

The audit itself is fine -- `authority_audit` really does drive `repair_authority`
over the full product of states, and `repair_authority` really does refuse to reach
`AUTHORIZED` without `new_authority` or same-domain-same-epoch transport. What is
missing is the evidence that the audit would notice if it stopped doing so.

This supplies that. Each mutant is a real alternative `repair_authority`; the same
invariant is evaluated over the same state product against each; and a mutant is
"detected" only when the invariant actually fails on it.

The meta-control matters most: a mutant that is behaviourally identical to the true
model must come back UNDETECTED. Without it, a control that reports everything
detected is indistinguishable from one that reports `True` unconditionally --
which is the defect being repaired.

Exit 0 controls are real and every mutant is caught, 1 otherwise.
"""
from __future__ import annotations

import itertools
import json
from dataclasses import dataclass

AUTHORIZED = "AUTHORIZED"
DENIED = "DENIED"
CANNOT_CHECK = "CANNOT_CHECK"
TERMINALS = (AUTHORIZED, DENIED, CANNOT_CHECK)


@dataclass(frozen=True)
class AuthorityState:
    terminal: str
    domain: str
    epoch: int
    support_survives: bool


def repair_authority(before: AuthorityState, *, target_domain: str, target_epoch: int,
                     new_authority: bool, blocker_established: bool = False) -> str:
    """The model as `check_merged_formalization_v1.py` defines it."""

    if blocker_established:
        return DENIED
    if new_authority:
        return AUTHORIZED
    if (before.terminal == AUTHORIZED and before.support_survives
            and target_domain == before.domain and target_epoch == before.epoch):
        return AUTHORIZED
    return CANNOT_CHECK


# --- the mutants, each a real alternative model ------------------------------


def m_ignore_domain(before, *, target_domain, target_epoch, new_authority,
                    blocker_established=False):
    if blocker_established:
        return DENIED
    if new_authority:
        return AUTHORIZED
    if (before.terminal == AUTHORIZED and before.support_survives
            and target_epoch == before.epoch):           # domain binding dropped
        return AUTHORIZED
    return CANNOT_CHECK


def m_ignore_epoch(before, *, target_domain, target_epoch, new_authority,
                   blocker_established=False):
    if blocker_established:
        return DENIED
    if new_authority:
        return AUTHORIZED
    if (before.terminal == AUTHORIZED and before.support_survives
            and target_domain == before.domain):          # epoch binding dropped
        return AUTHORIZED
    return CANNOT_CHECK


def m_obligation_free_reground(before, *, target_domain, target_epoch, new_authority,
                               blocker_established=False):
    """The A6 amplification attack: re-grounding grants authority by itself."""

    if blocker_established:
        return DENIED
    if new_authority:
        return AUTHORIZED
    if target_domain != before.domain:      # a re-grounding into another domain
        return AUTHORIZED                   # ... is treated as authorising
    if (before.terminal == AUTHORIZED and before.support_survives
            and target_epoch == before.epoch):
        return AUTHORIZED
    return CANNOT_CHECK


def m_identical(before, **kw):
    """Behaviourally identical to the true model. MUST come back undetected."""

    return repair_authority(before, **kw)


MUTANTS = {
    "ignore_domain_binding": m_ignore_domain,
    "ignore_epoch_binding": m_ignore_epoch,
    "obligation_free_reground_without_new_authority": m_obligation_free_reground,
    "_meta_identical_must_not_be_detected": m_identical,
}

DOMAINS = ("h0", "h1")
EPOCHS = (7, 8)


def _states():
    for terminal, dom, ep, sup in itertools.product(TERMINALS, DOMAINS, EPOCHS, (False, True)):
        before = AuthorityState(terminal, dom, ep, sup)
        for tdom, tep, newauth, blocker in itertools.product(
            DOMAINS, EPOCHS, (False, True), (False, True)
        ):
            yield before, dict(target_domain=tdom, target_epoch=tep,
                               new_authority=newauth, blocker_established=blocker)


def violations(model) -> list[dict]:
    """Where does this model grant AUTHORIZED without a licence to?

    The invariant, stated once: reaching AUTHORIZED requires either fresh
    authority, or transport of an already-authorized certificate whose support
    survives, in the same domain and the same epoch.
    """

    bad = []
    for before, kw in _states():
        if kw["blocker_established"]:
            continue
        got = model(before, **kw)
        licensed = kw["new_authority"] or (
            before.terminal == AUTHORIZED
            and before.support_survives
            and kw["target_domain"] == before.domain
            and kw["target_epoch"] == before.epoch
        )
        if got == AUTHORIZED and not licensed:
            bad.append({"before": before.__dict__, **kw})
    return bad


def main() -> int:
    states = sum(1 for _ in _states())
    true_violations = violations(repair_authority)

    detected: dict[str, dict] = {}
    for name, model in MUTANTS.items():
        found = violations(model)
        detected[name] = {"violations": len(found), "detected": bool(found)}

    problems: list[str] = []
    if true_violations:
        problems.append(
            f"the true model itself violates the invariant in {len(true_violations)} states"
        )
    for name in ("ignore_domain_binding", "ignore_epoch_binding",
                 "obligation_free_reground_without_new_authority"):
        if not detected[name]["detected"]:
            problems.append(f"mutant {name} was NOT detected")
    if detected["_meta_identical_must_not_be_detected"]["detected"]:
        problems.append(
            "the identical-model meta-control was 'detected', so this check is "
            "reporting True unconditionally -- exactly the defect it repairs"
        )

    payload = {
        "schema": "ORION.A6.AuthorityMutationControlsAreReal.v1",
        "repairs": "mutant_authority_controls in check_merged_formalization_v1.py, "
                   "whose three controls are constant True and call no model",
        "states_exercised_per_model": states,
        "true_model_violations": len(true_violations),
        "mutants": detected,
        "meta_control": "a behaviourally identical model must come back UNDETECTED",
        "problems": problems,
        "scientific_authority_delta": "NONE",
        "status": "REAL_CONTROLS_ALL_MUTANTS_CAUGHT" if not problems else "FAILED",
    }
    print(json.dumps(payload, indent=2, sort_keys=True))
    return 0 if not problems else 1


if __name__ == "__main__":
    raise SystemExit(main())
