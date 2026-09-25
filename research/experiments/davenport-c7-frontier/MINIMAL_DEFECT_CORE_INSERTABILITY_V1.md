# Minimal defect cores: atom insertion and a four-atom exchange obstruction — V1

Status: **proved elementary reductions; final written proof reviewed by the coordinating researcher**.
The assertions below are reductions and an explicitly delimited failed-route
example. They do not prove the general Davenport line or `D_3(C_7^3)`.

## 1. Minimality by sequence length

Let `p>=5` be prime, let `G=C_p^3`, and put

\[
M=\frac{5p-5}{2},\qquad
\delta(B)=|B|-p z(B).
\]

Assume there is a zero-sum block with defect greater than `M`, and choose
such a block `B` of minimum term length. Write

\[
z(B)=m,\qquad \delta(B)=M+q,\qquad q\ge1.
\]

Every proper zero-sum divisor `C` of `B` satisfies `delta(C)<=M`.
This conclusion uses length minimality, without assuming that the proposed
formula has already been proved at all lower multiwise levels. The classical
value `D(G)=3p-2` and the verified donor-derived value
`D_2(G)=2p+M` imply `m>=3`.

Here and throughout, occurrences, rather than only their values, are the
objects partitioned into subsequences.

### Contraction forces unit overshoot

Replace any two occurrences `a,b` of `B` by their sum `a+b`, obtaining a
shorter zero-sum block `B'`. Every atomic factorization of `B'` lifts to a
factorization of `B` into nonempty zero-sum blocks: expand the distinguished
occurrence `a+b` inside its factor and then factor the resulting block into
atoms. Consequently `z(B')<=m`.

By minimality,

\[
M\ge\delta(B')
 =M+q-1+p\bigl(m-z(B')\bigr).
\]

Both `q-1` and `m-z(B')` are nonnegative integers. Thus

\[
\boxed{q=1,\qquad z(B')=m.}
\]

In particular every shortest bad block has the exact critical length

\[
\boxed{|B|=pm+M+1.}
\]

The general simultaneous-bundle contraction theorem is developed separately
in the first-principles contraction note. The arguments below require only
minimality and the displayed unit overshoot.

## 2. Packing interaction across every zero-sum cut

Let `B=AC`, where `A,C` are nonempty zero-sum blocks. Put

\[
r=z(A),\quad s=z(C),\quad h=m-r-s.
\]

The concatenation of optimum factorizations of `A` and `C` shows `h>=0`.
Directly from the definition of defect,

\[
\boxed{\delta(A)+\delta(C)=M+1+ph.}
\]

Both sides of the cut are proper divisors, so each has defect at most `M`.
Hence

\[
\boxed{0\le h\le\left\lfloor\frac{M-1}{p}\right\rfloor.}
\]

This upper bound is one for `p=5` and two for `p>=7`. Thus an arbitrary
zero-sum cut can lose at most two packings relative to the optimum of the
whole minimal bad block. The integer `h` measures this loss; it is not
assumed to vanish.

For a merely divisibility-minimal bad block of defect `M+q`, the same proof
gives `h<=floor((M-q)/p)`. Length minimality is what supplies `q=1`.

### Defect controls insertion of an entire block

The same cut identity, using only `delta(C)<=M`, gives

\[
\boxed{ph\le\delta(A)-1.}
\]

Thus every proper zero-sum block `A` with `delta(A)<=p` can be inserted
with its full packing number into an optimum of `B`:

\[
z(B)=z(A)+z(B A^{-1}).
\]

In this situation **every** maximum factorization of `A` can be extended
by a maximum factorization of its complement. This does not say that an
arbitrary nonmaximum atomization of `A` can be extended to an optimum.

### Simultaneous pinning of specified atoms

There is a stronger formulation that keeps the actual chosen atoms.
Let `A_1,...,A_r` be occurrence-disjoint atoms in `B`, let
`C=B/(A_1...A_r)`, and put

\[
E=\sum_{i=1}^r(|A_i|-p),\qquad
h=m-r-z(C)\ge0.
\]

Allow `C` to be empty, with `z(C)=delta(C)=0`. It is a proper divisor,
so in all cases `delta(C)<=M`. Exact accounting gives

\[
\delta(C)=M+1-E+ph,
\qquad
\boxed{E\ge ph+1.}
\]

Consequently, whenever `E<=p`, **all the specified atoms are jointly
contained in a maximum factorization**. When `E<=2p`, imposing all of
them costs at most one packing factor. No assumption that their product
was already maximally factored is needed: the inequality itself gives
that conclusion in the `E<=p` case.

This is an atomic excess budget, parallel to the contraction-cost budget
in the companion note. More generally, over any finite abelian group
with exponent `n`, a cardinality-minimal defect counterexample at threshold
`M>=0` satisfies `E>=nh+1` for occurrence-disjoint specified atoms, where
`E=sum_i(|A_i|-n)`. The proof is the same unit-excess and complement
identity; rank three is not needed for this statement.

## 3. Every atom is at most one insertion short of an optimum

Let `A|B` be any atom, and set `C=B A^{-1}`. Since `m>=3`, the complement is
nonempty. Write

\[
e=|A|-p,\qquad h=m-1-z(C).
\]

The cut identity and `delta(C)<=M` give

\[
e+\delta(C)=M+1+ph,
\qquad ph\le e-1.
\]

Since an atom has length at most `3p-2`, one has `e<=2p-2`. Therefore

\[
\boxed{h\in\{0,1\},\qquad z(B A^{-1})\in\{m-1,m-2\}.}
\]

Call `A` *insertable* when some maximum factorization of `B` contains `A`.
This is equivalent to `h=0`. The preceding inequality proves the useful
uniform threshold

\[
\boxed{|A|\le2p\ \Longrightarrow\ A\text{ is insertable}.}
\]

Conversely, every noninsertable atom has `|A|>=2p+1`, and deleting it loses
exactly two packings. Its complement is quantitatively near the defect
boundary:

\[
\delta(C)=M+1+p-e\ge M-p+3.
\]

For a divisibility-minimal bad block with general overshoot `q`, the same
calculation gives insertability whenever `|A|<=2p+q-1`, and a possible
insertion deficit of at most one.

### The sharper three-packing threshold

Suppose `m=3` and `A` is noninsertable. Its complement then has packing
number one and is itself an atom. Therefore

\[
|A|\ge |B|-(3p-2)=M+3=\frac{5p+1}{2}.
\]

Writing `H=(p-1)/2`, this proves

\[
\boxed{m=3,\ |A|\le2p+H
\ \Longrightarrow\ A\text{ is insertable}.}
\]

For `p=7`, every atom of length at most 17 in a shortest bad block with
packing number three is insertable. This statement neither forces a
19-atom nor restricts a maximal atom to support four.

## 4. Noninsertability requires mixing at least three optimum atoms

Fix any maximum factorization

\[
B=U_1\cdots U_m.
\]

An atom `A|B` contained occurrencewise in one of the `U_i` must equal that
atom and is insertable. If `A` is contained in `U_i U_j`, its complement
inside that product is a nonempty zero-sum block: it cannot be empty because
the product of two nonempty zero-sum blocks is not an atom. Factoring this
complement and adjoining the other `m-2` atoms gives at least `m` factors
containing `A`. Optimality then gives exactly `m`.

Consequently

\[
\boxed{A\text{ noninsertable}
\ \Longrightarrow\ A\text{ meets at least three atoms of every optimum}.}
\]

This is a necessary mixing condition, not a positive-gain exchange theorem.
In particular the conclusion does not say that three source atoms suffice
to repair a noninsertable atom.

## 5. A structural obstruction to unrestricted three-atom augmentation

The restriction to minimal overbudget cores matters. Even in `C_p^3`,
an arbitrary atomization can resist every exchange of at most three source
atoms while admitting a larger atomization.

Choose a basis `e_1,e_2,e_3` and set

\[
g_1=e_1,\quad g_2=e_2,\quad g_3=e_3,\quad
g_4=-e_1-e_2-e_3.
\]

Let

\[
U_i=g_i^p,\qquad W=g_1g_2g_3g_4,
\qquad B_0=U_1U_2U_3U_4.
\]

Each `U_i` is an atom, and `W` is an atom because every three distinct
`g_i` are linearly independent. There are two factorizations

\[
\boxed{B_0=U_1U_2U_3U_4=W^p.}
\]

For completeness, these are the only atomic factorizations. A zero-sum
subsequence with multiplicities `0<=a_i<=p` satisfies

\[
a_1\equiv a_2\equiv a_3\equiv a_4\pmod p.
\]

If a multiplicity is zero, all multiplicities are zero or `p`, and any
nonempty such atom is a single `U_i`. Otherwise either the subsequence
contains a `U_i`, or all four multiplicities have a common value between
one and `p-1`. In the latter case the subsequence is a power of `W`, and is
an atom precisely when it equals `W`.

Thus every atom dividing `B_0` is one of `U_1,...,U_4,W`. Using any `W`
precludes all `U_i`, since each `W` consumes an occurrence of every `g_i`.
The remaining counts then force exactly `p` copies of `W`. Using no `W`
forces exactly the four `U_i`.

Every proper subproduct of `U_1,...,U_4` consequently has a unique
factorization. For `p>=5`, the four-atom factorization can be improved to
`p` atoms, but no exchange using at most three of its source atoms can
improve it. The minimum improving source arity is exactly four.

### What this example does and does not refute

It refutes a general rule that rank three, atomhood, or the sharp rank-three
`D_2` value alone guarantees an improving exchange on at most three source
atoms whenever an atomization is nonoptimal.

It is **not** a counterexample to the proposed Davenport line, or to a
three-atom exchange theorem with extra minimal-overbudget hypotheses:

\[
z(B_0)=p,\qquad \delta(B_0)=4p-p^2\le0.
\]

Moreover `B_0` contains short zero-sums, including `W`, and its displayed
four-atom factorization is not maximum. A genuine bounded-exchange theorem
for the target must exploit the stronger hypotheses instead of relying
only on ambient rank or on pairwise numerical excess bounds.

## 6. The unresolved bridge to the local donor frontier

The insertability lemmas apply to every atom of a shortest bad block. They
do not supply any of the following additional hypotheses used by the
canonical donor arguments:

1. a maximum factorization containing an atom of length `3p-2`;
2. such a maximal atom having support four;
3. the companion lying in a specified first corridor;
4. the pair having exactly the required support size;
5. a new companion value having the saturation multiplicity used by a
   boundary theorem.

Each transition needs its own proof. The new global insertion threshold
and the local boundary eliminations can be combined only after the
relevant transition has been established.

No theorem here says that sharp `D_2` forces a three-atom positive-gain
exchange in an overbudget maximum factorization. Such a statement would
be a new load-bearing theorem: a maximum factorization cannot admit any
positive-gain exchange, so proving its existence would itself exclude the
putative core.

## Donor and audit boundary

- Classical input: `D(C_p^3)=3p-2`.
- Verified donor-derived input: `D_2(C_p^3)=(9p-5)/2`, with its proof and
  prime-power scope recorded in `D2_PRIME_POWER_COROLLARY_V1.md`.
- The contraction, cut, insertion, occurrence-mixing and four-circuit
  proofs above are elementary and contain no search or enumeration input.
- The proof auditor supplied the cut, atom-insertion, mixing and four-circuit
  arguments; the coordinator reviewed the final proof and added the exact
  block and simultaneous-atom pinning laws. The review checked the empty
  complement convention, maximum versus arbitrary atomizations, both
  `p=5` and `p>=7` cut bounds, the sharper three-packing threshold, and
  the complete two-factorization classification of the circuit witness.
  Novelty and priority remain `CANNOT_CHECK`.
