# Conditional Width-One Bounds for Generalized Davenport Constants of \(C_5^3\)

## Abstract

Let \(D_k(G)\) be the least length that forces \(k\) pairwise disjoint nonempty
zero-sum subsequences. Conditional on the exact inputs \(D_3(C_5^3)=25\),
\(s_{\le6}(C_5^3)=24\), \(s_{\le5}(C_5^3)=33\), and the lower line
\(D_k(C_5^3)\ge5k+10\), we derive
\(5k+10\le D_k(C_5^3)\le5k+11\) for every \(k\ge4\).

If \(D_4(C_5^3)=30\), then the lower line is exact for every \(k\ge2\). To
analyze the remaining alternative, we study a hypothetical total-zero sequence
of length \(31\) with no nonempty zero-sum subsequence of length at most five.
For saturated short-free sequences over elementary abelian groups of odd prime
exponent, we prove a defect certificate that excludes multiplicity \(p-2\). In
the case \(p=5\), a saturated obstruction (in particular, every obstruction
with support at least nine) has only multiplicities \(1,2,4\). If \(s\) is support size
and \(c_i\) counts multiplicity \(i\), then \(c_2=31-s-3c_4\) and
\(c_1=2s-31+2c_4\).

The subsequence of points of multiplicity at least two has length
\(62-2s-2c_4\). Using the short-zero-sum threshold \(\eta(C_5^2)=13\), we prove
that this stratum must span rank three whenever \(s+c_4\le24\). We also prove an exact identity coupling
support deficit, repetitions inside zero-sum atoms, and overlaps between atom
supports. Two separate exact implementations found no obstruction through
support ten within the supplied computational model. Because this computation
has not been independently replicated, we report it only as bounded
computational evidence.

The exact value remains \(D_4(C_5^3)\in\{30,31\}\). A larger search through
support 22 is also bounded evidence and has no theorem authority.

**Keywords:** generalized Davenport constants; zero-sum sequences; elementary
abelian groups; short zero sums; inverse zero-sum problems

## 1. Introduction

Generalized Davenport constants measure the sequence length required to force
several pairwise disjoint zero sums. Rank-two groups exhibit strong eventual
structure, whereas rank-three groups can depart from the expected arithmetic
progression.

Under the declared inputs below, the values \(D_2=20\) and \(D_3=25\), together
with short-zero-sum thresholds, reduce the next value to

\[
D_4(C_5^3)\in\{30,31\}.
\]

This one-bit ambiguity controls the tail: the lower candidate \(D_4=30\) forces
\(D_k=5k+10\) for every \(k\ge2\). The upper candidate would yield a rigid
length-31 total-zero sequence with no zero sum of length at most five.

We combine the recurrence with symbolic analysis of that hypothetical
obstruction. The purpose is twofold: to obtain a conditional width-one theorem for
the full tail and to identify exactly where existing rank reductions cease to
be automatic. Computation is kept in a separate evidence class.

Our contributions are:

1. the conditional width-one corridor for every \(k\ge4\);
2. the conditional exact tail if \(D_4=30\);
3. an odd-prime saturation-defect lemma excluding multiplicity \(p-2\);
4. bounded computational evidence through support ten;
5. an exact multiplicity parameterization for every remaining support stratum;
6. the rank-forcing phase \(s+c_4\le24\) for the high-multiplicity stratum; and
7. an identity coupling support deficit to internal atom repetition and
   cross-atom overlap.

## 2. Definitions and declared inputs

For a finite abelian group \(G\), \(D_k(G)\) is the least integer \(n\) such
that every sequence of length at least \(n\) over \(G\) contains \(k\) pairwise
disjoint nonempty zero-sum subsequences. Let \(s_{\le\ell}(G)\) denote the least
length forcing a nonempty zero-sum subsequence of length at most \(\ell\). For
an odd prime \(p\), a sequence is *\(p\)-short-free* if it has no nonempty
zero-sum subsequence of length at most \(p\). It is *saturated* relative to
this property if appending any group element destroys it. Thus
*5-short-free* and *saturated* below are the specializations at \(p=5\).

We use the generalized-Davenport recurrence framework [1]

\[
D_{k+1}(G)
\le\max\{D_k(G)+\ell, \ s_{\le\ell}(G)-1\},
\]

and take the lower bound \(D_k(C_5^3)\ge5k+10\) in the range considered here as
an explicit input. The other exact inputs are

\[
D_2=20, \qquad D_3=25, \qquad s_{\le6}=24,
\]

while \(s_{\le5}(C_5^3)=\eta(C_5^3)=33\). We also condition the structural
analysis on the inverse-theorem input that every length-32 5-short-free
sequence has exactly eight support points. These rank-three statements are
explicit hypotheses, not results proved in this manuscript; every corridor
statement below is conditional on them. We also use the published rank-two
value \(\eta(C_5^2)=13\).

## 3. A width-one tail

Taking \(\ell=6\) gives

\[
D_4\le\max\{25+6,24-1\}=31.
\]

Together with the lower bound, this proves
\(D_4\in\{30,31\}\).

**Theorem 1 (conditional corridor).** Under the declared exact inputs, for every \(k\ge4\),

\[
5k+10\le D_k(C_5^3)\le5k+11.
\]

**Proof.** The base case is \(D_4\le31\). Apply the recurrence with
\(\ell=5\) and \(s_{\le5}-1=32\). If \(D_k\le5k+11\), then both terms in the
maximum are at most \(5(k+1)+11\). The declared lower-bound input supplies the lower
line. ∎

**Theorem 2 (conditional tail).** Under the declared exact inputs, if \(D_4(C_5^3)=30\), then

\[
D_k(C_5^3)=5k+10
\qquad(k\ge2).
\]

**Proof.** The statement holds for \(k=2,3,4\). Applying the same recurrence
with \(\ell=5\) propagates the upper bound \(5(k+1)+10\), which matches the
declared lower-bound input. ∎

There is no converse here: the assumption \(D_4=31\) does not by itself prove
that later terms lie on the upper line.

## 4. The hypothetical length-31 obstruction

Assume \(D_4(C_5^3)=31\). The extremal characterization of Freeze and Schmid
provides a total-zero sequence \(S\) of length 31 whose maximum factorization
length is four. If \(M\) is the minimum length of an atom dividing \(S\), their
recurrence gives \(31=D_4\le D_3+M=25+M\), so \(M\ge6\). On the other hand,
\(s_{\le6}(C_5^3)=24\) forces every 31-term sequence to contain a zero-sum
subsequence of length at most six; an inclusion-minimal such subsequence is an
atom. Hence \(M=6\), and \(S\) contains no zero-sum subsequence of length at
most five. Thus the upper candidate yields a sequence satisfying

\[
|S|=31, \qquad \sigma(S)=0,
\]

with no nonempty zero-sum subsequence of length at most five. Every element has
multiplicity at most four. If its support exceeds eight, it is saturated:
otherwise a short-free one-term extension would have length 32, whereas the
declared inverse-theorem input forces every length-32 5-short-free sequence to
have exactly eight support points.

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

For the saturated case \(s\ge9\), Corollary 4 excludes multiplicity three.
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

**Theorem 5 (rank-forcing phase).** For a saturated obstruction with
\(s\ge9\), the high-multiplicity stratum spans rank three whenever

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

## 7. Bounded low-support exclusion

Symbolic reductions combined with two exact state representations exclude
every support size through ten.

**Computational result.** In the supplied exact search model, no length-31
total-zero 5-short-free sequence over \(C_5^3\) exists with support at most ten.

**Exact search description.** Multiplicity at most four first excludes supports
at most seven. At support eight, the only length pattern is \(4^7 3\). Adding
the missing fourth copy of the triple point preserves short-freeness; total sum
then forces that point to equal the negative support sum. After normalizing a
basis by \(\mathrm{GL}(3,5)\), two exact subset-sum representations enumerate
all 564 normalized supports and find none satisfying this condition.

For supports nine and ten, saturation and Corollary 4 exclude multiplicity
three. The support-nine equations leave only \(4^7 2 1\); a canonical search
with the last point forced by total sum visits 6,537,270 states in each of two
independent exact-weight subset-sum engines and finds no solution. At support
ten, the only patterns are \(1^3 4^7\) and \(1,2^3 4^6\). Four
multiplicity-four points must span rank three because 16 terms in a rank-two
subgroup would contradict \(\eta(C_5^2)=13\). Normalizing an independent triple
to the standard basis makes the remaining enumeration complete. The two
engines agree exactly: they visit respectively 210,700 states with 3,558 leaves
and 272,119 states with no leaves, finding zero solutions in both patterns.

Both engines prune a partial candidate exactly when adding a term creates a zero-sum
subsequence of one of the lengths one through five; one stores explicit byte
reachability by weight and group sum, while the other stores translation masks
in a 128-bit representation. Their source, build instructions, expected rows,
and machine-readable results are included as ancillary files. Thus every
support stratum through ten is exhausted within the declared model. Because a
clean-room external replay has not been completed, this result is not used as
theorem authority.

A larger bounded computation found no such sequence through support 22. That
search has not received an external independent replay and is not used in any
proof above or below. Its bounded conclusion is useful for prioritizing the
next case split, but it does not establish support at least 23 as a theorem.

## 8. Atom repetition and overlap

Conditionally suppose that an independently verified extremal-factorization
argument establishes one of the candidate atom-length types

\[
(6,6,6,13)
\qquad\text{or}\qquad
(6,6,7,12).
\]

The identity below then applies; in fact, it holds for every
occurrence-disjoint atom factorization.

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
internal-repetition plus cross-overlap budget of at most \(31-s_0\). The
internally reproduced support-ten computation suggests \(s_0=11\) and hence
budget 20, but that numerical consequence remains computational evidence. If
the bounded support-22 computation is later
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
factorization language, and eventual-linearity context are established results
[1]. The \(C_0\) framework and short-zero-sum localization are also prior work
[2], as are the inverse zero-sum program [3] and rank-two inverse results [4].

The residual contribution is the width-one synthesis for \(C_5^3\), the
saturation-defect specialization, the exact multiplicity grammar, the
rank-forcing phase, and the coupling of support deficit with atom repetition and
overlap. These are structural compression results; they do not decide the final
extremal bit.

## 11. Reproducibility and limitations

The conditional corridor, defect lemma, and support-ten exclusion are separately bound to
exact records. A separate implementation enumerates all multiplicity patterns for
supports 8-31, checks the rank-phase equivalence, reproduces the support-23 and
support-24 tables, and validates the atom identity on independently generated
factorizations. Only the displayed analytic proofs carry all-parameter authority.

The exact value of \(D_4(C_5^3)\) remains open, as does the associated
length-31 extremal-spectrum statement. The support-22 frontier is bounded
computation pending external replay. The rank phase is one-way, and the atom
identity is a compression principle rather than a contradiction. No additional
implementation can substitute for an independently auditable final
obstruction proof.

## 12. Conclusion

Conditional on the declared exact inputs, the generalized Davenport constants
of \(C_5^3\) remain within one unit of the line \(5k+10\) for every \(k\ge4\),
and the lower choice at \(k=4\) would fix the entire tail. The hypothetical upper-line obstruction has substantially more
structure than this corridor alone reveals: its multiplicities have an exact
grammar, its high-multiplicity stratum enters a sharp rank-forcing phase, and
its atom factorization obeys a global repetition-overlap budget.

These results explain where the residual difficulty begins and define a smaller
intersection problem for the unresolved extremal bit. They do not claim to have
resolved it.

## Data and code availability

The verification package contains exact multiplicity enumeration, rank-phase
checks, atom-identity tests, and separately labeled bounded-search records.
These files are distributed in the source archive accompanying this version.

## References

1. M. Freeze and W. A. Schmid, “Remarks on a Generalization of the Davenport
   Constant,” *Discrete Mathematics* **310**, 3373-3389 (2010).
   DOI: 10.1016/j.disc.2010.07.028
2. Y. Fan, W. Gao, G. Wang, Q. Zhong, and J. Zhuang, “On Short Zero-Sum
   Subsequences of Zero-Sum Sequences,” *Electronic Journal of Combinatorics*
   **19**(3), P31 (2012). DOI: 10.37236/2602
3. W. Gao, A. Geroldinger, and W. A. Schmid, “Inverse Zero-Sum Problems,”
   *Acta Arithmetica* **128**, 245-279 (2007).
   DOI: 10.4064/aa128-3-5
4. Q. Zhong, “On the Inverse Problem of the \(k\)-th Davenport Constants for
   Groups of Rank 2,” *Combinatorica* **45**, article 31 (2025).
   DOI: 10.1007/s00493-025-00153-3
