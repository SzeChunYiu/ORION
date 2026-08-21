# QG-9 V6 — whole-system Tag-relocating support-1 normalization

Date: 2026-08-21
Issue: #807
Parent support theorem: PR #792 / `a80dbd57d9124f058de7465a13de8c69416c368b`
Parent V5 bounded-negative receipt: `49e21937f2bf28d8004b2eeb45a00da0d4efea30`
Branch: `shadow/orion-qg-qg9-v6-support1-normalization`
Status: **FROZEN BEFORE REPOSITORY THEOREM-CHECKER OUTCOME.**

Authority ceiling: frozen R6I all-n normal-form theorem attempt only. No novelty, R6 or physical-advantage authority.

## Target

Prove that every feasible frozen-R6I configuration whose four independent generators have support <=2 admits a feasible support<=1 replacement of no larger objective. With the protected parent `C_DP=C_cap2` this implies `C_DP=C_cap1` for every n.

## Construction and proof obligations

For each block choose an anticommuting local core `q_j` (`local_symp(r0,r1)=1`), which exists because the global symplectic product is one. Delete both generator letters at every other column and recompute the dependent third frame.

### L1 deletion credit

For any active non-core local column, all target letters and every central choice, zeroing both independent local generator letters has objective change:

- <= -4 for locally commuting active patterns;
- <= -7 for locally anticommuting patterns.

Reason: two active frame branches refund at least 6 while at most two Restore supports can worsen; a locally anticommuting column activates all three branches, refunds exactly 10 and at most three Restore supports worsen.

### L2 core alignment

Any ordered local anticommuting basis has all three frame letters nonidentity, so its weighted frame contribution is exactly 10 for every central choice. Replacing one ordered anticommuting basis by another changes frame cost by zero and can worsen at most three Restore letters. Exact bound: <= +3.

### L3 canonical shared Tag

For every ordered local anticommuting basis there are unique nonzero local Tag letters generating canonical labels `(c0,c1)=(1,2)`.

- common qubit + common basis -> Tag cost 4;
- distinct localization qubits -> place the corresponding dual letters at both qubits -> Tag cost 8.

Every feasible original configuration has both global Tag strings nonzero, hence original Tag cost >=4.

### L4 distinct cores

If `q_A != q_B`:

- when both blocks are already support1, feasibility with equal nonzero distinct labels forces each Tag string to be nonzero at both frame qubits, so original Tag cost >=8;
- otherwise at least one block deletes a non-core active column, earning >=4 credit; original Tag cost >=4, paying the new cost 8.

### L5 same core

If `q_A == q_B`:

- equal local ordered bases need no alignment and new Tag cost 4;
- different bases cannot occur when both blocks are already support1 under equal nonzero distinct shared labels;
- therefore at least one differing-basis block has a non-core active column: delete it for >=4 credit and align that block's core basis for <=3 cost. New Tag cost 4 <= original Tag cost.

No target, B permutation or central choice is changed by the construction.

## Frozen complete machine domains

1. **Deletion:** `(a,b)!=(I,I)` (15 local pairs) x 64 local target triples x 3 centrals = 2,880 rows. Classify local anticommutation and verify exact maxima `-4` commuting / `-7` anticommuting.
2. **Core alignment:** 6 old ordered anti bases x 6 new bases x 64 target triples x 3 centrals = 6,912 rows. Verify frame contribution invariant at 10 and max objective increase exactly `+3`.
3. **Canonical dual Tag:** all 6 ordered anti bases. Construct `(1,2)` labels and require both dual letters nonidentity.
4. **Same-qubit rigidity:** 6x6 ordered basis pairs x 16 local Tag-letter pairs = 576 rows. Every row with equal nonzero distinct labels must have identical ordered bases.
5. **Distinct-qubit Tag:** 6x6 ordered basis pairs x 16 two-qubit choices for S0 x 16 two-qubit choices for S1 = 9,216 rows. The checker must prove the exact minimum shared-Tag cost is 8 for every one of the 36 basis pairs.
6. **Feasible Tag lower bound:** enumerate all ordered distinct nonzero labels and verify each of the two Tag syndrome rows is nonzero; therefore each global Tag string must be nonzero and Tag cost >=4.
7. Bind parent support<=2 protected receipt/result and parent V5 bounded-negative receipt without using the negative panel as proof.

## Production-binding gates

Rebuild local multiplication/symplectic/weight independently from `p10.h` and require exact equality with R6I `_MUL/_SYMP/_LW`. All theorem arithmetic is integer/exact.

## Composition audit

Machine record must explicitly verify:

- extra active column credit floor `4` > core-alignment ceiling `3`;
- distinct-core non-support1 case: `old_tag_floor 4 + one_extra_credit 4 >= new_tag 8`;
- distinct-core both-support1 case: exact old Tag floor `8`;
- same-core case: `new_tag 4 <= old_tag_floor 4` and, when alignment is needed, `extra_credit 4 >= alignment 3`;
- support0 is infeasible for rank2 because `symp(0,0)=0`.

## Stress arm

After the exact lemmas are computed, generate deterministic feasible support<=2 configurations at n=2..6, arbitrary targets/centrals/permutations, apply the explicit normalization and recompute costs/acceptance. Stress cannot authorize the theorem; it can only refute it or corroborate the finite proof.

## Honest terminals

- `QG9_RANK2_ALL_N_SUPPORT1_SUFFICIENCY_MACHINE_CHECKED`
- `QG9_SUPPORT1_LOCAL_LEMMA_COUNTEREXAMPLE_FOUND`
- `QG9_SUPPORT1_COMPOSITION_GAP_FOUND`
- `QG9_SUPPORT1_PARENT_BINDING_GAP`
- `QG9_SUPPORT1_GENERIC_NATIVE_DISAGREEMENT`
- `QG9_SUPPORT1_CANNOT_CHECK`

If the positive terminal is earned, support0 is impossible, so the exact intrinsic support number is `kappa_R6I=1` under the frozen grammar/objective.
