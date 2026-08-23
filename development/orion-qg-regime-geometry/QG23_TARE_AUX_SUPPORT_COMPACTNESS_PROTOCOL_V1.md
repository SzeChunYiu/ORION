# ORION-QG QG-23 — six-coordinate auxiliary-support compactness protocol V1

Date: 2026-08-22
Parent programme: #740
Issue: #879
Structural parent: `research/extensions/orion-qg/QG7C_CLASSIFICATION_RESULTS.json`
Hostile correction parent: QG-7f F0 / PR #878 / `research/extensions/orion-qg/QG7F_CHAIN_REPRESENTATION_AUDIT_RESULTS.json`
Status: **FROZEN BEFORE QG-23 MACHINE OUTCOME.**
Authority: compiler-structure theorem only; no novelty, R6, full-state-dimension, chain-closure, B''-completeness, or physical-advantage authority.

## Scientific question

QG-7f refuted the proposed common-two-coordinate chain picture. Is there nevertheless an all-n, n-independent bound on the coordinates needed by the **auxiliary** TARE objects (frames, shared Tag, and phantom homes) after the already-earned QG-7c reductions?

Let the three irreducible block types be:
- `A`: anchored;
- `P`: phantom;
- `C`: comm-s2.

Write their counts as `(a,p,c)` with `a+p+c=3`.

## Frozen theorem candidate

QG-7c must bind the following earned structural facts:

1. M1 irreducible shapes are exactly A/P/C.
2. After T1, T2 gives `wt(S) <= 3 + c`.
3. Every irreducible phantom has one home coordinate with no Tag letter; hence there are at most `p` off-Tag phantom-home coordinates.
4. Anchored and comm-s2 blocks have no additional off-Tag home coordinate in the irreducible grammar.

Define

`U_aux = supp(S) union {phantom home coordinates}`.

Then

`|U_aux| <= wt(S)+p <= 3+c+p = 6-a <= 6`.

The positive theorem is therefore:

> Every irreducible three-block TARE auxiliary configuration produced after the earned QG-7c reductions has an auxiliary-support skeleton of cardinality at most six, independently of physical qubit count n.

The bound is an existence/representation statement about the auxiliary objects only.

## Mandatory scope barrier

This protocol does **not** assert that the full compiler state or the six target Paulis live on six qubits. Spectator target coordinates outside `U_aux` may carry nontrivial Pauli letters and may affect F3 / target-permutation costs. QG-7d and QG-22 are explicit controls showing omitted environment information can be load-bearing.

The following must remain false in every QG-23 output:
- `FULL_STATE_DIMENSION_6`
- `CHAIN_ALL_N`
- `GLOBAL_BDOUBLEPRIME_COMPLETENESS`
- `FIFTH_REGIME_FOUND`

## P1 — exact QG-7c parent binding

Read the committed QG-7c result and require:
- `m1_inventory.holds == true`;
- irreducible shape counts contain exactly `anchored`, `phantom`, `comm_s2` as positive classes and no fourth irreducible class;
- `t2_occupancy.holds == true`;
- `t2_occupancy.occupancy_failures_from_m1 == 0`;
- per-shape anticommuting Tag-qubit counts are anchored=1, phantom=1, comm_s2=2;
- the T2 corollary text explicitly contains the all-n bound `wt(s) <= 3 + #comm-s2`;
- M1/L4b text records that every irreducible borrow qubit carries a Tag letter and every phantom home carries none, and that cyclic borrowing is structurally impossible.

If any parent field is absent or weaker than the stated premise, return `QG23_PARENT_OCCUPANCY_AUTHORITY_GAP` rather than reconstructing authority from memory/prose.

## P2 — hostile QG-7f binding

Bind the committed QG-7f F0 result and require:
- terminal `QG7F_TWO_COORD_REDUCTION_REFUTED__TAG3_MULTI_COMM_S2_CONFIGURATION`;
- both harnesses accepted;
- Tag weight 3;
- B/C support pairs `[0,1]` and `[1,2]` differ;
- `CHAIN_REPRESENTATION_COMPLETE == false`.

This is a mandatory anti-regression control: QG-23 may never simplify the six-coordinate theorem into a common-two-coordinate theorem.

## P3 — complete shape-count lattice

Enumerate all nonnegative triples `(a,p,c)` with `a+p+c=3`. There must be exactly 10.

For each row serialize:
- `tag_support_bound = 3+c`;
- `phantom_off_tag_home_bound = p`;
- `aux_support_bound = 3+c+p = 6-a`.

The maximum over the complete lattice must be exactly 6. The rows attaining 6 are exactly those with `a=0`.

No stronger global bound may be promoted from this finite count lattice.

## P4 — proof audit

The analyzer and verifiers must explicitly check:
- physical n does not occur in the derived bound;
- overlapping comm-s2 support pairs are allowed;
- the proof counts phantom homes only once per phantom, as a worst-case union bound (coincident homes may reduce actual support but cannot increase it);
- target spectator state remains OPEN;
- no optimization-family completeness follows from auxiliary compactness alone.

## Independent generic ORION

Generic ORION reads the two parent receipts but derives the 10 shape-count triples and inequalities independently. It must not import the production QG-23 analyzer and must reject any output that asserts common-two-coordinate support or full-state dimension six.

## Native ORION-Q

May accept only responsibility `AUXILIARY_SUPPORT_COMPACTNESS` when:
- the QG-7c structural premises bind exactly;
- the QG-7f hostile correction binds exactly;
- production and generic lattice/proof audit agree;
- all stronger authority coordinates remain false.

## Intended positive terminal

`QG23_TARE_AUXILIARY_SUPPORT_SKELETON_AT_MOST_6_ALL_N_MACHINE_CHECKED`

Honest alternatives:
- `QG23_PARENT_OCCUPANCY_AUTHORITY_GAP`
- `QG23_PHANTOM_HOME_COUNT_GAP`
- `QG23_HOSTILE_CORRECTION_BINDING_GAP`
- `QG23_GENERIC_NATIVE_DISAGREEMENT`
- `QG23_CANNOT_CHECK`

## Donor subtraction

Incidence counting, hypergraph support unions, matroid/rank-style compactness arguments and finite combinatorial enumeration are established methods and receive zero novelty credit. Candidate contribution is only the exact compiler-specific all-n auxiliary-support theorem and its downstream consequences.
