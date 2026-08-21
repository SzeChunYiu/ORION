# QG-9 V4 — full-acceptance closure from support 3 to support 2

Date frozen: 2026-08-21. Parent issue: #762.
Frozen parent commit: `4d70700ba23a8276d4610203124fc178f3929a58`, carrying the protected V3 support<=3 theorem receipt.
Authority ceiling: bounded R6I theorem candidate only; no support<=1, tightness, novelty, R6, or physical-advantage authority.

## Parent theorem and residual

V3 earned:

`QG9_RANK2_ALL_N_SUPPORT3_SUFFICIENCY_MACHINE_CHECKED`.

The V3 relabel+delete grammar is support-nonincreasing, preserves the full five-bit single-block syndrome, and has adversarial all-target/all-central cost certificates. On the deliberately broad support-3 QG-1-irreducibility superset it leaves 21 unsafe action-profile cases.

Those 21 were retained solely as an anti-overclaim boundary. The broad domain does **not** enforce the complete R6I block acceptance condition for the second independent generator's Tag label.

V4 introduces **no new edit**. It tests whether the remaining broad-superset obstructions are realizable compiler states.

## Full R6I block acceptance

For a descriptor multiset, XOR local coordinates across the selected generator support:

- `alpha = <R0,R1>`;
- `u0 = <S0,R0>`, `v0 = <S1,R0>`;
- `u1 = <S0,R1>`, `v1 = <S1,R1>`.

Define branch labels

`c0 = 2*u0 + v0`,
`c1 = 2*u1 + v1`.

A selected block is fully admissible iff:

1. `alpha == 1`;
2. `c0 in {1,2,3}`;
3. `c1 in {1,2,3}`;
4. `c0 != c1`.

Then dependent label `c2=c0 XOR c1` is automatically the third nonzero label and `R2=R0R1` has the correct shared-Tag labeling. Global anticommutation implies both independent generators are nonzero.

Cross-block label equality does not need to be re-solved: every V3 edit has zero five-bit syndrome change, so starting equality to the untouched other block is preserved. Treating every individually accepted selected-block slice as realizable is conservative; the true global domain is a subset.

## Support-3 theorem gate

Reconstruct V3's complete broad support-3 boundary from its frozen parent code and protected result:

1. QG-1-reducible patterns are already handled by QG-1 moves;
2. V2 deletion-safe patterns are already handled by V2;
3. V2-survivor / V3-rich-safe profile cases are already handled by V3;
4. only V3-rich-unsafe profile cases remain.

For every remaining V3-rich-unsafe support-3 profile case, evaluate full block acceptance from the descriptor XORs.

Primary gate:

**zero V3-rich-unsafe support-3 profile cases are fully accepted R6I blocks.**

Then parent V3 support<=3 plus exhaustion of every accepted support-3 boundary yields by lexicographic descent:

> every optimum of the frozen R6I grammar admits all four independent generators with support <=2, for every n and every admitted instance.

No new local cost lemma is introduced in V4; all reducing moves are already protected parent evidence.

## Support-2 boundary control

Reconstruct the broad support-2 QG-1-irreducible/V2-deletion-survivor domain, expand into V3 action-profile types, and apply the same full R6I acceptance predicate.

Report:
- fully accepted support-2 type cases;
- accepted cases safe under V3 relabel+delete grammar;
- accepted cases unsafe under V3 grammar.

A nonempty accepted unsafe set blocks support<=1 under the current theorem stack. It is **not** a proof that support 2 is necessary for any concrete target instance.

No expected counts are supplied to the official checker.

## Independent verification

Generic ORION verifier uses the independently implemented V3 generic algebra/action search, reconstructs the support-3/support-2 boundary and full acceptance filter, and must reproduce all candidate counts without importing production R6I or the V4 candidate checker.

Native ORION-Q verifier binds:
- protected V3 support<=3 receipt;
- production R6I acceptance semantics / local algebra;
- zero five-bit-delta preservation;
- authority ceiling.

## Honest terminals

- `QG9_RANK2_ALL_N_SUPPORT2_SUFFICIENCY_MACHINE_CHECKED`
- `QG9_VALID_SUPPORT3_OBSTRUCTION_FOUND`
- `QG9_PARENT_BOUNDARY_RECONSTRUCTION_GAP`
- `QG9_GENERIC_NATIVE_DISAGREEMENT`
- `QG9_CANNOT_CHECK`

## Stop boundary

Even a positive V4 may not claim support<=1 or support-2 tightness. Any surviving accepted support-2 obstruction is a method boundary only and must be resolved by an exact target-level tightness experiment or a separately frozen stronger edit theorem.
