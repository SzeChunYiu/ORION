# ORION-QG QG-37c — independent-replication closure of one-corruption robust geometry

Date: 2026-08-22
Parent: QG-37 issue #937 / draft PR #947
Replica lane: draft PR #948

## Status

**FROZEN AFTER THE QG-37 PRODUCTION RESULT AND BEFORE ANY QG-37b REPLICA OUTCOME IS READ.**

QG-37 production is preserved exactly as earned: `QG37_ROBUST_CLASS_CONDITIONED_UPPER_BOUND_ONLY`, with 89 of 92 class minima exact and three classes unresolved by the production time cap. QG-37c does not change that historical terminal. It defines the only allowed successor route by which a separately frozen independent exact replication may close the compiler-specific robust geometry.

Production result binding:
- QG-37 result digest: `12bf825a29710e5939642afe52f8645a70c120ca7461d6f61102853bc6eba566`;
- frozen QG-37 protocol blob: `c99f6ee73ab8e44e588a14ad0ab79b3fe426311c`;
- exact production classes: 89/92;
- production unresolved class indices: `[39,40,63]`;
- production upper bounds on those three classes: `[7,8,7]` respectively.

The numerical robust minima of those residual classes, the global robust worst case, and the exact robust-overhead distribution are **not predicted here**.

## 1. Immutable scientific target

The target is unchanged from QG-37:
- 715 local-Clifford orbit identities;
- 384 distinct physical indexed probes;
- 92 known joint bulk+spectrum summary classes;
- selected response code minimum Hamming distance at least three inside each class;
- physical probe identity and multiplicity preserved;
- `D3(S)` = minimum selected physical probes satisfying that distance-three condition.

## 2. Parent roles are non-substitutable

QG-37 production and QG-37b replication have different responsibilities.

### QG-37 production

May contribute:
- its 89 exact class minima and witnesses;
- its independently replayable distance-three witnesses / decoder certificates;
- upper bounds only for classes 39, 40, and 63.

It does **not** gain exact authority on those three classes retrospectively.

### QG-37b independent replication

May contribute exact `D3(S)` only if its separately frozen physical-coordinate pseudo-Boolean decision procedure:
- reconstructs the universe independently;
- preserves physical-probe multiplicity;
- proves all smaller cardinalities UNSAT before the first SAT cardinality or closes at the puncturing floor by theorem+witness;
- independently recomputes distance >=3 and radius-1 unique decoding;
- returns exact results on all 92 classes.

No production MILP LP bound, basis, branch tree, grouped-variable incumbent, or claimed optimality may serve as a QG-37b lower-bound proof.

## 3. Exact closure decision table

Let `P_i` be the QG-37 production record and `R_i` the QG-37b exact replica record for class `i`.

QG-37c may earn exact robust geometry iff **all** of the following hold:

1. Both parent result digests and protocol/binding hashes validate.
2. Both reconstruct the identical 715 / 384 / 92 universe and identical class ordering.
3. QG-37b is exact for all 92 classes.
4. For every one of the 89 production-exact classes, `P_i.minimum == R_i.minimum`.
5. For each production-unresolved class 39, 40, 63:
   - the QG-37b exact minimum is no larger than the QG-37 production certified upper bound;
   - the QG-37b selected witness independently has distance >=3;
   - no exactness is retroactively assigned to the original production record.
6. A third generic verifier, using generic QG-32 F2^2/F3 primitives rather than either optimizer, recomputes every parent witness and all 92 minima-vector consistency checks.
7. Native ORION-Q accepts only the scoped one-corruption structural identity authority.
8. Deterministic replay of QG-37b is byte-identical.
9. A self-consistent tamper of at least one replica class minimum/witness with recomputed result digest is rejected by the generic verifier for a semantic reason.
10. All stronger authority fields remain false.

If conditions 1-10 hold, terminal:

`QG37C_EXACT_ONE_CORRUPTION_ROBUST_GEOMETRY_CLOSED_BY_INDEPENDENT_REPLICATION`

If any exact production class disagrees with the replica, terminal:

`QG37C_PRODUCTION_REPLICA_EXACT_CLASS_DISAGREEMENT`

If a residual replica minimum exceeds the production certified upper bound, terminal:

`QG37C_PRODUCTION_UPPER_BOUND_CONTRADICTION`

Any timeout, unknown, missing parent, malformed receipt, verifier disagreement, replay drift, or failed tamper demonstration:

`QG37C_CANNOT_CHECK`

## 4. Robustness-overhead composition

QG-35 already independently earned the exact noiseless class-conditioned minima `D1(S)=F(S)` on the same 92 classes. Only after QG-37c exact closure may this lane compute the compiler-specific structural robustness overhead

`H(S) = D3(S) - D1(S)`.

It may then report exactly:
- the 92-entry overhead vector;
- overhead histogram;
- maximum overhead;
- robust worst-case `R1_star=max_S D3(S)`;
- which classes attain the robust worst case;
- which classes lie strictly above the general puncturing floor `D1(S)+2`.

This is an observation/evidence-reliability cost inside the frozen compiler response model. It is **not** a hardware-noise rate, fault-tolerance threshold, physical measurement count, or physical resource advantage.

## 5. Universal robust code remains separate

QG-37c does not infer the minimum universal fixed distance-three probe set. `R1_universal` remains a separate exact optimization and has no authority here unless separately frozen and solved.

## 6. Hard-false authority

Always false:
- hardware measurement-noise model;
- stochastic physical error rate;
- quantum fault-tolerance threshold;
- hardware measurement minimum;
- full finite-n compiler optimum probe minimum;
- generic coding / PB-SAT / separating-system novelty;
- runtime superiority;
- physical quantum advantage;
- external novelty authority.

## 7. Frontier-harness rule

The frontier harness is the promotion boundary. A QG-37b solver success by itself is not QG-37c authority. Promotion requires the frozen composition, third generic verifier, native gate, deterministic replay, semantic tamper rejection, and hard-false checks above.

No failed parent is rewritten to green. QG-37 remains an honest upper-bound production record even if QG-37c later closes the scientific quantity by independent replication.
