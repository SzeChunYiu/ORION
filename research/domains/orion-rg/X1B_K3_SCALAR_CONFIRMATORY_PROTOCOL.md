# X1-B k=3 scalar residual — independent confirmation protocol

Parent: #900
Exploratory predecessor: `research/domains/orion-rg/x1b_k3_scalar_residual_exploratory.py` at commit `8aadb63d8c4f48581710060a3af0ae2d6ed572a0`.

## Evidence status

**FROZEN CONFIRMATORY PROTOCOL.** The exploratory aggregate result was already observed before this packet was written. Therefore this confirmation may establish independent reconstruction of that finite statement, but it is not prospective discovery evidence.

No theorem, novelty, C15, or infinite-family authority is granted by this protocol alone.

## Frozen claim to confirm

Let `A` be a 10-term multiset over `F_3^3` satisfying:

1. no nonempty zero-sum subsequence of length at most 3;
2. no two disjoint nonempty zero-sum subsequences.

For every such `A`, test whether there is a position-labelled map `f:A -> F_5` satisfying

`sum_{a in B} f(a) = 1`

for every nonempty zero-sum subsequence `B <= A`.

The exploratory implementation reports that no such `f` exists for any admissible orbit.

## Independence requirements

The confirmatory implementation MUST NOT import or call the exploratory implementation and MUST NOT use its two-stage algorithm

`support GL-orbits -> support stabilizer -> doubled-position orbits`.

Instead it must use a separately written **canonical augmentation of full multiplicity vectors**:

- state is a 26-entry multiplicity vector over nonzero `F_3^3` elements;
- multiplicities are restricted to `{0,1,2}` by the length<=3 zero-sum gate;
- total multiplicity is exactly 10;
- partial states are pruned directly by primitive zero-sum conditions;
- completed candidates are canonicalized under the full `GL(3,3)` action on multiplicity vectors, without using support stabilizers;
- every canonical survivor is replayed from its explicit 10 positions.

This is algorithmically distinct enough to catch support/stabilizer quotient mistakes, orbit omission, or doubled-set canonicalization errors in the exploratory path.

## Primitive verifier requirements

For every canonical candidate:

1. enumerate every nonempty position subset and compute its sum directly in `F_3^3`;
2. reject if any zero-sum subset has size <=3;
3. reject if two zero-sum subset masks are disjoint;
4. build the affine system over `F_5` with one equation per nonempty zero-sum mask and common RHS 1;
5. independently row-reduce the augmented matrix over `F_5` and classify consistency;
6. serialize a canonical witness digest for each surviving orbit so the orbit census can be replayed.

## Frozen comparison coordinates

The confirmatory result records, but does not hard-code as success criteria:

- `GL(3,3)` size;
- number of canonical 10-multiset candidates after the no-short-zero-sum gate;
- number surviving the no-two-disjoint-zero-sums gate;
- support-size histogram of survivors;
- number with a consistent common-RHS affine system;
- multiset of equation ranks;
- SHA-256 digest of sorted canonical survivor encodings.

The primary confirmation criterion is only:

`consistent_common_rhs_orbit_count == 0`

plus complete primitive replay of all canonical survivors.

## Failure interpretation

- Any consistent survivor is a **counterexample** to the exploratory finite claim and must be committed in full.
- Any census mismatch with the exploratory script is a first-class disagreement even if both find zero consistent systems.
- Resource exhaustion is `CANNOT_CHECK_RESOURCE_BOUND`, not confirmation.
- Agreement grants only `FINITE_CONFIRMATORY_RECONSTRUCTION`; it cannot self-promote to the all-sequence C15 theorem.

## Downstream gate

Only after an independent implementation satisfies this packet may X1-B use the k=3 residual as closed finite evidence. The k=4 / 13-point residual remains independently open and cannot be inferred from k=3 closure.
