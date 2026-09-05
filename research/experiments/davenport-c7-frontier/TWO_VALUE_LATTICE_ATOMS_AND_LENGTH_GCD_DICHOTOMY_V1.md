# Consecutive lattice atoms and the two-value length-gcd dichotomy — V1

Status: **proved structural theorem for every full-rank sublattice of `Z^2`**, with a prime-cyclic rigid-power dichotomy as a consequence. Atom types mean count vectors, not different labeled realizations of the same vector.

## 1. General lattice theorem

Let `L` be a full-rank sublattice of `Z^2`, with finite index

\[
\Delta=[\mathbb Z^2:L].
\]

An **atom** of `L∩N_0^2` is a nonzero point that cannot be written as a sum of two nonzero points of this monoid. Equivalently, `P` is an atom precisely when there is no lattice point `E` with `0≤E≤P` coordinatewise except `0` and `P`.

The atoms are finite in number. Indeed, let `M,N` be the least positive integers with `(M,0),(0,N)∈L`; these exist because `L` has finite index. The only axis atoms are these two points. Every other atom has coordinates `0<A<M` and `0<B<N`, since otherwise it contains an axis atom as a proper componentwise divisor. Any two distinct atoms are incomparable coordinatewise. Consequently their first coordinates are all distinct, and arranging them in decreasing first coordinate arranges their second coordinates in strictly increasing order. The list starts with `(M,0)` and ends with `(0,N)`.

> **Consecutive-atom determinant theorem.** If `P=(A,B)` and `Q=(C,D)` are consecutive in this ordered list, with `A>C` and `B<D`, then
>
> \[
> \boxed{\det(P,Q)=AD-BC=\Delta.}
> \]

**Proof.** The determinant is positive. The lattice `L'=ZP+ZQ` is a full-rank sublattice of `L`, so

\[
AD-BC=[\mathbb Z^2:L']=[\mathbb Z^2:L][L:L']=k\Delta
\]

for a positive integer `k`.

Suppose `k>1`. A nonzero coset of `L/L'` has a representative in the half-open fundamental parallelogram of `P,Q`, obtained by subtracting integer multiples of these two basis vectors. Thus there is a nonzero point

\[
T=\alpha P+\beta Q\in L,
\qquad 0\le\alpha,\beta<1.
\]

Neither coefficient can be zero: if, say, `α=0`, then `0<β<1` and `T=βQ` is a nonzero proper coordinatewise divisor of the atom `Q`. The same argument excludes `β=0`.

If `α+β>1`, replace `T` by `P+Q−T`. This replacement is again a lattice point, and its coefficients `1−α,1−β` are positive and have sum less than one. After this replacement if necessary, we therefore have

\[
T=\alpha P+\beta Q\in L,
\qquad \alpha,\beta>0,
\qquad \alpha+\beta\le1.
\]

In particular,

\[
T_1=(\alpha+\beta)A-\beta(A-C)<A,
\qquad
T_2=(\alpha+\beta)D-\alpha(D-B)<D.
\]

Choose an atom `E=(E_1,E_2)` dividing `T` coordinatewise. Such an atom exists by descent on the positive integer coordinate sum. We have `E_1<A` and `E_2<D`. If `E_1≤C`, then `E` is a nonzero proper coordinatewise divisor of `Q`, contradicting atomicity of `Q`. Hence `E_1>C`. Likewise, if `E_2≤B`, then `E` is a nonzero proper divisor of `P`, so `E_2>B`. Thus

\[
C<E_1<A,
\qquad B<E_2<D.
\]

The atom `E` lies strictly between the asserted consecutive atoms, a contradiction. Therefore `k=1`. QED.

The proof uses only elementary lattice index, a fundamental parallelogram, and atomicity. It assumes neither convexity of an unexplained Hilbert-basis chain nor any higher-dimensional unimodularity theorem.

## 2. Rectangles inherit consecutive atoms

Fix nonnegative integer capacities `r,t`. The atoms in the rectangle

\[
\mathcal R=[0,r]\times[0,t]
\]

form a contiguous segment of the ordered global list. If two such atoms surround a third global atom, the third has its first coordinate between their first coordinates and its second coordinate between their second coordinates, and so also belongs to the rectangle.

If the rectangle contains at least two atoms, it therefore contains a globally consecutive pair `P=(A,B),Q=(C,D)`. A common divisor of the coordinate sums of **all** atoms in the rectangle divides both `A+B` and `C+D`, and hence divides

\[
A(C+D)-C(A+B)=AD-BC=\Delta.
\]

Thus the following statement holds without any prime or cyclic assumption:

> If a capacity rectangle contains at least two atoms of `L∩N_0^2`, the gcd of their coordinate sums divides `[Z^2:L]`.

For any two elements `x,y` of a finite abelian group, the relation lattice

\[
L_{x,y}=\{(A,B)\in\mathbb Z^2:Ax+By=0\}
\]

has index `|<x,y>|`, by the homomorphism `(A,B)↦Ax+By`. Its nonnegative atoms are exactly the count vectors of the zero-sum sequence atoms supported on `x,y`. Consequently the gcd statement applies directly to atomic sequence divisors with actual occurrence capacities.

## 3. Prime-cyclic dichotomy

Let `p` be prime and let `x,y` be distinct nonzero values of `C_p`. Let

\[
S=x^r y^t,
\qquad 0\le r,t\le p-1.
\]

Every atom dividing `S` is mixed: a nonempty pure zero-sum would require `p` occurrences. Every cyclic atom has length at most `p`, by the distinct proper partial sums argument. A mixed atom `x^A y^B` cannot have length `p`: if `A+B=p`, then its zero-sum equation gives

\[
0=Ax+(p-A)y=A(x-y),
\]

contradicting `1≤A<p` and `x≠y`. Thus every atomic divisor has length strictly less than `p`.

The relation lattice has index `p`. By Section 2, if at least two distinct atomic count-vector types occur, their length gcd divides `p`; because it also divides a positive length smaller than `p`, it equals one.

> **Two-value spectral dichotomy.** A sequence with two distinct nonzero values in `C_p`, each used fewer than `p` times, either has at most one distinct atomic divisor or the gcd of all its atomic-divisor lengths is one.

If `S` is nonempty zero-sum, it has an atomization. In the one-atomic-divisor case, every factor is the unique atom `Q`, so `S=Q^k`. If also `|S|>p`, then `k≥2`. Thus for such zero-sum sequences the alternatives are an actual rigid power or a length spectrum of gcd one.

No long-atom theorem, index-one theorem, or splitting lemma is used. Merely exhibiting a power factorization is insufficient: the dichotomy is about the full set of atomic divisors in the capacity rectangle.

## 4. Review and exact scope

The proof was independently developed in the proof-audit lane, checked by the quotient-structure lane, and reviewed by the coordinating researcher. The review includes the finiteness and ordering of atoms, the fundamental-parallelogram point and its complement, rectangle contiguity, and the strict prime-order atom-length bound. This is internal mathematical scrutiny, not external referee approval or a claim of literature priority.

The gcd-one alternative is real: the theorem does not force every two-value zero-sum sequence to be rigid. It applies only to two-dimensional relation lattices and does not assert higher-dimensional unimodularity. No prime, vector, or subsequence enumeration supplies the proof. No first-corridor theorem or unproved generalized Davenport equality is asserted.
