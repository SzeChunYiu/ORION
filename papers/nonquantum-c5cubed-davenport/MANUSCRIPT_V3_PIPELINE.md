# A Width-One Generalized-Davenport Corridor in \(C_5^3\) and a Rank-Forcing Obstruction Phase

## Abstract

Let \(D_k(G)\) be the least length that forces \(k\) pairwise disjoint nonempty
zero-sum subsequences. We show that the generalized Davenport constants of
\(C_5^3\) lie in the width-one corridor

\[
5k+10\le D_k(C_5^3)\le5k+11
\qquad(k\ge4).
\]

If \(D_4(C_5^3)=30\), then the lower line is exact for every \(k\ge2\). To
analyze the remaining alternative, we study a hypothetical total-zero sequence
of length \(31\) with no nonempty zero-sum subsequence of length at most five.
For saturated short-free sequences over elementary abelian groups of odd prime
exponent, we prove a defect certificate that excludes multiplicity \(p-2\). In
the case \(p=5\), only multiplicities \(1,2,4\) remain. If \(s\) is support size
and \(c_i\) counts multiplicity \(i\), then

\[
c_2=31-s-3c_4,
\qquad
c_1=2s-31+2c_4.
\]

The subsequence of points of multiplicity at least two has length
\(62-2s-2c_4\). Using \(\eta(C_5^2)=13\), we prove that this stratum must span
rank three whenever \(s+c_4\le24\). We also prove an exact identity coupling
support deficit, repetitions inside zero-sum atoms, and overlaps between atom
supports. Together with a theorem-grade exclusion through support ten, these
results isolate the residual obstruction phase without deciding it.

The exact value remains \(D_4(C_5^3)\in\{30,31\}\). A larger internal search
through support 22 is reported only as bounded computational evidence and is
not used as theorem authority.

## 1. Introduction

Generalized Davenport constants measure the sequence length required to force
several pairwise disjoint zero sums. Rank-two groups exhibit strong eventual
structure, whereas rank-three groups can depart from the expected arithmetic
progression.

For \(C_5^3\), the exact values \(D_2=20\) and \(D_3=25\), together with known
short-zero-sum thresholds, reduce the next value to

\[
D_4(C_5^3)\in\{30,31\}.
\]

This one-bit ambiguity controls the tail: the lower candidate \(D_4=30\) forces
\(D_k=5k+10\) for every \(k\ge2\). The upper candidate would yield a rigid
length-31 total-zero sequence with no zero sum of length at most five.

We combine the recurrence with symbolic analysis of that hypothetical
obstruction. The purpose is twofold: to obtain a rigorous width-one theorem for
the full tail and to identify exactly where existing rank reductions cease to
be automatic. Computation is kept in a separate evidence class.

Our contributions are:

1. the width-one corridor for every \(k\ge4\);
2. the conditional exact tail if \(D_4=30\);
3. an odd-prime saturation-defect lemma excluding multiplicity \(p-2\);
4. a theorem-grade support-at-least-eleven result for the length-31 obstruction;
5. an exact multiplicity parameterization for every remaining support stratum;
6. the rank-forcing phase \(s+c_4\le24\) for the high-multiplicity stratum; and
7. an identity coupling support deficit to internal atom repetition and
   cross-atom overlap.

## 2. Definitions and known inputs

For a finite abelian group \(G\), \(D_k(G)\) is the least integer \(n\) such
that every sequence of length at least \(n\) over \(G\) contains \(k\) pairwise
disjoint nonempty zero-sum subsequences. Let \(s_{\le\ell}(G)\) denote the least
length forcing a nonempty zero-sum subsequence of length at most \(\ell\).

We use the recurrence

\[
D_{k+1}(G)
\le\max\{D_k(G)+\ell, \ s_{\le\ell}(G)-1\},
\]

and the known lower bound \(D_k(C_5^3)\ge5k+10\) in the range considered here.
The exact registered inputs are

\[
D_2=20, \qquad D_3=25, \qquad s_{\le6}=24,
\]

while \(s_{\le5}(C_5^3)=\eta(C_5^3)=33\). We also use the rank-two value
\(\eta(C_5^2)=13\).

## 3. A width-one tail

Taking \(\ell=6\) gives

\[
D_4\le\max\{25+6,24-1\}=31.
\]

Together with the lower bound, this proves
\(D_4\in\{30,31\}\).

**Theorem 1.** For every \(k\ge4\),

\[
5k+10\le D_k(C_5^3)\le5k+11.
\]

**Proof.** The base case is \(D_4\le31\). Apply the recurrence with
\(\ell=5\) and \(s_{\le5}-1=32\). If \(D_k\le5k+11\), then both terms in the
maximum are at most \(5(k+1)+11\). The known lower bound supplies the lower
line. ∎

**Theorem 2.** If \(D_4(C_5^3)=30\), then

\[
D_k(C_5^3)=5k+10
\qquad(k\ge2).
\]

**Proof.** The statement holds for \(k=2,3,4\). Applying the same recurrence
with \(\ell=5\) propagates the upper bound \(5(k+1)+10\), which matches the
known lower bound. ∎

There is no converse here: the assumption \(D_4=31\) does not by itself prove
that later terms lie on the upper line.

## 4. The hypothetical length-31 obstruction

The upper candidate yields a sequence \(S\) over \(C_5^3\) satisfying

\[
|S|=31, \qquad \sigma(S)=0,
\]

with no nonempty zero-sum subsequence of length at most five. Every element has
multiplicity at most four. In the support case relevant here, the established
extension dichotomy forces saturation: appending any support element destroys
short-freeness.

**Theorem 3 (saturation defect).** Let \(p\) be odd and let \(S\) be a saturated
\(p\)-short-free sequence over an elementary abelian exponent-\(p\) group. If a
nonzero element \(x\) has multiplicity \(m<p\), then there is a subsequence \(R\)
such that

\[
|R|\le p-1-m,
\qquad x\notin\operatorname{supp}(R),
\qquad \sigma(R)=-(m+1)x.
\]

**Proof.** Append one further copy of \(x\). Saturation supplies a zero-sum
subsequence of length at most \(p\) that uses the appended occurrence. It must
also use every original copy of \(x\); otherwise replacing the appended copy by
an unused original occurrence would give a short zero sum already contained in
\(S\). Removing the \(m+1\) copies of \(x\) leaves the required \(R\). ∎

**Corollary 4.** Multiplicity \(p-2\) is impossible.

Indeed, the defect subsequence would have length at most one and sum \(x\),
forcing a forbidden additional copy of \(x\). For \(p=5\), multiplicity three
is absent. Singleton and double points also acquire defect certificates of
length at most three and two, respectively.

## 5. Exact multiplicity grammar

Let \(s=|\operatorname{supp}(S)|\), and let \(c_1, c_2, c_4\) count points of
multiplicity one, two, and four. Then

\[
c_1+c_2+c_4=s,
\qquad
c_1+2c_2+4c_4=31.
\]

Writing \(c_4=j\) gives

\[
c_2=31-s-3j,
\qquad
c_1=2s-31+2j.
\]

Thus \(c_1\) is odd, and nonnegativity determines the complete admissible range
for every support size. For example, the support-23 patterns are

\[
1^{15}2^8, \qquad 1^{17}2^5 4, \qquad 1^{19}2^2 4^2,
\]

and the support-24 patterns are

\[
1^{17}2^7, \qquad 1^{19}2^4 4, \qquad 1^{21}2 4^2.
\]

## 6. The rank-forcing phase

Let \(H\) be the subsequence consisting of all points of multiplicity two or
four. Its length is

\[
|H|=2c_2+4c_4=62-2s-2c_4.
\]

If \(H\) were contained in a subgroup of rank at most two, it would be a
5-short-free sequence over \(C_5^2\). The value
\(\eta(C_5^2)=13\) forces a short zero sum once \(|H|\ge13\). Since \(|H|\) is
even, the contradiction begins at \(|H|\ge14\).

**Theorem 5 (rank-forcing phase).** The high-multiplicity stratum spans rank
three whenever

\[
s+c_4\le24.
\]

**Proof.** The condition \(|H|\ge14\) is equivalent to
\(62-2s-2c_4\ge14\), hence to \(s+c_4\le24\). ∎

The theorem gives the following exact boundary:

| Support | \(c_4\) | Consequence from Theorem 5 |
|---:|---:|---|
| 23 | 0 or 1 | rank three forced |
| 23 | 2 | threshold is silent |
| 24 | 0 | rank three forced |
| 24 | 1 or 2 | threshold is silent |
| at least 25 | any admissible value | threshold is silent |

Silence is not a converse. Outside the phase, rank three may follow from a
different argument.

## 7. Theorem-grade low-support exclusion and bounded evidence

Signed symbolic reductions combined with two exact state representations
exclude every support size through ten.

**Theorem 6.** Every length-31 total-zero 5-short-free sequence over \(C_5^3\),
if one exists, has support at least eleven.

A larger internal computation found no such sequence through support 22. That
search has not received an external independent replay and is not used in any
proof above or below. Its bounded conclusion is useful for prioritizing the
next case split, but it does not establish support at least 23 as a theorem.

## 8. Atom repetition and overlap

Under the conditional assumption \(D_4=31\), extremal factorization arguments
force one of the atom-length types

\[
(6,6,6,13)
\qquad\text{or}\qquad
(6,6,7,12).
\]

Let \(S=U_1\cdots U_r\) be an occurrence-disjoint atom factorization. For each
group element \(g\), let \(r_g\) be the number of atom supports containing \(g\),
and define the internal deficit

\[
\delta_i=|U_i|-|\operatorname{supp}(U_i)|.
\]

**Theorem 7 (repetition-overlap identity).** Every occurrence-disjoint
factorization satisfies

\[
|S|-|\operatorname{supp}(S)|
=\sum_i\delta_i
+\sum_{g\in\operatorname{supp}(S)}(r_g-1).
\]

**Proof.** Summing the atom support sizes counts every global support point
\(r_g\) times. Hence

\[
\sum_i\delta_i=|S|-\sum_g r_g,
\]

while cross-atom overlap equals

\[
\sum_g r_g-|\operatorname{supp}(S)|.
\]

Adding the two identities proves the claim. ∎

Thus any independently established lower support bound \(s_0\) gives a total
internal-repetition plus cross-overlap budget of at most \(31-s_0\). The proven
value \(s_0=11\) gives budget 20. If the bounded support-22 computation is later
independently certified, the budget sharpens to eight; that sharper value is
conditional and not used as theorem authority here.

## 9. The residual obstruction phase

A decisive next analysis should impose simultaneously:

1. the multiplicity pattern from Section 5;
2. the rank status from Theorem 5;
3. the saturation-defect certificate at every singleton and double point;
4. one of the two conditional atom-length types;
5. the repetition-overlap identity; and
6. total sum zero with exclusion of zero sums of lengths one through five.

This intersection is substantially smaller than an unstructured support search.
A surviving sequence would require independent factorization verification before
establishing \(D_4=31\). A complete, independently replayed infeasibility proof
for the length-31 target would establish the lower candidate \(D_4=30\).

## 10. Relation to prior work

The generalized-Davenport recurrence, lower-bound framework, extremal
factorization language, and eventual-linearity context are established results.
The \(C_0\) framework and short-zero-sum localization are also prior work, as
are the inverse zero-sum program and rank-two inverse results.

The residual contribution is the width-one synthesis for \(C_5^3\), the
saturation-defect specialization, the exact multiplicity grammar, the
rank-forcing phase, and the coupling of support deficit with atom repetition and
overlap. These are structural compression results; they do not decide the final
extremal bit.

## 11. Reproducibility and limitations

The corridor, defect lemma, and support-ten exclusion are separately bound to
exact records. An independent verifier enumerates all multiplicity patterns for
supports 8–31, checks the rank-phase equivalence, reproduces the support-23 and
support-24 tables, and validates the atom identity on independently generated
factorizations. The displayed proofs carry all-parameter authority.

The exact value of \(D_4(C_5^3)\) remains open, as does the associated
length-31 extremal-spectrum statement. The support-22 frontier is bounded
computation pending external replay. The rank phase is one-way, and the atom
identity is a compression principle rather than a contradiction. No additional
internal implementation can substitute for an independently auditable final
obstruction proof.

## 12. Conclusion

The generalized Davenport constants of \(C_5^3\) remain within one unit of the
line \(5k+10\) for every \(k\ge4\), and the lower choice at \(k=4\) would fix the
entire tail. The hypothetical upper-line obstruction has substantially more
structure than this corridor alone reveals: its multiplicities have an exact
grammar, its high-multiplicity stratum enters a sharp rank-forcing phase, and
its atom factorization obeys a global repetition-overlap budget.

These results explain where the residual difficulty begins and define a smaller
intersection problem for the unresolved extremal bit. They do not claim to have
resolved it.

## Data and code availability

The verification package contains exact multiplicity enumeration, rank-phase
checks, atom-identity tests, and separately labeled bounded-search records. A
permanent archival identifier should be added before final submission.

## References

1. M. Freeze and W. A. Schmid, “Remarks on a Generalization of the Davenport
   Constant,” *Discrete Mathematics* **310**, 3373–3389 (2010).
   DOI: 10.1016/j.disc.2010.07.032
2. Y. Fan, W. Gao, G. Wang, Q. Zhong, and J. Zhuang, “On Short Zero-Sum
   Subsequences of Zero-Sum Sequences,” *Electronic Journal of Combinatorics*
   **19**(3), P31 (2012). DOI: 10.37236/2602
3. W. Gao, A. Geroldinger, and W. A. Schmid, “Inverse Zero-Sum Problems,”
   *Acta Arithmetica* **128**, 245–279 (2007).
   DOI: 10.4064/aa128-3-5
4. Q. Zhong, “On the Inverse Problem of the \(k\)-th Davenport Constants for
   Groups of Rank 2,” *Combinatorica* **45**, article 31 (2025).
   DOI: 10.1007/s00493-025-00153-3
