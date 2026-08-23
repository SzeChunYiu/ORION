# ORION-QG QG-30 — exact 45-bin bulk coarse-graining and bulk/defect scale separation V1

Date: 2026-08-22
Issue: #893
Parent programme: #740
Execution branch: `codex/orion-qg-qg30-bulk-coarse-grain-20260822`
Direct parents:
- QG-27 protected four-form bulk/asymptotic theorem
- QG-28 protected 715 local-Clifford orbit histogram theorem
Related control: QG-29 protected finite-size defect-saturation theorem
Status: **FROZEN BEFORE QG-30 MACHINE OUTCOME.**
Authority: exact compiler bulk coarse-graining only; no physical RG/universality, full-defect sufficiency, finite-n optimum from 45 counts, chain/B'' completeness, novelty, R6 or physical-advantage authority.

## Scientific question

QG-28 gives 715 exact local-Clifford target-column orbit counts as a sufficient statistic for the full finite-size optimizer. QG-27 shows the extensive/asymptotic term is only the lower envelope of four distinct spectator baseline forms.

For each 715-orbit `o`, define its ordered **bulk signature**

`s(o)=(b_0(o),b_1(o),b_2(o),b_3(o))`.

Does the thermodynamic/bulk compiler geometry admit a much coarser exact sufficient statistic, while the bounded finite-size defect term demonstrably retains finer information?

## P1 — exact 45-signature census

Rebuild the 715 QG-28 orbits and the canonical four QG-27/QG-28 baseline vectors independently. Group orbit representatives by the ordered four-tuple `s(o)`.

Frozen expected number of distinct signatures: **45**.

Serialize the complete 45-row signature table. Each row contains:
- signature tuple;
- number of 715-orbits in the signature;
- total number of original 4096 column types represented by those orbits;
- lexicographically first orbit representative;
- SHA256 of the sorted member-orbit representative list.

Required totals:
- signature orbit multiplicities sum to 715;
- raw column multiplicities sum to 4096.

No post-outcome merging of the 45 signatures is permitted in V1.

## P2 — exact 45-count bulk sufficient statistic

Let `H_s` be the number of physical target columns whose local-Clifford orbit has signature s. Then for each bulk form r,

`B_r(N)=sum_s H_s*s_r`.

Therefore:
- QG-27 exact asymptotic density `e(p)=min_r beta_r(p)` depends only on normalized 45-signature frequencies;
- every pure-scaling-ray slope `B_min(h)` depends only on the 45 signature counts;
- all six pairwise bulk tie forms descend exactly to `Z^45`.

Thus 45 bins are an exact sufficient statistic for the extensive/asymptotic bulk geometry.

## P3 — complete one-active finite-defect profile census

Use the same frozen one-active language as QG-26/QG-28:
- all 715 canonical local-Clifford orbit representatives;
- all 48 feasible one-coordinate shared-label frame/Tag rows;
- all 8 target-permutation tuples;
- canonical central tuple `(0,0,0)`.

For one orbit representative o, define its canonical **one-active defect profile** as the sorted multiset of the 384 integers

`K = structural + F3_aux - spectator_baseline`.

Serialize only profile SHA256 + value histogram by default; full profile vectors are not needed except for a counterexample.

Group profiles by bulk signature and report:
- distinct defect-profile count in each of the 45 signature classes;
- total distinct one-active profiles across all 715 orbits;
- number of signatures containing >1 defect profile.

These are outcome values, not frozen expectations.

## P4 — mandatory information-loss witness

Search the complete census in lexicographic `(signature,rep1,rep2)` order for two local-Clifford orbit representatives with:
- identical 4-form bulk signature;
- different one-active defect profiles.

If found, serialize verbatim:
- both representatives;
- common signature;
- each profile SHA256 and exact K-value histogram;
- first index in the canonical 384-entry ordered profile at which they differ, including permutation tuple and auxiliary row.

This earns

`BULK_SIGNATURE_SUFFICIENT_FOR_FULL_DEFECT = false`.

If the complete 715-orbit census contains no such pair, return the honest terminal `QG30_NO_ONE_ACTIVE_DEFECT_INFORMATION_LOSS_FOUND__SUCCESSOR_REQUIRED`. Do **not** promote full finite-size sufficiency in V1; a one-active profile is not itself proven to be a complete defect invariant.

## P5 — bulk/defect scale separation theorem

If P1/P2 are exact and P4 finds an information-loss witness, QG-30 may state:

> The exact extensive/asymptotic TARE geometry coarse-grains from 715 finite-size orbit bins to 45 bulk-signature bins, but that coarse-graining provably loses bounded finite-defect information.

This is an exact compiler-specific bulk/defect scale separation.

It is not a physical renormalization-group flow and does not claim universal critical exponents or physical universality classes.

## P6 — 45-dimensional bulk phase geometry

For each of the four bulk forms, serialize its exact coefficient row in `Z^45`. For all six pairs serialize the tie/difference row, support size, coefficient range and SHA256.

The normalized 45-frequency simplex has exact asymptotic compiler cells under the lower envelope of these four forms.

No finite-n global phase-boundary authority.

## P7 — local controls / parent binding

Bind QG-28:
- 715 orbit census and member partition of 4096;
- local-Clifford equivariance;
- 4 distinct quotient baseline vectors;
- unsafe 54-bin position quotient remains false.

Bind QG-27:
- four exact bulk forms;
- asymptotic density authority;
- finite defect term is O(1) / bounded.

Bind QG-29 only as a control:
- clip6 defect saturation / k43 theorem may be mentioned after QG-30, but QG-30 authority must not depend on it.

## Independent generic ORION

Must independently rebuild phase-free Pauli/F3 algebra, S3 local-Clifford orbits, four baseline forms, 45 signatures, complete 715×384 one-active profile census, first information-loss witness, and 45-dimensional pairwise bulk tie forms before binding parent hashes.

## Native ORION-Q

May authorize:
- `BULK_SIGNATURE_COUNT_45`
- `BULK_45_HISTOGRAM_SUFFICIENT_FOR_ASYMPTOTIC_DENSITY`
- `ASYMPTOTIC_PHASE_GEOMETRY_DESCENDS_TO_45_COUNTS`
- `BULK_DEFECT_SCALE_SEPARATION` if P4 finds a witness.

Mandatory false:
- `BULK_SIGNATURE_SUFFICIENT_FOR_FULL_DEFECT`
- `FULL_FINITE_N_OPTIMUM_FROM_45_COUNTS`
- `PHYSICAL_RENORMALIZATION_GROUP`
- `FINITE_N_GLOBAL_PHASE_BOUNDARY`
- `CHAIN_ALL_N`
- `CLOSED_FORM_BDOUBLEPRIME_COMPLETENESS`
- novelty/R6/physical-advantage authority.

## Intended strong terminal

`QG30_TARE_BULK_GEOMETRY_COMPRESSES_EXACTLY_TO_45_SIGNATURE_COUNTS__DEFECT_INFORMATION_REMAINS`

Honest alternatives:
- `QG30_SIGNATURE_COUNT_MISMATCH`
- `QG30_BULK_BASELINE_NOT_CONSTANT_ON_SIGNATURE`
- `QG30_NO_ONE_ACTIVE_DEFECT_INFORMATION_LOSS_FOUND__SUCCESSOR_REQUIRED`
- `QG30_QG28_PARENT_BINDING_GAP`
- `QG30_GENERIC_NATIVE_DISAGREEMENT`
- `QG30_CANNOT_CHECK`

## Donor subtraction

Coarse-graining, sufficient statistics, invariant partitions and bulk/defect decompositions are established donor ideas. Candidate contribution is only the exact TARE-specific 715→45 bulk compression and demonstrated separation between extensive bulk information and bounded compiler-defect information.
