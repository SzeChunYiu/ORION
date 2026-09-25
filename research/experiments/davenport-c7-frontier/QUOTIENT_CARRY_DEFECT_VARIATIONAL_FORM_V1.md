# Exact quotient atomization and kernel carry — V1

Status: **proved first-principles variational identity over every finite abelian group, with an explicit obstruction to greedy projection**. This supplies an exact generalized form for transferring the packing problem to a subgroup and quotient. It does not bound the resulting minimum by the proposed rank-three intercept.

## 1. Atomize the quotient, retaining every occurrence

Let `G` be a finite abelian group, let `H<=G`, and let `pi:G->G/H` be the quotient map. Write a zero-sum block as

\[
B=KR,
\]

where `K` consists of all term occurrences in `H`, and `R` consists of the remaining occurrences. Both may be empty. Although `R` need not sum to zero in `G`, its projection does sum to zero in `G/H`.

Let `P=(T_1,...,T_t)` range over all occurrence partitions of `R` for which each `pi(T_i)` is an atom in `G/H`. Such partitions exist by atomizing the zero-sum projected sequence. When `R` is empty, include the empty partition.

Each aggregate `sigma(T_i)` belongs to `H`. Form the labeled kernel block

\[
K_P=K\prod_{i=1}^t \sigma(T_i).
\]

The aggregate occurrences remain distinguished, including aggregates equal to zero or to an existing term of `K`. Its sum is zero because `sigma(K_P)=sigma(B)`.

> **Exact quotient-factorization theorem.**
>
> \[
> \boxed{z_G(B)=\max_P z_H(K_P).}
> \tag{1}

For each fixed `P`, every kernel factorization lifts to a zero-sum partition of `B`: replace an aggregate occurrence by its bundle `T_i`. Thus `z_H(K_P)<=z_G(B)`.

For the reverse inequality, choose a maximum atomic factorization of `B`. For each factor that meets `R`, atomize the projection of its `R` part. Collect all these projected atoms into `P`. In `K_P`, put each resulting aggregate together with the original kernel occurrences from the same factor of `B`. Factors wholly in `K` remain as they are. This is a partition of `K_P` into `z_G(B)` nonempty zero-sum blocks. Hence `z_H(K_P)>=z_G(B)` for this particular `P`, proving (1).

The proof needs no inverse theorem for quotient atoms and makes no assertion that an arbitrary fixed projected atomization attains the maximum.

## 2. Exact defect decomposition

Fix a positive integer slope `n`, in particular `n=exp(G)`, and use the same slope on both groups:

\[
\delta_n^G(B)=|B|-n z_G(B),\qquad
\delta_n^H(C)=|C|-n z_H(C).
\]

Put

\[
d(P)=\sum_i(|T_i|-1)=|R|-t.
\]

Since `|K_P|=|K|+t=|B|-d(P)`, equation (1) gives

> **Generalized quotient defect formula.**
>
> \[
> \boxed{\delta_n^G(B)=
> \min_P\left(d(P)+\delta_n^H(K_P)\right).}
> \tag{2}

The subgroup defect is measured using `n`, even when `exp(H)<n`; replacing it silently by its own-exponent defect changes the formula.

For `G=C_p^3` and any line `H`, the target becomes the precise selection inequality

\[
\min_P\left(\sum_i(|T_i|-1)+\delta_p^H(K_P)\right)
\le \frac{5(p-1)}2.
\tag{3}
\]

Equation (2) is proved. Inequality (3) for arbitrary `B` is still the global problem. The classical rank-two constants control which quotient atomizations exist, but do not by themselves control their kernel contributions or select one achieving (3).

## 3. A scalar reservoir makes the carry literal

Suppose `H=<g>` has order `n`, and the kernel part of `B` is exactly `g^w`, with `0<=w<n`. Assume `R` is nonempty. In this section let `Q=(T_1,...,T_t)` be an arbitrary projected-zero partition, with no requirement that its projected parts be atoms.

There is a unique `c_i` in `{0,...,n-1}` satisfying

\[
\sigma(T_i)+c_i g=0.
\]

Total zero sum gives `sum_i c_i == w (mod n)`. Therefore

\[
\sum_i c_i=w+hn,\qquad h\ge0,
\]

and the occurrence identity is

\[
\boxed{B(g^n)^h=\prod_i(T_i g^{c_i}).}
\tag{4}
\]

The integer `h` counts the extra full cyclic blocks required to complete this particular projected partition separately. It is not a free resource present in `B`.

> **Zero-carry allocation theorem.**
>
> \[
> \boxed{z_G(B)=\max_{Q:\,\sum_i c_i=w} t.}
> \tag{5}

Every zero-carry partition in (5) gives a factorization of `B` into `t` nonempty zero-sum blocks by (4). Conversely, in a maximum atomic factorization of `B`, every factor meets `R`: a nonempty zero-sum factor made only from fewer than `n` copies of `g` cannot exist. Restricting the factors to `R` gives a projected-zero partition. The number of copies of `g` used by its `i`th factor lies between zero and `w<n`, so it equals the canonical `c_i`. Their sum is exactly `w`, proving (5).

Refining a projected part into quotient atoms can increase the sum of its canonical completion residues by a multiple of `n`. Thus zero carry need not survive refinement. Formula (1) accounts for this by permitting subsequent kernel regrouping; formula (5) accounts for it by optimizing over general projected-zero parts. Mixing these two domains would be an error.

## 4. Greedily maximizing quotient factors can lose arbitrarily many ambient factors

The obstruction is structural and uses no enumeration. Take `G=C_p^3`, `p>=5`, a basis `e_1,e_2,e_3`, and

\[
g=e_1+e_2+e_3,\qquad H=\langle g\rangle,\qquad
B_L=e_1^{pL}e_2^{pL}e_3^{pL}\quad(L\ge1).
\]

Independence of the basis implies that every zero-sum atom dividing `B_L` is one of `e_i^p`. Hence

\[
z_G(B_L)=3L,\qquad \delta_p^G(B_L)=0.
\]

In `G/H`, the three projected values have the relation

\[
\bar e_1+\bar e_2+\bar e_3=0,
\]

and every pair is independent. Every projected atom is either a pure `\bar e_i^p` or the triple `\bar e_1\bar e_2\bar e_3`: if its three multiplicities are positive, their common residue modulo `p` makes it contain the triple; if one is zero, independence forces a pure `p`-power atom.

For any projected factorization let `k` count its triple atoms and `a_i` count its pure atoms. Occurrence accounting gives

\[
k+p a_i=pL\quad(i=1,2,3).
\]

Thus `k=pj` for `0<=j<=L`, `a_i=L-j`, and its number of projected atoms is

\[
3L+(p-3)j.
\]

This is maximized only at `j=L`: all `pL` projected atoms are triples. Each triple lifts to sum `g`, so this greedy projected atomization has kernel block `g^{pL}` and lifts to only `L` ambient factors. Its value in the defect objective (2) is `2pL`, while the correct minimum is zero.

In contrast, projecting the actual pure-power factorization gives `3L` kernel occurrences equal to zero and recovers all `3L` ambient factors. Therefore even a **maximum** quotient atomization can lose `2L` packing factors, with no bound independent of the sequence length. Knowing exact quotient multiwise constants does not repair this choice error.

In the scalar-reservoir language, the all-triple partition has `w=0`, `c_i=p-1`, and carry `h=L(p-1)`. The pure-power partition has zero carry. The two formulations agree exactly.

The family is not a counterexample to the proposed rank-three line and is not short-zero-free. Its role is to invalidate the unrestricted greedy-transfer step and identify the quantity that an additional structural theorem must control.

## 5. Interface with the minimal-core contraction theorem

If `B` is a shortest counterexample with defect `M+1`, then every family of disjoint projected-zero bundles of total cost at most `p` can be contracted without changing its packing number. These aggregates may be moved into a chosen kernel line while retaining an optimum. For a complete quotient atomization `P`, its cost need not be at most `p`; in that case packing preservation is not supplied by the minimal-core theorem.

Consequently the two legitimate routes are now explicit: control a complete quotient atomization's exact kernel defect in (2), or construct a sufficiently inexpensive partial contraction to which the proved compatibility theorem applies. Neither route permits discarding carry or assuming the canonical saturated donor form in advance.

Audit: the subgroup-transfer specialist supplied the scalar carry idea and fixed-partition warning. The coordinator derived and reviewed the exact arbitrary-subgroup identity, the converse lift from an ambient optimum, the scalar allocation theorem, and the complete greedy counterexample. The proofs are elementary; no search, finite realization check, or novelty/priority claim is used.
