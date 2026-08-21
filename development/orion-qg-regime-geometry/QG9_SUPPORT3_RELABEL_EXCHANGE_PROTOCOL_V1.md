# QG-9 V3 support-3 relabel-exchange theorem — protocol V1

Date frozen: 2026-08-21. Parent issue: #762. Parent stacked PR: #786.
Frozen parent commit: `51d81c448a67c7da8e89310c02ef890f5afd0f7b`, which already carries the protected support<=4 theorem receipt.
Authority ceiling: bounded R6I theorem candidate only; no support<=2, tightness, novelty, R6, or physical-advantage authority.

## Parent theorem

QG-9 V2 earned:

`QG9_RANK2_ALL_N_SUPPORT4_SUFFICIENCY_MACHINE_CHECKED`.

Its deletion-only combined grammar closes every support-5 irreducible boundary but leaves 36/432 support-4 patterns unresolved. Those 36 are a **method boundary**, not tightness evidence.

## New edit grammar

V3 enlarges only the **local edit**, not the R6I compiler grammar or objective.

At one qubit a block has independent generator letters `(a,b)` and fixed shared Tag letters `(s0,s1)`. A replacement `(a',b')` is admitted iff:

- if `a=I`, then `a'=I`; otherwise `a'` may be any of `{I,X,Y,Z}`;
- if `b=I`, then `b'=I`; otherwise `b'` may be any of `{I,X,Y,Z}`;
- `(a',b') != (a,b)`.

Thus the edit can delete or **relabel an already-active local generator letter**, but can never add generator support on a previously inactive coordinate. The dependent third letter is recomputed exactly as `a'*b'`.

No target, Tag, central choice, permutation, or other block coordinate is changed.

## Exact semantic signature

For each concrete local state and replacement compute

`delta_sigma = sigma(a,b,s0,s1) XOR sigma(a',b',s0,s1)`

where

`sigma = (<R0,R1>, <S0,R0>, <S1,R0>, <S0,R1>, <S1,R1>) in F_2^5`.

A multi-column relabel/edit is globally semantics-preserving iff its signature XOR is zero.

## Exact worst-case local cost certificate

Use the frozen R6I local objective, including:
- three frame multipliers `(4,4,4)` with the selected central branch reduced to `2`;
- all three Restore supports;
- dependent third frame recomputed before and after;
- Tag unchanged.

For each concrete local state and replacement, compute `Delta C` over every target triple `(p0,p1,p2) in {I,X,Y,Z}^3`, separately for every central choice. Store the **maximum** per central.

A multi-column edit is safe only when summed maxima are `<=0` for all three central choices. Therefore the certificate is adversarial over target letters and valid independently of the particular instance targets.

## Action-profile types

The V2 descriptor alone is insufficient because different concrete Pauli/Tag representatives can admit different relabel signatures. V3 therefore groups local states only when they have:

1. the same V2 descriptor
   `(a_active,b_active,coincidence,alpha,beta00,beta10,beta01,beta11)`;
2. the same complete Pareto-minimal action profile, where each retained action records
   `(delta_sigma, worst_cost_vector, R0_support_drop, R1_support_drop, replacement)`.

No profile equivalence is assumed before exact enumeration.

For each `(delta_sigma, R0_drop, R1_drop)` keep every nondominated replacement needed to preserve the componentwise cost frontier; deterministic tie-break is lexicographic replacement code.

## Support-4 closure test

V2 already proves all but 36 support-4 descriptor patterns reducible under a strict subset of the V3 action grammar. V3 must mechanically verify that the old deletion actions are contained in the new grammar, then needs only attack the 36 V2 survivors.

For **every concrete action-profile-type combination** compatible with each of those 36 descriptor patterns, search the finite product of local actions plus `none`.

A valid combined move must:
- have total five-bit signature zero;
- delete at least one R0 support coordinate;
- never add R0/R1 support;
- have total worst-case cost `<=0` for each central choice.

Primary gate: every support-4 survivor/type combination has a valid move.

If so, V2 support<=4 plus this closure gives by lexicographic descent:

> every frozen-R6I optimum admits all four independent generators with support <=3, for every n and admitted instance.

## Support-3 boundary control

Use the same broad QG-1 irreducibility superset at support 3. V2's deletion-only grammar already closes some of this domain and leaves a finite unresolved set. V3 must enumerate every action-profile-type combination of the unresolved support-3 patterns and report whether the richer grammar leaves any unsafe case.

A nonempty unsafe set blocks support<=2 under this edit grammar. It is **not** a support-3 tightness theorem.

No expected pattern/type counts are supplied to the official checker.

## Independent verification

Generic ORION verifier rebuilds phase-free one-qubit Pauli algebra, replacement grammar, five-bit signatures, cost envelopes, profile grouping, and support-4/support-3 searches without importing R6I production tables or the candidate checker.

Native ORION-Q verifier binds:
- parent V2 protected support<=4 receipt;
- canonical QG-1 family/objective boundary;
- production R6I local algebra;
- exact authority ceiling.

## Honest terminals

- `QG9_RANK2_ALL_N_SUPPORT3_SUFFICIENCY_MACHINE_CHECKED`
- `QG9_SUPPORT4_RELABEL_EXCHANGE_COUNTEREXAMPLE_FOUND`
- `QG9_ACTION_PROFILE_BINDING_GAP`
- `QG9_GENERIC_NATIVE_DISAGREEMENT`
- `QG9_CANNOT_CHECK`

## Stop boundary

Even a positive V3 may not claim support<=2 or tightness. A support-3 obstruction under this grammar is only a **method obstruction** and becomes the input to a separate successor lane.
