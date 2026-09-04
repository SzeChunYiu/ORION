# First-corridor exact-support-six equality-face sweep — V1

Status: **bounded exact discovery/control sweep**. This is not a prime-uniform theorem. It exhausts only the support-six equality face already proved for a support-four maximal atom in the first maximal corridor.

## 1. Target face

Let `p>=5` be prime and let

`U=e1^(p-1)e2^(p-1)e3^a g4^(p-a)`,

`g4=e3-a^{-1}(e1+e2)`,

be a support-four maximal atom. In the first prime-uniform maximal corridor

`C_1(p)=(p+1, (3p-1)/2, 3p-2)`,

let `V` be the longer companion, so

`|V|=(3p-1)/2`.

The branch has already proved that `|supp(UV)|>=6`. Assume equality.

`SUPPORT4_MAXIMAL_PAIR_SUPPORT6_NORMAL_FORM_V1.md` reduces the equality face to exactly two branches:

1. **support-three planar branch:** `V` shares exactly one of the two unsaturated values `e3,g4`, has exactly two new actual support values, and its rank-two plane meets `supp(U)` in precisely that one shared point;
2. **support-four rank-three branch:** `V` shares both unsaturated values, has exactly two new actual support values, and spans `C_p^3`.

No other support-six geometry is enumerated here.

## 2. Exact predicate

For every candidate, the sweep uses only already-proved exact constraints:

- pair multiplicity capacity `v_x(UV)<=p-1`;
- the one-dimensional kernel criterion for a three- or four-support atom;
- the exact support-six plane-intersection normal form;
- the closed support-four representation-depth oracle `rho_U`;
- the graded pair criterion

`|W|+rho_U(-sigma(W))>=|V|`

for every nonempty proper `W|V`.

For fixed support multiplicities, the final new support point is forced by the zero-sum equation, so the sweep never enumerates arbitrary pairs of new values.

The rank-three branch similarly chooses one new point outside the plane of the two shared values and solves uniquely for the second.

This is therefore an exact equality-face census, not a whole-group search.

## 3. Frozen result

`search_support4_first_corridor_support6_face_v1.cpp` gives:

### p=5

| support-four type `a` | support-three survivors | support-four survivors |
|---:|---:|---:|
| 1 | 0 | 0 |
| 2 | 4 | 0 |

Thus `p=5` is a genuine counter-boundary to any unqualified all-prime support-seven statement. Exact support-six compatibility occurs in the planar branch.

This is retained as a mutation/control: a checker that accidentally rejects every equality face would fail here.

### p>=7 bounded rows

For every support-four maximal-atom type at each prime

`p in {7,11,13,17,19,23,29}`,

the exact result is

`support-three survivors = 0`,

`support-four survivors = 0`.

Equivalently, on every tested prime `p>=7`, a first-corridor maximal pair with a support-four maximal atom satisfies

`|supp(UV)|>=7`.

This last sentence is a **bounded computational statement on the listed primes only**.

## 4. Relation to the old C7 closure

At `p=7`, the first corridor is `(8,10,19)`.

The old full support-four pair enumeration gave 538, 24 and 0 compatible length-10 companions for the three canonical maximal-atom types before the 8-atom completion was added. The present sweep searches only the exact-support-six equality face and returns zero in all three types.

Thus the new bounded result is consistent with, but structurally different from, the earlier full C7 enumeration: it explains that every compatible C7 maximal pair already has support at least seven before the third atom is introduced.

## 5. Discovery implication

The data now separates the small-prime boundary sharply:

- `p=5`: support six is genuinely realizable in the exact equality face;
- `p=7,11,13,17,19,23,29`: the entire equality face is empty.

This registers the next theorem target:

> **Target, not yet proved.** For every prime `p>=7`, if the first maximal corridor contains a support-four maximal atom `U`, then its maximal pair `UV` has support at least seven.

The finite sweep is evidence and a theorem-discovery control only. It does not authorize the universal quantifier.

## 6. Next analytic split

The rejection statistics from the discovery run show that surviving structural candidates are always killed by a very small proper companion subsequence. This points to a low-cardinality depth-shell theorem rather than a larger census.

The planar branch is especially rigid. If the companion shares the heavy maximal-atom value, its rank-two plane receives at least `(p+1)/2` extra copies from `U`; numerical arithmetic checks suggest a prime-uniform half-extension lemma should force a short zero-sum in that plane. That lemma is not promoted here because its final residue argument is still open.

The middle-inverse rank-three branch remains the second analytic target and should be attacked using simultaneous quotient atomicity plus the graded depth shells.

## Verification receipt

The frozen program was compiled with `g++ -O3 -std=c++17` and, on the committed bounded prime set, returns

`SUPPORT4_FIRST_CORRIDOR_SUPPORT6_FACE_SWEEP_GREEN`.

A local replay of the exact committed source completed the full frozen set and reproduced the asserted p=5 mutation/control and the seven zero-prime rows.

## Boundary

- No result for `p=31` or larger is claimed by this sweep.
- The sweep assumes the maximal atom has support exactly four.
- It treats only the first maximal corridor `j=1`.
- It does not determine `D_3(C_p^3)`.
- The proposed support-seven statement remains a target until an analytic proof is committed.
