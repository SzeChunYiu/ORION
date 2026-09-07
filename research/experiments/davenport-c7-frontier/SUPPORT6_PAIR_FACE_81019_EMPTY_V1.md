# C7 first-corridor pair support-six face is empty — V1

Status: **complete bounded pair-level elimination with two independent exact implementations**. This is stronger than the earlier full-triple support-four closure, but it is still a `p=7` theorem only.

## Statement

Let `U` be a support-four maximal atom of length 19 over `C_7^3`, and let `V` be a length-10 atom such that `UV` is 9-short-zero-free. Then

`boxed{|supp(UV)|>=7.}`

Equivalently, the exact support-six equality face from `SUPPORT4_MAXIMAL_PAIR_SUPPORT6_NORMAL_FORM_V1.md` is empty in the `(19,10)` pair.

## Exhaustive cover

By `SUPPORT4_MAXIMAL_ATOM_WEIGHTS_V1.md`, up to automorphism the length-19 atom is one of the three canonical types `a=1,2,3`.

The already frozen stage-one `(19,10)` search gives exactly

- `a=1`: 538 compatible length-10 companions;
- `a=2`: 24;
- `a=3`: 0.

The new classifier replays this complete universe and then records the union support of each pair. The support-six counts are

`boxed{0,0,0.}`

Thus none of the 562 compatible pair factorizations reaches the support-six lower bound.

## Independent implementations

`search_support6_pair_face_81019_v1.py` uses Python sets and cardinality-indexed incremental companion subset sums. It first asserts the frozen `538,24,0` pair totals and then asserts that the support-six face is empty.

`verify_support6_pair_face_81019_independent_v1.cpp` uses the earlier C++ bitset state representation and an independently coded support/rank classifier. It reproduces the same totals and the same empty face.

Both implementations are pair-level: the length-8 third atom is never introduced.

## Consequence for the old closure

`SUPPORT4_81019_CLOSURE_V1.md` proved that every full `(8,10,19)` triple with support-four 19-atom four-packs. The present result is structurally earlier and stronger in a different direction:

> before the length-8 atom is considered, every compatible `19+10` pair already uses at least seven actual support values.

This removes the entire support-six normal-form face from the C7 first corridor and leaves only pair support at least seven.

## Generalization signal and small-prime boundary

A separate equality-face depth-oracle control finds the same empty support-six face for the first corridor at primes `p=11,13,17` (all support-four types), while `p=5` has genuine support-six pair examples in the `a=2` light-share rank-two branch. Therefore the natural next theorem target is

`p>=7, j=1, support-four maximal atom => |supp(UV)|>=7`,

not an all-prime statement starting at `p=5`.

The `p=11,13,17` observations are discovery controls only and are not promoted here as theorem authority.

## Boundary

- This file proves only the `p=7`, `(19,10)` pair statement.
- It does not eliminate pair support `>=7`.
- It does not cover the `(19,9)` second corridor.
- The proposed `p>=7` generalization remains to be proved analytically.
- No `D_3(C_7^3)` value is claimed.
