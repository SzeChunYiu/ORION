# QG-22 — minimal hidden-home state quotient for J5 protocol V1

Date: 2026-08-22
Issue: #868
Parent: QG-7d information closure PR #860 / issue #836
Branch: `codex/orion-qg-qg22-hidden-home-state-20260822`
Status: **FROZEN BEFORE QG-22 OFFICIAL ENUMERATION / FEATURE-SUBSET OUTCOME.**
Authority ceiling: exact local state-quotient result only; no all-n B'' completeness, novelty, R6, or physical-advantage authority.

## Parent obstruction

QG-7d established that the visible pinned-PP T4b state omits a phantom-home environment. With that visible state fixed, the hidden six local Pauli letters span `4^6=4096` environments and the proposed J5 Restore contribution spans every integer from `-4` through `+4`. Therefore the current quotient cannot price J5.

QG-22 asks whether this missing information can be compressed into a small exact structural signature.

## Disclosed exploratory target

This V1 is confirmatory. Before freeze, exploratory first-principles enumeration of one hidden branch with letters `(a,b,c)` and modifier `m` used

`delta_m = F3(a,b,c) - F3(a,b*m,c)`.

The frozen 11-predicate language is, in this order:

`a0,b0,c0,ab,ac,bc,am,bm0,cm,a_bm,c_bm`

where, e.g., `a0=[a=I]`, `ab=[a=b]`, `bm0=[b*m=I]`, `a_bm=[a=b*m]`.

The prospectively selected canonical signature is:

`S5=(b0,ab,ac,bm0,a_bm)`.

Exploratory expectation, now falsifiable: S5 determines exact branch delta for both `m=Z` and `m=X`; its induced branch quotient has 18 nonempty cells; and minimum determining cardinality inside the full frozen 11-predicate language is exactly 5.

No predicate may be added to V1 after outcome.

## Complete official domains

### Branch domain
For each `m in {Z,X}`, enumerate all 64 ordered `(a,b,c) in {I,X,Y,Z}^3`.

### Paired PP hidden-home domain
Enumerate all `4^6=4096` six-letter states, with branch-0 modifier Z and branch-1 modifier X, exactly matching QG-7d information closure.

## Gates

Positive state-quotient terminal requires all of:

1. primitive phase-free multiplication/F3 tables bind to the frozen compiler parent;
2. QG-7d parent control is reproduced: paired delta range exactly `[-4,+4]` with all nine integer values present on 4096 states;
3. S5 has zero mixed-delta cells for both modifiers;
4. S5 has exactly 18 nonempty cells for each modifier;
5. the signature-to-delta table is modifier-invariant under the literal structural signature;
6. exhaustive subset search over all 11 frozen predicates proves minimum determining cardinality exactly 5;
7. serialize all tied minimum-cardinality subsets;
8. every 4-predicate subset has a concrete mixed-delta counterexample;
9. paired S5 signatures determine total delta exactly on all 4096 states;
10. paired signature has exactly 324 realized cells and zero mixed-total-delta cells.

## Meaning of minimality

The minimality claim is **only within this frozen 11-predicate structural language**. It is not a universal information-theoretic lower bound over arbitrary encodings. The exact delta value itself forms a smaller 5-valued branch label, but that answer-encoding receives no explanatory-state minimality authority.

## Next theorem interface

A positive QG-22 result only repairs the information needed to **price J5**. A separate fresh protocol must combine the enriched hidden-home signature with the visible T4b pinned census and test a state-conditioned J5/fallback policy over the 32,556 PP failures. QG-22 cannot grant that all-n theorem.

## Dual harness

Generic ORION independently rebuilds Pauli multiplication, F3, feature truth values, complete domains, subset search, minimality witnesses, and paired composition without importing QG-22 analyzer helpers.

Native ORION-Q binds the QG-7d parent and keeps `STATE_QUOTIENT`, `J5_DELTA_DETERMINATION`, and `ALL_N_NORMALIZATION` separate; V1 must have `all_n_theorem_authority=false`.

## Honest terminals

- `QG22_HIDDEN_HOME_J5_DELTA_EXACTLY_DETERMINED_BY_MINIMAL_5_PREDICATE_STATE`
- `QG22_SELECTED_STATE_INSUFFICIENT__MIXED_DELTA_CELL_FOUND`
- `QG22_MINIMALITY_REFUTED__SMALLER_FROZEN_SIGNATURE_FOUND`
- `QG22_PARENT_BINDING_GAP`
- `QG22_GENERIC_NATIVE_DISAGREEMENT`
- `QG22_CANNOT_CHECK`

No novelty, R6, physical quantum advantage, or protected-subject authority follows.