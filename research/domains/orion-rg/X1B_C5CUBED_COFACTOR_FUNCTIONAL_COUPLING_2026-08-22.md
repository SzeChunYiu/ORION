# X1-B theorem bridge — deletion functionals are cofactors of one common kernel polynomial

Parent: #900. Committed before downstream use.

## Status

**DONOR-DERIVED CROSS-DELETION COUPLING.**

This packet extracts a consequence already implicit in the Geroldinger--Yang p-group group-algebra proof. The group-algebra machinery and the resulting `nu_p` theorem are donor mathematics. The useful increment here is the explicit form needed by the C15 block-lift interface.

## Group-algebra coordinates

Let

`G=C_5^3=<e1> direct-sum <e2> direct-sum <e3>`

and work in `F_5[G]`. Put

`z_r = 1-X^{e_r}` for `r=1,2,3`.

Then

`F_5[G] ≅ F_5[z1,z2,z3]/(z1^5,z2^5,z3^5)`

and the group-algebra socle element is

`Omega = sum_{g in G} X^g = z1^4 z2^4 z3^4`.

Let

`H=h_1 ... h_12`

be a maximal zero-sum-free sequence in `G`. Since `d(G)=12`, Geroldinger--Yang Lemma 3.4 gives

`Pi(H)=c Omega`.

Because H is zero-sum free, the coefficient of `X^0` in `Pi(H)` is contributed only by the empty subsequence and equals 1; the coefficient of `X^0` in `Omega` is also 1. Hence

`Pi(H)=Omega`.

Write

`h_j=(a_{j1},a_{j2},a_{j3}) in F_5^3`.

The degree-one term of `1-X^{h_j}` in the z-coordinates is

`L_j = a_{j1} z1 + a_{j2} z2 + a_{j3} z3`.

Since every factor has zero constant term, the degree-12 part of `Pi(H)` is exactly

`P_H(z)=prod_{j=1}^{12} L_j`.

In the truncated algebra, every degree-12 monomial vanishes unless every exponent is at most 4; because the total degree is 12, the only surviving degree-12 monomial is `z1^4 z2^4 z3^4`. Thus

`[z1^4 z2^4 z3^4] P_H = 1`.

Define the common multilinear top-coefficient polynomial

`F(h_1,...,h_12) = [z1^4 z2^4 z3^4] prod_j L_j`.

For every maximal zero-sum-free H under the above basis,

`F(H)=1`.

## Deletion cofactor formula

Fix i and let

`T_i = H h_i^{-1}`,

`Q_i(z)=prod_{j != i} L_j`.

Geroldinger--Yang's proof constructs the canonical homomorphism `lambda_i^can:G->F_5` characterized by

`(1-X^y) Pi(T_i) = lambda_i^can(y) Omega`.

Only the linear term

`L_y = y_1 z1 + y_2 z2 + y_3 z3`

of `1-X^y` can contribute to the degree-12 socle when multiplied by the degree-11 leading term `Q_i`. Therefore

`lambda_i^can(y) = [z1^4 z2^4 z3^4] L_y Q_i`.

Equivalently, define

`q_i1 = [z1^3 z2^4 z3^4] Q_i`,

`q_i2 = [z1^4 z2^3 z3^4] Q_i`,

`q_i3 = [z1^4 z2^4 z3^3] Q_i`.

Then

`lambda_i^can(y_1,y_2,y_3) = q_i1 y_1 + q_i2 y_2 + q_i3 y_3`.

Thus the canonical deletion functional is the cofactor covector

`q_i=(q_i1,q_i2,q_i3)`.

## Gradient interpretation

Since F is multilinear in each h_i,

`q_ir = partial F / partial a_{ir}`.

Hence

`lambda_i^can = grad_{h_i} F`.

All twelve deletion functionals are therefore **not independent choices**. They are the twelve block-gradients of one and the same multilinear polynomial F evaluated at the same maximal kernel sequence H.

In particular,

`lambda_i^can(h_i)=q_i dot h_i = F(H)=1`

for every i.

The normalized missing-value functional used in the local-scalarization packet is `-lambda_i^can`; the common-RHS finite tests are invariant under this global nonzero rescaling.

## Explicit partition form

The common polynomial can also be written without group algebra as

`F(H) = sum_P prod_{j in P1} a_{j1} prod_{j in P2} a_{j2} prod_{j in P3} a_{j3}`,

where the sum ranges over ordered partitions

`[12]=P1 disjoint-union P2 disjoint-union P3`

with `|P1|=|P2|=|P3|=4`.

The cofactor coordinate `q_i1`, for example, is the analogous partition sum of the remaining eleven indices into sizes `(3,4,4)`.

This gives a primitive finite-field verifier independent of group-algebra implementation.

## Consequence for the six k=4 obstruction orbits

The failed one-functional test treated the local scalar functionals for different residual-block deletions as unconstrained except for nonzeroness. That relaxation is too broad.

Any actual C15 lift must admit:

1. twelve kernel block sums `h_1,...,h_12 in F_5^3` forming a maximal zero-sum-free sequence;
2. `F(H)=1` after choosing a kernel basis;
3. for every deletion/replacement family used in the quotient residual, the corresponding scalar constraint must use the **specific cofactor functional** `grad_{h_i}F`, not an arbitrary unrelated functional.

Therefore the six quotient obstruction orbits remain only projected obstructions. Their next exact discriminator is **cofactor-lift feasibility**.

## Next frozen question

For each of the six k=4 quotient obstruction orbits, determine whether there exists any assignment of kernel vectors to the residual positions together with ten fixed triple-block sums such that:

- the resulting 12 block sums are maximal zero-sum free in `C_5^3`;
- their common top coefficient satisfies `F(H) != 0` (normalized to 1 by basis/scaling where admissible);
- every legal replacement equation is satisfied by the cofactor functional belonging to the replaced block.

A proof that all six are infeasible would close the k=4 residual. A feasible witness becomes the next exact obstruction state.

## Claim boundary

The cofactor identity is extracted from donor group-algebra mathematics and receives no standalone novelty credit. Novelty, if any, can arise only from a new all-instance consequence of this coupling for the C15 rank-3 lift problem or beyond.
