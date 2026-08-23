# X1-B theorem bridge — one symmetric bilinear form governs every residual two-block extension

Parent: #900. Committed before downstream use.

## Status

**DONOR-DERIVED GLOBAL PACKING COUPLING.**

This theorem is an exact consequence of the committed group-algebra cofactor formulation. It upgrades deletion-local scalarization to a single object shared by **all** residual two-block packings built over the same ten previously removed quotient triples.

The group-algebra/top-coefficient machinery is donor-derived. The C15-specific use of the resulting common bilinear form is the live theorem interface.

## Fixed ten-block kernel state

In the surviving k=4 branch of a hypothetical C15 counterexample, ten disjoint quotient-zero-sum triples have already been removed. Let their lifted sums in the kernel `C_5^3` be

`t_1,...,t_10`.

These ten vectors are fixed while the two residual quotient-zero-sum blocks vary.

Choose a kernel basis and write

`t_j=(a_{j1},a_{j2},a_{j3})`.

Let

`L_{t_j}=a_{j1}u1+a_{j2}u2+a_{j3}u3`

and define the degree-10 polynomial

`R_T(u)=prod_{j=1}^{10} L_{t_j}`.

## Symmetric extension matrix

For `r,s in {1,2,3}`, define

`M_T[r,s] = [u1^4 u2^4 u3^4] (u_r u_s R_T)`.

Equivalently:

- if `r=s=1`, this is `[u1^2 u2^4 u3^4]R_T`;
- if `r=1,s=2`, this is `[u1^3 u2^3 u3^4]R_T`;
- and analogously for the remaining entries.

Because multiplication is commutative,

`M_T[r,s]=M_T[s,r]`.

Thus `M_T` is a symmetric `3x3` matrix over `F_5`.

## Two-extension coefficient identity

Let `x,y in C_5^3` and write

`L_x=sum_r x_r u_r`,

`L_y=sum_s y_s u_s`.

Then

`[u1^4u2^4u3^4] R_T L_x L_y`

is exactly

`x^T M_T y`.

Now suppose the twelve-term sequence

`H = t_1...t_10 x y`

is zero-sum free. It has maximal length `d(C_5^3)=12`. By the group-algebra identity already established in the cofactor packet,

`Pi(H)=Omega=u1^4u2^4u3^4`.

Hence its top coefficient is 1, and therefore

> **`x^T M_T y = 1`.**

## Apply to every residual packing

Let A be the 13-position k=4 quotient residual, with individual kernel coordinates `y_j in C_5^3` for its original positions.

For every nonempty quotient-zero-sum subset `Z <= A`, define its lifted block sum

`z_Z = sum_{j in Z} y_j`.

If `Z` and `W` are disjoint nonempty quotient-zero-sum subsets, then the twelve quotient blocks

`10 fixed triples + Z + W`

are pairwise disjoint. In a hypothetical globally zero-sum-free C15 sequence, their twelve lifted block sums must themselves form a zero-sum-free sequence in `C_5^3`; otherwise a zero-sum subcollection of block sums lifts to a zero-sum subsequence of the original sequence.

Therefore **every edge** `(Z,W)` in the disjoint-zero-sum graph of A satisfies

`z_Z^T M_T z_W = 1`,

with the **same symmetric matrix `M_T` for all edges**.

This is the first global coupling that survives the earlier proof-method counterexamples:

- one local deletion functional was too weak;
- two local deletion cofactors for one selected packing were too weak;
- but the fixed ten-block state forces all possible residual packings to share one bilinear extension form.

## Relaxed necessary condition

For quotient-side falsification it is enough initially to forget whether a proposed symmetric matrix M is actually realizable as `M_T` for ten zero-sum-free-compatible block sums.

Thus every genuine C15 counterexample must at minimum admit vectors `y_1,...,y_13 in F_5^3` and **some symmetric** `M in Mat_3(F_5)` such that

`(sum_Z y_j)^T M (sum_W y_j)=1`

for every disjoint quotient-zero-sum pair `(Z,W)` in A.

If even this relaxed system is infeasible for one of the six quotient obstruction orbits, that orbit is eliminated a fortiori.

If it is feasible, the witness defines the next obstruction state; later gates can restore:

1. realizability of M as a ten-factor catalecticant `M_T`;
2. zero-sum-freeness of the ten fixed block sums;
3. individual-term/global lift constraints.

## Mathematical form

Since

`z_Z=sum_j 1_Z(j)y_j`,

the edge equation is quadratic in the original residual kernel variables and linear in the six independent entries of M.

Equivalently, putting `B_{jk}=y_j^T M y_k`, each edge imposes

`sum_{j in Z, k in W} B_{jk}=1`,

where the `13x13` matrix B must factor through a symmetric bilinear form on a 3-dimensional space and hence has rank at most 3.

This rank formulation may allow an independent finite-algebra verifier.

## Next frozen discriminator

Test the six committed k=4 quotient obstruction orbits against the relaxed system:

`exists y_1,...,y_13 in F_5^3, symmetric M : every disjoint zero-sum edge has bilinear value 1`.

Strong positive for the C15 proof programme:

`NO` for all six orbits.

Honest negative:

serialize any feasible orbit with a full `(y,M)` witness and reframe to catalecticant realizability / global original-index constraints.

## Claim boundary

This packet does not assert that every symmetric M is realizable by ten kernel block sums. It states only a necessary condition for an actual counterexample and deliberately begins with a relaxed superset to obtain a cheap, fail-closed discriminator.
