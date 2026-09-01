# The fourth generalized Davenport constant of \(C_5^3\)

**ORION-04 — exact-theorem successor V3**  
**Supersedes for journal science:** `WAVE3_SCOPED_MANUSCRIPT_V2.md`  
**Preserves:** the complete bounded structural argument, all reproducibility
boundaries, and the absence of novelty or editorial authority

## Abstract

We determine the remaining low-index branch in the generalized Davenport
constants of the elementary abelian group \(C_5^3\). The committed symbolic
argument gives
\[
5k+10\le D_k(C_5^3)\le 5k+11\qquad(k\ge4)
\]
and reduces the decision to whether a length-31 total-zero sequence can avoid
every nonempty zero-sum subsequence of length at most five. Saturation restricts
all positive multiplicities of such a sequence to \(1,2,4\). A prior exact
reduction excludes support at most 13. We give an equation-complete cover of
the remaining supports 14--31: 60 multiplicity patterns split into 78 exhaustive
rank/plane branches. Two exact engines with different state representations
agree branch by branch across 156 runs and find no survivor. A non-generating
checker reconstructs the cover, checks the bindings and rejects omitted-branch
and altered-fingerprint controls. An off-host replay with a different compiler
major version and native instruction target reproduces the result digest.
Therefore no length-31 obstruction exists, \(31\in C_0(C_5^3)\), and
\[
D_4(C_5^3)=30.
\]
The committed recurrence then yields \(D_k(C_5^3)=5k+10\) for every \(k\ge2\).
The result is a bounded computer-assisted theorem. The replay is an independent
execution of the same source, not an independent implementation, and the paper
does not claim novelty of the generic zero-sum machinery or editorial authority.

## 1. Problem and theorem

For a finite abelian group \(G\), let \(D_k(G)\) be the least length forcing
\(k\) pairwise disjoint nonempty zero-sum subsequences. The ORION-04 symbolic
chain had already established the one-unit corridor
\[
5k+10\le D_k(C_5^3)\le5k+11\quad(k\ge4)
\]
and the conditional implication
\[
D_4(C_5^3)=30\quad\Longrightarrow\quad
D_k(C_5^3)=5k+10\quad(k\ge2).
\]
It also established \(D_4(C_5^3)\in\{30,31\}\). The sole remaining numerical
question was therefore the existence of a length-31 total-zero sequence with
no zero sum of length one through five.

The present successor closes that question.

> **Theorem 1.** No length-31 total-zero sequence over \(C_5^3\) is free of
> nonempty zero-sum subsequences of lengths one through five. Consequently
> \(31\in C_0(C_5^3)\), \(D_4(C_5^3)=30\), and
> \(D_k(C_5^3)=5k+10\) for every \(k\ge2\).

The proof is computer-assisted but finite and explicitly decomposed below.
Generic recurrence, localization, and zero-sum results used as premises remain
donor mathematics.

## 2. Saturation and the finite grammar

Let \(S\) be a hypothetical obstruction. The inherited saturation theorem
restricts every positive multiplicity to \(1,2,4\). If \(a_1,b_2,c_4\) denote
the numbers of support points having those multiplicities, then
\[
a_1+b_2+c_4=s,
\qquad
a_1+2b_2+4c_4=31.
\]
These two equations generate the outer grammar; no pattern is selected by a
search outcome. The committed parent computation excludes every admissible
candidate with support at most 13. The new cover contains all 42 patterns on
supports 14--22 and all 18 patterns on supports 23--31.

A local projective-line enumeration supplies two further restrictions. Among
the states in \(\{0,1,2,4\}^4\), exactly 21 are free of zero sums of lengths at
most five. It follows that a multiplicity-four point is isolated on its
projective line and that two multiplicity-two points cannot be collinear.
Thus any two high-multiplicity support points are linearly independent.

## 3. Exhaustive rank and plane cover

For supports 14--22, the high-multiplicity subsequence either forces rank three
through the bound \(\eta(C_5^2)=13\), supplies a rank-three basis through four
multiplicity-four points, or falls into the explicit rank-two plane case when
\(c_4=3\). In the last case, two plane points normalize to \(e_1,e_2\), the
third plane direction is enumerated, and a forced point outside the plane
normalizes to \(e_3\). These cases give 51 branches.

For supports 23--31, the high-support set \(H\) is divided by rank. If
\(\operatorname{rank}(H)=3\), basis extension gives one of the profiles
\((2,2,2)\), \((4,2,2)\), or \((4,4,2)\). If its rank is two, all remaining
high points lie in the normalized \(\langle e_1,e_2\rangle\) plane and an
outside singleton normalizes to \(e_3\). If \(|H|=1\), the high point extends
with two singletons; if \(H\) is empty, three singletons form the basis. The
\(\eta(C_5^2)\) inequality removes rank-two branches whenever their high
subsequence is already too long. This gives the remaining 27 branches.

The independent cover checker confirms exactly 60 patterns and 78 branches.
It also rejects a cover with one branch removed. This is the completeness
claim needed by Theorem 1; duplicate orbit representatives may add work but
cannot remove a candidate.

## 4. Exact search and verification

Each engine maintains all group sums reachable at exact weights zero through
five. Adding a point translates the previous exact-weight layers and rejects a
partial sequence immediately if zero becomes reachable. Remaining points of a
fixed multiplicity are enumerated in increasing encoded order. In plane
branches, remaining doubletons are restricted to the normalized plane. Once
all but one nonseed singleton are chosen, the total-zero condition uniquely
forces the last singleton; distinctness, line isolation, canonical order, and
the short-zero exclusion are checked before acceptance.

The primary engine represents each weight layer by a 128-bit mask and uses
coordinate-mask translations. The second engine uses five 25-bit coordinate
planes in AVX2 lanes with independently implemented cyclic shifts. They must
agree on nodes, leaves, solution counts, and every normalized rank-two seed
row—not merely on the final zero.

The frozen replay executes both engines on every branch: 78 branches times two
engines, or 156 exact runs. All processes return cleanly, both representations
agree on every registered fingerprint, and every solution count is zero. The
non-generating verifier checks the source digests, parent binding, cover,
result digest, and authority flags. Re-signed hostile controls that alter a
fingerprint, omit a required branch, or promote a forbidden authority flag are
rejected.

An additional replay ran the same six C sources on a different host using GCC
13.2.0 rather than GCC 14.2.0 and a different `-march=native` target. All 156
runs reproduced the exact result and cover digests. This is an independent
execution and toolchain check of the frozen source. It is not an independent
implementation and is not described as one.

## 5. Proof of the exact value

**Proof of Theorem 1.** Suppose a length-31 total-zero short-zero-free sequence
exists. Saturation puts its multiplicities in \(\{1,2,4\}\), so its support
belongs to the equation-generated grammar. The parent theorem excludes support
at most 13. The checked rank/plane decomposition partitions every remaining
pattern on supports 14--31 into one of the 78 branches. Both exact engines
exhaust every branch and find no solution. Hence the supposed sequence cannot
exist, which is the asserted membership \(31\in C_0(C_5^3)\). Combining this
with \(30\le D_4(C_5^3)\le31\) gives \(D_4(C_5^3)=30\). The previously proved
conditional recurrence implication now applies and gives the stated formula
for every \(k\ge2\). $\square$

## 6. Scope, adverse boundaries, and novelty

The earlier support-at-least-14 theorem remains a valid intermediate result but
is no longer the publication ceiling. The earlier “30 or 31” terminal is
historical and is superseded by Theorem 1.

The current evidence does not establish:

- a new general recurrence or localization theorem;
- novelty of standard Davenport, saturation, or projective-space machinery;
- an independent reimplementation of the exact search;
- external peer review, priority, journal fit, or acceptance;
- an algorithm-independent complexity lower bound.

The literature search found no retrieved source that states this exact value,
but that search is not an exhaustive priority certificate. The manuscript
therefore avoids “first” and “unique” language. A closer source may narrow the
positioning without changing the checked theorem.

## 7. Reproducibility

The exact authority packet is
`evidence/global-obstruction-v1/`. It contains the equation-generated cover,
both engines, independent cover and result checkers, source and result digests,
hostile controls, resource receipts, and the off-host replay receipt. The
machine-verification sequence is:

```text
python generate_cover.py
python independent_checker/check_static.py
python run_replay.py
python independent_checker/check_result.py
```

The source and package manifests bind the reader PDF to that evidence. A
passing package checksum proves byte identity, not mathematical novelty or
editorial acceptance.

## 8. Conclusion

The open one-unit branch for the fourth generalized Davenport constant of
\(C_5^3\) is closed. Saturation converts a hypothetical length-31 obstruction
into a finite multiplicity grammar; the parent theorem excludes supports
through 13; and an exact, independently checked 60-pattern and 78-branch cover
excludes all remaining supports. Thus \(D_4(C_5^3)=30\), and the committed
recurrence gives \(D_k(C_5^3)=5k+10\) for every \(k\ge2\). The claim is exactly
this bounded computer-assisted theorem and no broader novelty or validation
claim.
