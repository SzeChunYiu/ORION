# A One-Unit Generalized-Davenport Corridor and a Rank-Forcing Obstruction Phase in \(C_5^3\)

## Abstract

For a finite abelian group \(G\), the generalized Davenport constant \(D_k(G)\) is the least length that forces \(k\) pairwise disjoint nonempty zero-sum subsequences. We study the unresolved rank-three exponent-five case \(G=C_5^3\). Established recurrence and lower-bound inputs imply the all-\(k\) corridor
\[
5k+10\le D_k(C_5^3)\le 5k+11\qquad(k\ge4),
\]
and the lower line becomes exact for every \(k\ge2\) if the remaining early value satisfies \(D_4(C_5^3)=30\). Thus one unresolved unit at \(k=4\) controls the exact infinite tail.

We sharpen the obstruction structure without claiming that this final unit has been resolved. A hypothetical upper-line extremal yields a length-31 total-zero sequence with no nonempty zero-sum subsequence of length at most five. For saturated exponent-five obstructions, multiplicity three is impossible. Writing \(s\) for support size and \(c_i\) for the number of support points of multiplicity \(i\), every remaining multiplicity pattern satisfies
\[
c_2=31-s-3c_4,\qquad c_1=2s-31+2c_4.
\]
The subsequence supported on multiplicities two and four has length \(62-2s-2c_4\). The donor value \(\eta(C_5^2)=13\) then forces this high-multiplicity stratum to span rank three throughout the exact region \(s+c_4\le24\). We also derive an occurrence-disjoint atom identity showing that internal atom repetition plus cross-atom support overlap equals \(31-s\). Under the conditional four-atom types \((6,6,6,13)\) or \((6,6,7,12)\), any support-at-least-23 extremal therefore has a total repetition/overlap budget at most eight.

The paper separates theorem-grade deductions from bounded computation. The signed parent package establishes support at least eleven. An internal census reports no obstruction through support 22, but its own metadata withholds theorem authority pending the registered external replay. That replay is presently blocked by an explicit fresh one-shot authorization requirement. Consequently \(D_4(C_5^3)\in\{30,31\}\) remains open. The contribution is a rigorous corridor and a structural compression of the residual obstruction, not a claimed solution of the open extremal problem.

## 1. Introduction

Zero-sum theory asks when a sufficiently long sequence over a finite abelian group must contain a subsequence whose sum is zero. Generalized Davenport constants strengthen the question from one zero sum to several pairwise disjoint zero sums. In this setting the first few constants often control eventual arithmetic behavior, so a small unresolved early case can encode a much larger structural problem.

For \(C_5^3\), the registered exact inputs
\[
D_2=20,\qquad D_3=25
\]
combine with the short-zero-sum recurrence to give
\[
D_4(C_5^3)\in\{30,31\}.
\]
This width-one ambiguity is scientifically important for two reasons. First, if the lower value is correct, the entire subsequent sequence is forced onto the lower arithmetic line. Second, the upper value would require a highly constrained length-31 extremal object. The unresolved bit is therefore not merely another table entry: it is an inverse-structure problem.

The natural temptation is to treat a larger computational census as the theorem. We do not. Instead, we ask what can already be proved about any surviving obstruction, which parts of the computational frontier are independently authoritative, and exactly where the current symbolic normalizations stop being automatic.

The answer yields three forms of compression. The first is global: all later generalized Davenport constants lie in a one-unit corridor. The second is local: multiplicity and rank constraints reduce the residual support patterns to an exact phase diagram. The third couples two previously separate descriptions of an extremal sequence—its support grammar and its atom factorization—through a single deficit identity.

These results identify a smaller final obstruction problem while preserving the open status of \(D_4\).

### 1.1 Contributions

The paper makes the following evidence-bounded contributions.

1. **All-\(k\) corridor.** For every \(k\ge4\), \(5k+10\le D_k(C_5^3)\le5k+11\).
2. **Conditional exact tail.** If \(D_4=30\), then \(D_k=5k+10\) for all \(k\ge2\).
3. **Saturation defect.** A general odd-prime saturation argument excludes multiplicity \(p-2\); for \(p=5\), multiplicity three cannot occur.
4. **Exact multiplicity grammar.** Every saturated length-31 obstruction is parameterized by \((s,c_4)\) through explicit formulas for \(c_1\) and \(c_2\).
5. **Rank-forcing phase.** The high-multiplicity stratum must span rank three whenever \(s+c_4\le24\).
6. **Theorem/computation separation.** Support at least eleven is theorem-grade in the signed parent package; support through 22 is retained only as bounded computational evidence.
7. **Atom-overlap budget.** Internal atom repetition plus cross-atom overlap equals \(31-s\), giving a budget of at most eight if the bounded support-23 frontier is accepted.

None of these statements is promoted to the unresolved equality \(D_4=30\) or \(D_4=31\).

## 2. Donor results and problem boundary

We use established generalized-Davenport and short-zero-sum inputs rather than re-owning them. The recurrence has the form
\[
D_{k+1}(G)\le \max\{D_k(G)+\ell,\,s_{\le\ell}(G)-1\},
\]
with the specialized lower framework giving the lower arithmetic line used here. For \(C_5^3\), the registered values include \(D_2=20\), \(D_3=25\), \(s_{\le6}=24\), and \(s_{\le5}=\eta(C_5^3)=33\).

The \(C_0(G)\) framework and the localization of short zero sums are donor-owned. Likewise, rank-two inverse results and the value \(\eta(C_5^2)=13\) are inputs, not contributions of the present paper.

Our residual scientific question is narrower:

> Given the width-one ambiguity at \(D_4(C_5^3)\), what structural conditions are forced on a hypothetical upper-line extremal, and which of those conditions are theorem-grade rather than merely observed in an internal census?

This boundary matters for novelty and for inference. A complete computational enumeration may eventually settle the problem, but until its authority gate is satisfied it cannot silently substitute for a proof.

## 3. The width-one corridor

Using \(\ell=6\),
\[
D_4\le\max\{25+6,24-1\}=31.
\]
The specialized lower bound gives \(D_4\ge30\), hence
\[
D_4\in\{30,31\}.
\]

### Theorem 1 — all-\(k\) corridor

For every \(k\ge4\),
\[
5k+10\le D_k(C_5^3)\le5k+11.
\]

**Proof.** The lower line is the registered donor lower bound. The base upper value is \(D_4\le31\). Apply the recurrence with \(\ell=5\). If \(D_k\le5k+11\), then both recurrence terms are bounded by \(5(k+1)+11\). Induction gives the upper line. \(\square\)

### Theorem 2 — conditional exact tail

If \(D_4(C_5^3)=30\), then
\[
D_k(C_5^3)=5k+10
\]
for all \(k\ge2\).

The proof combines the same recurrence with the matching lower bound. Importantly, the argument does **not** establish an analogous exact upper-line propagation theorem from \(D_4=31\). That converse is not claimed.

## 4. The length-31 obstruction

Assume, conditionally, that the upper value is realized. Standard extremal reduction produces a sequence \(S\) over \(C_5^3\) with
\[
|S|=31,\qquad \sigma(S)=0,
\]
and no nonempty zero-sum subsequence of length at most five.

Since the exponent is five, multiplicities are at most four. The remaining obstruction is highly constrained by saturation.

### Theorem 3 — saturation defect

Let \(p\) be odd and let \(S\) be a saturated \(p\)-short-free sequence over an elementary abelian exponent-\(p\) group. If a nonzero point \(x\) occurs with multiplicity \(m<p\), then there exists a subsequence \(R\), avoiding \(x\), such that
\[
|R|\le p-1-m,
\qquad
\sigma(R)=-(m+1)x.
\]

The argument is simple but load-bearing. A saturation witness obtained after appending another copy of \(x\) must consume every existing copy of \(x\); otherwise an unused copy would yield a forbidden short zero sum already inside \(S\).

### Corollary 4

Multiplicity \(p-2\) is impossible. Therefore in the exponent-five obstruction, multiplicity three does not occur.

This leaves multiplicities one, two and four.

## 5. Exact multiplicity grammar

Let
\[
s=|\operatorname{supp}(S)|,
\]
and let \(c_1,c_2,c_4\) count support points of multiplicities one, two and four. Then
\[
c_1+c_2+c_4=s,
\qquad
c_1+2c_2+4c_4=31.
\]
Solving gives
\[
c_2=31-s-3c_4,
\qquad
c_1=2s-31+2c_4.
\]

Thus every support stratum can be generated exactly from \((s,c_4)\) subject only to nonnegativity. In particular \(c_1\) is odd.

For support 23, the possibilities are
\[
1^{15}2^8,\qquad
1^{17}2^5 4,\qquad
1^{19}2^2 4^2.
\]
For support 24, they are
\[
1^{17}2^7,\qquad
1^{19}2^4 4,\qquad
1^{21}2 4^2.
\]

The value of the parameterization is not cosmetic. It makes the exact boundary of the next rank argument visible.

## 6. The rank-forcing phase

Let \(H\) be the subsequence formed by points of multiplicity two or four. Then
\[
|H|=2c_2+4c_4
=62-2s-2c_4.
\]

If \(H\) were supported inside a subgroup of rank at most two, it would be a 5-short-free sequence over \(C_5^2\). Since \(\eta(C_5^2)=13\), every such sequence of length at least 13 contains a forbidden short zero sum. Because \(|H|\) is even, the contradiction is forced once \(|H|\ge14\).

### Theorem 5 — rank-forcing phase

The high-multiplicity stratum spans rank three whenever
\[
s+c_4\le24.
\]

**Proof.** The inequality \(|H|\ge14\) is equivalent to
\[
62-2s-2c_4\ge14,
\]
which reduces to \(s+c_4\le24\). \(\square\)

The theorem exposes a genuine phase transition in proof reach. At support 23, the \(c_4=0\) and \(c_4=1\) branches are automatically rank three, whereas \(c_4=2\) is the first branch not normalized by this donor threshold. At support 24, only \(c_4=0\) is automatically forced. Beyond this region the theorem is silent; it does not assert that rank three fails.

This distinction prevents a common logical error: failure of a sufficient forcing condition is not evidence for the opposite structural state.

## 7. The theorem-grade support boundary

The signed M2/M3 parent package combines symbolic reductions with independently represented exact states to exclude support at most ten.

### Theorem 6

Any length-31 total-zero 5-short-free sequence over \(C_5^3\), if one exists, has support at least eleven.

A larger internal replay reports no solutions through support 22. That result is useful for designing the final search, but the controlling metadata explicitly records that theorem authority is false and external replay remains required. We therefore use support at least 23 only conditionally when deriving computational-search consequences.

This separation is central to the manuscript. The support-11 statement and the support-23 computational frontier are different kinds of evidence and remain labeled differently everywhere they affect the claim.

## 8. Coupling support and factorization

Under the conditional upper-line extremal, the registered factorization analysis restricts the occurrence-disjoint atom lengths to
\[
(6,6,6,13)
\quad\text{or}\quad
(6,6,7,12).
\]

Let
\[
S=U_1\cdots U_r
\]
be an occurrence-disjoint atom factorization. Define the internal deficit
\[
\delta_i=|U_i|-|\operatorname{supp}(U_i)|
\]
and, for each group element \(g\), let \(r_g\) denote the number of atom supports containing \(g\).

### Theorem 7 — repetition/overlap identity

For every such factorization,
\[
31-s
=
\sum_i\delta_i
+
\sum_{g\in\operatorname{supp}(S)}(r_g-1).
\]

**Proof.** The first sum is
\[
31-\sum_g r_g,
\]
because summing atom-support sizes counts each global support point once for each atom in which it appears. The second sum is
\[
\sum_g r_g-s.
\]
Adding them gives \(31-s\). \(\square\)

If the bounded support-through-22 census is later externally ratified, then \(s\ge23\) and the total budget is at most eight. Thus internal atom repetition and cross-atom support overlap cannot be optimized independently: together they consume a single small deficit budget.

This yields a sharper final search than another unconstrained support row.

## 9. A decisive residual search

A scientifically useful next computation should intersect all currently justified constraints at once:

1. the exact multiplicity pattern;
2. rank-forcing status from Theorem 5;
3. saturation-defect witnesses for every singleton and double point;
4. the conditional atom types;
5. the global repetition/overlap budget;
6. total sum zero;
7. exclusion of every zero sum of length at most five.

A surviving sequence would support \(D_4=31\) only after independent verification of both the sequence and the extremal-factorization conditions. A complete, independently replayed UNSAT certificate would establish the opposite side of the residual obstruction and could close the exact theorem.

The current repository does not yet possess that authority. The registered replay is intentionally fail-closed: a fresh one-shot operator authorization must bind the reviewed successor commit, source-manifest digest, a new nonduplication key, durable job root and shared global registry. Historical keys may not be reused. This is an authority and custody requirement, not a numerical shortfall that can be bypassed by another local run.

## 10. Relation to prior work

Freeze and Schmid provide the generalized-Davenport recurrence, lower-bound framework, extremal language and eventual-linearity context used here. Fan, Gao, Wang, Zhong and Zhuang provide the \(C_0\) formulation and short-zero-sum localization. Gao, Geroldinger and Schmid provide broader inverse zero-sum structure, and later rank-two work sharpens the contrast with the unresolved rank-three setting.

The contribution of this paper is therefore deliberately residual. We do not claim the recurrence, the rank-two thresholds, the \(C_0\) framework or general inverse zero-sum theory. We contribute the exact way those inputs compress this particular width-one obstruction and the proof/authority bookkeeping needed to keep the remaining computation from being overstated.

## 11. Reproducibility and authority

The results fall into three tiers.

**Proof-level results.** The width-one corridor, conditional exact tail, saturation defect, multiplicity grammar, rank-forcing phase and atom-overlap identity are mathematical deductions. Their authority does not depend on the size of a numerical census.

**Signed theorem parent.** The support-at-least-eleven result is bound to the M2/M3 theorem package.

**Bounded computation.** The larger support frontier through 22 is retained as a machine-census result whose own metadata withholds theorem authority. It is guidance until the registered external replay is validly executed and checked.

Internal dual implementations are not described as external replication. Likewise, an operator assertion of externality does not become machine-established identity merely because it appears in a job request.

## 12. Limitations

The limitations are substantive rather than presentational.

1. \(D_4(C_5^3)\) remains either 30 or 31.
2. The exact length-31 \(C_0\) target remains open.
3. The support-through-22 frontier is bounded computational evidence, not a theorem.
4. The rank-forcing theorem is one-way: outside \(s+c_4\le24\), it gives no rank conclusion.
5. The atom-overlap identity compresses the search but does not itself produce a contradiction.
6. The decisive registered replay cannot be self-authorized from the present manuscript-writing lane.
7. Author-side literature review does not substitute for an immediate pre-submission novelty audit.

## 13. Conclusion

The unresolved generalized Davenport problem for \(C_5^3\) has more structure than a single unknown bit suggests. The bit constrains the whole infinite tail; a hypothetical upper-line extremal has an exact multiplicity grammar; a donor rank-two threshold creates a sharp rank-forcing phase; and atom factorization shares one small deficit budget between internal repetition and cross-atom overlap.

These facts turn an opaque support search into a structured residual problem. They do not solve that problem, and the manuscript does not claim otherwise. Its strongest present contribution is a rigorous specialist result that identifies precisely what is proved, what is computationally observed, and what must still be independently authorized and checked before the open extremal theorem can move.

## Selected references

- M. Freeze and W. A. Schmid, *Remarks on a Generalization of the Davenport Constant*, Discrete Mathematics 310 (2010), 3373–3389.
- Y. Fan, W. Gao, G. Wang, Q. Zhong and J. Zhuang, *On Short Zero-Sum Subsequences of Zero-Sum Sequences*, Electronic Journal of Combinatorics 19(3) (2012), P31.
- W. Gao, A. Geroldinger and W. A. Schmid, *Inverse Zero-Sum Problems*, Acta Arithmetica 128 (2007), 245–279.
- Q. Zhong, *On the Inverse Problem of the k-th Davenport Constants for Groups of Rank 2*, Combinatorica 45 (2025), article 31.

## Submission posture

**Bounded paper:** complete manuscript candidate for a specialist combinatorics / computational-combinatorics venue after bibliography, independent proof review, render and final literature closure.

**Maximum top-tier theorem:** not earned. It requires a valid decisive extremal proof or independently authorized complete replay; prose refinement cannot supply that authority.