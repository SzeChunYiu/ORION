# A One-Unit Generalized-Davenport Corridor and a Certified Low-Support Exclusion in \(C_5^3\)

**Canonical Wave-3 bounded manuscript, ORION-04**  
**Scientific terminal:** `ORION04_EXACT_D4_NOT_ESTABLISHED__PAPER_REFRAMED_TO_BOUNDED_STRUCTURAL_RESULT`  
**Subject repository state:** `e5dd6f1685eabd78e2f427c7a8665f619b4416b4`

## Abstract

For a finite abelian group \(G\), let \(D_k(G)\) be the least length that forces \(k\) pairwise disjoint nonempty zero-sum subsequences. For \(G=C_5^3\), known early constants and donor recurrences confine every later value to a one-unit corridor,
\[
5k+10\le D_k(C_5^3)\le 5k+11\qquad(k\ge4).
\]
If \(D_4(C_5^3)=30\), the lower line is exact for every \(k\ge2\). The unresolved upper-line alternative produces a length-31 total-zero sequence with no nonempty zero-sum subsequence of length at most five.

We study that finite obstruction without claiming to resolve it. A saturation-defect argument excludes multiplicity three. Exact, content-bound replay in two different state representations excludes every admissible multiplicity/rank branch of support at most thirteen; therefore any obstruction, if one exists, has support at least fourteen. The replay is accompanied by an independently enumerating checker and hostile, re-signed tamper controls. We also derive a complete multiplicity parameterization, a rank-forcing phase \(s+c_4\le24\) for the high-multiplicity stratum, and an atom repetition/overlap identity. These results sharply delimit the remaining support-14-and-higher problem.

A larger internal search reports no solutions through support 22, but its own authority record withholds theorem status pending independent proof/replay. We preserve that boundary. Thus \(D_4(C_5^3)\in\{30,31\}\) remains open. The contribution is a rigorous structural and computer-assisted reduction, not an exact determination of \(D_4\).

## 1. Problem and scope

The generalized Davenport constants interpolate between zero-sum existence and factorization. For a positive integer \(k\), \(D_k(G)\) is the least \(\ell\) such that every sequence of length at least \(\ell\) over \(G\) contains \(k\) pairwise disjoint nonempty zero-sum subsequences.

The rank-three group \(C_5^3\) has a particularly narrow unresolved frontier. The registered exact inputs
\[
D_2(C_5^3)=20,\qquad D_3(C_5^3)=25
\]
and the short-zero-sum thresholds used below imply
\[
D_4(C_5^3)\in\{30,31\}.
\]
This is not merely one missing table entry. The lower value propagates to the whole tail, while the upper value requires a highly constrained length-31 obstruction.

This paper deliberately separates three kinds of statement:

1. **symbolic theorems**, proved from stated donor inputs;
2. **bounded exact computation with theorem authority**, where a complete finite grammar, two exact representations, deterministic receipts, and a non-generating checker are all bound;
3. **internal exploratory computation**, useful for navigation but not promoted to theorem status.

The third category includes the current support-through-22 search. Its negative rows inform the next attack but do not enter the paper's theorem list.

## 2. Donor inputs and the one-unit corridor

We use the generalized-Davenport recurrence and lower-bound framework of Freeze and Schmid. In the notation \(s_{\le \ell}(G)\), the relevant recurrence has the form
\[
D_{k+1}(G)\le \max\{D_k(G)+\ell,\ s_{\le \ell}(G)-1\}.
\]
The registered specialized inputs are
\[
D_2=20,\quad D_3=25,\quad s_{\le6}=24,\quad s_{\le5}=\eta(C_5^3)=33.
\]

### Theorem 1 — width-one tail

For every \(k\ge4\),
\[
5k+10\le D_k(C_5^3)\le5k+11.
\]

**Proof.** With \(\ell=6\), the recurrence gives
\[
D_4\le\max\{25+6,24-1\}=31.
\]
Together with the donor lower bound, \(D_4\in\{30,31\}\). For the induction, use \(\ell=5\) and the fixed threshold \(s_{\le5}-1=32\). If \(D_k\le5k+11\), both recurrence terms are at most \(5(k+1)+11\). The lower line is the registered donor lower bound. \(\square\)

### Theorem 2 — conditional exact tail

If \(D_4(C_5^3)=30\), then
\[
D_k(C_5^3)=5k+10\qquad(k\ge2).
\]

The same recurrence propagates the lower-line value. No corresponding theorem is asserted from the upper alternative \(D_4=31\).

## 3. The finite obstruction

Assume the unresolved upper alternative. Standard extremal localization yields a sequence \(S\) over \(C_5^3\) satisfying
\[
|S|=31,\qquad \sigma(S)=0,
\]
with no nonempty zero-sum subsequence of length at most five. We call such a sequence a **length-31 5-short-free obstruction**.

Every multiplicity is at most four. In the support range relevant after the early reductions, the extension argument is saturated: appending any new point creates a forbidden short zero sum.

### Theorem 3 — saturation defect

Let \(p\) be odd, and let \(S\) be a saturated \(p\)-short-free sequence over an elementary abelian exponent-\(p\) group. If a nonzero point \(x\) has multiplicity \(m<p\), then there is a subsequence \(R\), disjoint from \(x\), such that
\[
|R|\le p-1-m,\qquad \sigma(R)=-(m+1)x.
\]

**Proof.** A short zero-sum witness created by appending a further copy of \(x\) must use every existing copy of \(x\). Otherwise one existing copy can replace the appended copy and produces a forbidden short zero sum already contained in \(S\). Removing the \(m+1\) copies of \(x\) from the witness leaves \(R\) with the stated size and sum. \(\square\)

### Corollary 4 — multiplicity three is absent

Multiplicity \(p-2\) is impossible. In the present case \(p=5\), every multiplicity belongs to
\[
\{1,2,4\}.
\]

Indeed, when \(m=p-2\), the theorem would require a one-term subsequence summing to \(x\), contradicting disjointness from \(x\).

## 4. Complete multiplicity grammar

Let \(s=|\operatorname{supp}(S)|\), and let \(c_1,c_2,c_4\) count support points of multiplicity \(1,2,4\). Then
\[
c_1+c_2+c_4=s,\qquad c_1+2c_2+4c_4=31.
\]
Writing \(c_4=j\) gives
\[
c_2=31-s-3j,\qquad c_1=2s-31+2j.
\]
Nonnegativity therefore enumerates the complete multiplicity grammar at every support size; no pattern is admitted by case guessing.

For example, support 13 has the four patterns
\[
1^1 2^9 4^3,\quad 1^3 2^6 4^4,\quad
1^5 2^3 4^5,\quad 1^7 4^6,
\]
and the first of these requires separate rank-two and rank-three normalization branches. Support 23 has exactly
\[
1^{15}2^8,\qquad 1^{17}2^5 4,\qquad 1^{19}2^2 4^2.
\]

## 5. Certified exclusion through support thirteen

The support-at-most-ten parent packet combines symbolic reductions with independent exact subset-sum state representations. The Wave-3 successor then enumerates the full support-11, support-12, and support-13 grammar prospectively.

The successor contains nine rank-three rows. The pattern
\[
(c_1,c_2,c_4)=(1,9,3)
\]
also has a separately normalized rank-two branch. Each row is replayed by:

- an exact `unsigned __int128` weight-state implementation;
- an exact explicit-byte state implementation.

The representations agree on every registered node, leaf, and solution fingerprint. Every branch has zero solutions. The packet binds source hashes, protocol identity, parent receipt, row grammar, expected terminals, and authority fields. A checker that does not import either generator independently reconstructs the multiplicity patterns and verifies the exact fingerprints. Re-signed hostile mutations of a rank-three fingerprint, rank-two coverage, or an authority flag are rejected.

### Theorem 5 — low-support exclusion

Every length-31 total-zero 5-short-free sequence over \(C_5^3\), if one exists, has support at least fourteen.

**Proof.** The parent theorem excludes support at most ten. The complete successor grammar contains every admissible support-11, support-12, and support-13 multiplicity pattern and both required rank branches. Exact dual-state replay gives no survivor in any branch; the independent checker verifies completeness, fingerprints, and authority boundaries. \(\square\)

The theorem is bounded: it certifies this finite grammar and no larger support range.

## 6. Rank-forcing phase

Let \(H\) be the subsequence formed by all points of multiplicity two or four. Its length is
\[
|H|=2c_2+4c_4=62-2s-2c_4.
\]
If \(H\) were contained in a rank-at-most-two subgroup, it would be a 5-short-free sequence over \(C_5^2\). The donor value \(\eta(C_5^2)=13\) forces a short zero sum once \(|H|\ge13\). Since \(|H|\) is even, the contradiction begins at \(|H|\ge14\).

### Theorem 6 — rank-forcing region

The high-multiplicity stratum spans rank three whenever
\[
s+c_4\le24.
\]

This identifies a real phase boundary. At support 23, the \(c_4=0\) and \(c_4=1\) branches are automatically rank three, whereas the \(c_4=2\) branch is the first branch not normalized by this threshold alone. Outside the region, rank three may still follow from another argument; the theorem only states where this particular donor threshold forces it.

## 7. Four-atom overlap budget

Under the conditional upper-line alternative, extremal factorization arguments reduce to the atom-length types
\[
(6,6,6,13)\quad\text{or}\quad(6,6,7,12).
\]
For an occurrence-disjoint atom factorization \(S=U_1\cdots U_r\), let
\[
\delta_i=|U_i|-|\operatorname{supp}(U_i)|
\]
be internal repetition in atom \(U_i\), and let \(r_g\) count how many atom supports contain \(g\).

### Theorem 7 — repetition/overlap identity

\[
|S|-|\operatorname{supp}(S)|
=\sum_i\delta_i+\sum_{g\in\operatorname{supp}(S)}(r_g-1).
\]

**Proof.** The sum of atom support sizes counts \(g\) exactly \(r_g\) times. Hence
\[
\sum_i\delta_i=|S|-\sum_g r_g,
\]
while the cross-atom overlap count is
\[
\sum_g r_g-|\operatorname{supp}(S)|.
\]
Adding gives the identity. \(\square\)

If a future independent proof promotes support at least 23, then the total internal-repetition plus cross-atom-overlap budget is at most eight. In the present paper this is a conditional compression, not an admitted support-23 theorem.

## 8. What the larger computation does and does not show

The repository also contains an internal exact-search ledger reporting no solutions through support 22. It is valuable because it identifies a plausible frontier and the three support-23 multiplicity patterns. It is not used to prove Theorem 5 or any stronger theorem. Its own metadata states:

- `theorem_authority=false`;
- `external_replay_required=true`.

Accordingly, the statements “support at least 23”, “\(31\in C_0(C_5^3)\)”, and “\(D_4(C_5^3)=30\)” are absent from the admitted claim set.

## 9. Reproducibility and falsification

The theorem-grade Wave-3 packet is located at

`research/orion-rg/wave3/orion04-support11-13-v1/`.

A clean replay:

1. runs `run_replay.py` and byte-compares the generated `RESULT.json`;
2. runs `independent_checker/check_result.py` and byte-compares `GENERIC_RESULT.json`;
3. executes hostile receipt controls;
4. checks that support-14+, support-23, external-replay, \(C_0(31)\), exact-\(D_4\), novelty, venue, and CI authority remain false.

The checker is intentionally non-generating. It reconstructs the multiplicity grammar from the two defining equations and compares exact row fingerprints rather than trusting a producer-supplied success flag.

## 10. Relation to prior work

Freeze and Schmid provide the generalized-Davenport recurrence, lower bounds, and eventual-linearity context. Fan, Gao, Wang, Zhong, and Zhuang provide the \(C_0\) localization framework for short zero sums. The inverse zero-sum literature supplies the broader extremal language. Zhong's rank-two inverse theorem shows the contrast between the resolved rank-two structure and this rank-three frontier.

Our claims after donor subtraction are narrow:

- the registered specialization yielding the one-unit \(C_5^3\) corridor;
- the saturation-defect consequence used here;
- the complete, independently checked support-11-to-13 exclusion;
- the rank-forcing phase and atom overlap budget as structural compression.

We do not claim novelty for the donor recurrence, Property C, \(C_0\), rank-two thresholds, or generic inverse zero-sum theory.

## 11. Limitations

1. \(D_4(C_5^3)\) remains \(30\) or \(31\).
2. \(31\in C_0(C_5^3)\) is not established.
3. No length-31 obstruction is constructed.
4. Support 14 and higher remain open at theorem level.
5. The support-through-22 search remains internal bounded evidence.
6. External independent replay of the Wave-3 finite packet is not recorded.
7. The atom identity compresses a future proof but is not itself a contradiction.
8. This manuscript is positioned for specialist review, not as a completed exact-extremal theorem.

## 12. Conclusion

The unresolved generalized-Davenport value in \(C_5^3\) controls an infinite tail but is constrained by a finite obstruction. We prove a one-unit corridor, a conditional exact lower tail, a saturation defect, and a certified exclusion of every obstruction with support at most thirteen. The remaining object must use at least fourteen support points, multiplicities in \(\{1,2,4\}\), the stated rank phase, and a tightly coupled atom-overlap grammar.

That is a substantial reduction, but the exact extremal bit remains open. Closing the research programme at this bounded terminal is more informative than treating an internally explored support frontier as a theorem.

## References

1. M. Freeze and W. A. Schmid, “Remarks on a Generalization of the Davenport Constant,” *Discrete Mathematics* 310 (2010), 3373–3389; arXiv:0905.4248.
2. Y. Fan, W. Gao, G. Wang, Q. Zhong, and J. Zhuang, “On Short Zero-Sum Subsequences of Zero-Sum Sequences,” *Electronic Journal of Combinatorics* 19(3) (2012), P31, doi:10.37236/2602.
3. W. Gao, A. Geroldinger, and W. A. Schmid, “Inverse Zero-Sum Problems,” *Acta Arithmetica* 128 (2007), 245–279, doi:10.4064/aa128-3-5.
4. Q. Zhong, “On the Inverse Problem of the \(k\)-th Davenport Constants for Groups of Rank 2,” *Combinatorica* 45 (2025), article 31, doi:10.1007/s00493-025-00153-3.

## Data and code availability

All theorem-grade computational artifacts, source identities, exact receipts, independent verification code, hostile tests, and the dedicated GitHub Actions workflow are contained in the public ORION repository. The larger support-through-22 ledger is also public but is explicitly classified as non-theorem internal evidence.
