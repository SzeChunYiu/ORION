# ORION-21 publication-freeze addendum V1

**Freeze date:** 2026-08-31  
**Status:** `CURRENT_EARNED_CEILING_FROZEN__WIDTH_CONDITIONED__FAMILY_SCALE_SUCCESSOR_ONLY`

This addendum is part of the frozen ORION-21 paper-content packet. It records the
ceiling already established in `P11_ACTIVE_CLAIM_AUTHORITY_V2.json` and grants no
authority that record does not already carry.

## Earned scientific ceiling

The active terminal is `P11_WIDTH_CONDITIONED_AUTHORITY_SUPPORTED`, and the
paper-level outcome is `SUPPORTED_WITH_EXPLICIT_WIDTH_AND_RESPONSIBILITY_BOUNDARIES`.

The supported claim is `P11.R7.POOLED_ATTACK_ADVANTAGE`, status
`SUPPORTED_REPLICATED`, terminal `P11I_HIGH_WIDTH_ADVANTAGE_REPLICATED_WIDE_PANEL`.
Its maximum authorized wording is fixed in the authority record and is reproduced
here without extension:

> Across three independent RNG replicates and three fixed geometry strata, all nine
> prespecified r=7 seed-by-geometry cells passed the frozen non-compensatory gates
> while the matched r=3 controls kept the pooled attack live.

That result is scoped to compiled-state width 7, three execution seeds, three fixed
geometry strata, three independent random replicates, nine prespecified
seed-by-geometry cells, and five repeated queries per cell. The width condition is
not decoration: it is the boundary the paper's title claim is conditioned on.

The peer-review decision recorded in `PEER_REVIEW_READINESS.md` is
`READY_FOR_EXTERNAL_REVIEW_AS_CONTROLLED_THEORY/SYSTEMS_SUPERIORITY_RESULT`, scoped
by that same terminal and by the width and responsibility boundaries below.

## Frozen boundary

A binding negative is part of this freeze, not an omission from it. Claim
`P11.QUERY_FAMILY.DIGITS.V1` carries authority `BINDING_NEGATIVE_BOUNDARY` and
terminal `P11_QUERY_FAMILY_PHASE_V1_GATE_NOT_MET`: family-scale 16-of-64 learned
compilation was supported for 3 of 10 digit responsibilities under LINEAR access and
5 of 10 under each of RBF and KNN, against a frozen gate of at least 8 of 10 within a
0.02 quality tolerance. The registered resource identities held exactly, and the
study was not retuned. Family-scale compilation support on digits is therefore
refuted at the frozen gate, and the paper says so.

The earlier narrow-width result `P11.R3.POOLED_ATTACK_ADVANTAGE`
(`P11H_POOLED_UNIVERSAL_ATTACK_PREVAILED`) is retained as a historical boundary and
not as an active positive claim: the pooled attack prevailed in the registered
narrow-width regime, and the r=7 result must never be generalized across state width.

The authority record forbids four promotions, and this freeze licenses none of them:
an unconditional compiled-state advantage; family-scale compilation support on
digits; nine independent random replicates (there are three, across nine cells); and
real-system superiority.

`check_p11_adverse_integration_v2.py` passes with
`scientific_authority_delta: BOUNDARY_NARROWING_ONLY`. Integrating the adverse family
result narrowed what this paper may claim; it did not widen it.

## Frozen content surface

The content packet consists of `manuscript/main.tex` and its sections,
`CLAIM_EVIDENCE_LEDGER.md`, `PEER_REVIEW_READINESS.md`,
`P11_ACTIVE_CLAIM_AUTHORITY_V2.json` and the evidence it binds, the adverse
integration checker `check_p11_adverse_integration_v2.py`, and this addendum. The
ORION-21 claim is about moving structural search between representation construction
and downstream use under a stated width condition; it does not own the
responsibility-transport results of its sibling papers.
