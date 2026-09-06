# C7^3 multiwise Davenport frontier — frozen frame V1

Status: exploratory research frame; no novelty authority.
Branch: `shadow/davenport-c7-frontier-20260903`.
Base: `5d9c714dcd8f94d504ef58f56620678c552878bf`.

## Primary question

Determine whether

\[
D_3(C_7^3)=36.
\]

If equality holds, identify a structural mechanism strong enough to explain why every length-36 sequence over `C_7^3` contains three pairwise disjoint nonempty zero-sum subsequences. If equality fails, retain a smallest explicit obstruction and diagnose its mechanism.

## Frozen interpretation

- `C_7^3 = (Z/7Z)^3 = F_7^3`.
- `D_3(G)` is the least length forcing three pairwise disjoint nonempty zero-sum subsequences.
- Existing donor lower bounds, recurrence theorems, exact classical Davenport constants, eta/short-zero-sum thresholds, and prior exact multiwise values receive zero ORION novelty credit.
- The computation or host may propose evidence; it does not grant scientific or novelty authority.

## Required research atoms

1. **Donor frontier.** Saturate exact and alias searches for `D_3(C_7^3)`, multiwise/generalized Davenport constants of `C_p^3`, and rank-three zero-sum packing mechanisms.
2. **Lower-bound ownership.** Reconstruct the specialized Freeze–Schmid lower bound and strongest known exact inputs without relabeling donor structure.
3. **Counterexample semantics.** Derive necessary conditions on a hypothetical length-36 sequence with zero-sum packing number at most two.
4. **Spectrum geometry.** Test whether forbidden zero-sum-length spectra, plane occupancy, projective-line occupancy, multiplicity grammar, or another invariant separates `p=3` from `p>=5`.
5. **Exact bounded experiments.** Prefer exact/SAT/ILP/DP checks with symmetry normalization over unstructured enumeration. Every positive result needs an independent checker where practical.
6. **Hostile review.** Attempt to reduce every apparent new mechanism to a donor theorem, trivial consequence of `D_2`, or a stronger known invariant.
7. **Saturation challenge.** Do not stop on repeated search flatness; record which search universe, formulations, methods, obstruction classes, and verification routes were actually exercised.

## Success criteria

A successful research terminal is one of:

- a proof-level route to `D_3(C_7^3)=36` with all donor dependencies named and any computation independently checkable;
- an explicit verified length-36 counterexample, proving `D_3(C_7^3)>=37` and identifying the obstruction mechanism;
- a strictly stronger theorem/lemma that materially narrows the problem and survives hostile donor subtraction;
- a bounded `CANNOT_CHECK` packet that identifies the exact unsolved residual and next discriminating experiment.

## Claim ceiling

This frame grants no claim that the problem is open, that any derived corollary is novel, or that a finite experiment proves an all-instance statement outside its declared scope.
