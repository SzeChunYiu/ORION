# The authority mutation controls could not fail — and the model they guard is fine

**Status:** `CONTROL_GAP_FOUND_AND_REPAIRED__UNDERLYING_MODEL_CONFIRMED_SOUND`
**Scientific authority delta:** `NONE`.

## What this is about

`check_merged_formalization_v1.py` reports `all_mutants_detected: true` for three authority
mutants, and issue #49's box 389 — *"independently verify non-amplification / domain / epoch
confinement"* — cites that result as closed.

Two of its three mutation-control groups are real, and should be said so first:

| control group | exercises |
|---|---|
| `mutant_selective_controls` | `affected`, `descendants` |
| `mutant_donor_controls` | `candidate_relation`, `ideal_typed_product` |
| `mutant_authority_controls` | **neither `repair_authority` nor anything derived from it** |

## The gap

`mutant_authority_controls` in full:

```python
before_auth = AuthorityState(AUTHORIZED, "h0", 7, True)
bad_cross_domain = AUTHORIZED if (before_auth.terminal == AUTHORIZED
                                  and before_auth.support_survives) else CANNOT_CHECK
catches_domain = bad_cross_domain == AUTHORIZED
...
bad_reground = AUTHORIZED
catches_reground = auth_bit(bad_reground) > auth_bit(before_unknown.terminal)
```

`before_auth` is a literal with `terminal=AUTHORIZED` and `support_survives=True`, so both
conditionals are decided at authorship time. `auth_bit(t)` is `int(t == AUTHORIZED)`, so
`catches_reground` is `1 > 0`.

**All three are constant `True`.** The function takes no arguments, mutates nothing, and
cannot report a missed mutant under any change whatsoever to the model it nominally guards.

Verified by AST rather than by reading: the function's call set is exactly
`{AuthorityState, auth_bit}`.

## The model itself is sound — that part of box 389 stands

`authority_audit` really does drive `repair_authority` over the state product, and
`repair_authority` really does refuse `AUTHORIZED` without either fresh authority or
transport of an already-authorized certificate whose support survives, in the same domain
and the same epoch.

`check_authority_mutants_really_mutate_v1.py` confirms it independently: **0 violations of
the non-amplification invariant across 384 states.**

So what was missing was never the model. It was the evidence that the audit would notice if
the model stopped being right.

## The replacement

Each mutant is now a real alternative `repair_authority`, evaluated over the same state
product, and "detected" only when the invariant actually fails:

| mutant | violations | detected |
|---|---:|---|
| `ignore_domain_binding` | 4 | yes |
| `ignore_epoch_binding` | 4 | yes |
| `obligation_free_reground_without_new_authority` | **48** | yes |
| `_meta_identical_must_not_be_detected` | 0 | **no — as required** |

The meta-control is the load-bearing one. A behaviourally identical model must come back
*undetected*, because without that a control reporting "everything detected" is
indistinguishable from one returning `True` unconditionally, which is the defect being
repaired.

## How this sits beside the amplification attack

`a6-amplification-real-classifier-v1/` shows the same attack **landing** on ORION-16's
shipped `classify()`: four amplifying edges, five of them realized inside ORION-16's own
24-case set.

Those two results are not in tension, and together they are sharper than either alone:

- **The specification is non-amplifying.** `repair_authority` forbids obligation-free
  re-grounding by construction, and 384 states confirm it.
- **The implementation is not.** ORION-16's shipped classifier has no coordinate
  distinguishing a condition satisfied by evidence from one satisfied by absence, so the
  same re-grounding reaches `ADMISSIBLE` there.

That is a specification/implementation gap, and it is the most precise statement the A6
programme has produced about what the composed system does and does not guarantee. A
manuscript may claim the first. It may not claim the second without the guard from
`a6-amplification-real-classifier-v1/REPAIR_PROTOCOL_V1.md`.

## What box 389 should say

Its substance holds for the merged formalization and does not hold for the shipped
classifier. The box is not wrong to be checked, and the finding above belongs beside it,
because a reviewer who runs the shipped checker will see the attack land.
