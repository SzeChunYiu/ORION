# A one-unit generalized-Davenport corridor and a support-at-least-14 theorem in \(C_5^3\)

> **Historical predecessor.** Superseded for current journal science by
> `WAVE3_SCOPED_MANUSCRIPT_V3.md` after the complete global obstruction packet
> earned the exact theorem `D_4(C_5^3)=30`.

**ORION-04 — Wave 3 scientific successor V2**  
**Supersedes for journal science:** `WAVE3_SCOPED_MANUSCRIPT_V1.md`  
**Preserves:** the bounded Wave-3 terminal and all unresolved exact-\(D_4\) boundaries

## Abstract

We study the remaining low-index uncertainty in the generalized Davenport constants of the elementary abelian group \(C_5^3\). The committed symbolic chain gives a one-unit corridor
\[
5k+10\le D_k(C_5^3)\le 5k+11\qquad(k\ge4),
\]
and shows that the lower value at \(D_4\) would force the lower line thereafter. The exact value of \(D_4(C_5^3)\) is not established.

For a hypothetical length-31 total-zero sequence with no nonempty zero-sum subsequence of length at most five, the saturation-defect theorem restricts nonzero multiplicities to \(1,2,4\). A previously committed exact reduction excludes supports at most 10. The Wave-3 M4 computation then exhausts every multiplicity pattern at supports 11, 12 and 13, including the required rank-two branch at support 13. Two exact state representations independently within the repository reproduce the registered fingerprints and return zero solutions, and a separate checker reconstructs the outer multiplicity grammar and rejects re-signed hostile mutations. Combining the parent support-\(\le10\) theorem with the new support-11–13 exclusion proves:

> if such a length-31 obstruction exists, its support is at least 14.

This is a bounded computer-assisted structural theorem. It does not decide whether \(D_4=30\) or \(31\), does not establish \(31\in C_0(C_5^3)\), and does not promote the larger exploratory support-through-22 search. The contribution is the one-unit corridor, the saturation/multiplicity reduction, the exact support-at-least-14 theorem, and its fail-closed replay custody.

## 1. Decision axis

For \(G=C_5^3\), the current programme leaves one unresolved numerical branch rather than a broad asymptotic problem. The paper asks:

1. what later \(D_k\) values are already forced symbolically;
2. what structural restrictions any length-31 upper-line obstruction must satisfy;
3. how far exact finite computation can reduce that obstruction without being mistaken for an exact \(D_4\) solution.

The answer to the third question is **support at least 14**. Exact \(D_4\) remains open.

## 2. Symbolic corridor

### Theorem 1 — one-unit corridor

For every \(k\ge4\),
\[
5k+10\le D_k(C_5^3)\le5k+11.
\]

The general recurrence/localization machinery used in the derivation is donor mathematics. The paper claims the assembled consequence for the registered \(C_5^3\) boundary.

### Theorem 2 — conditional lower-line tail

If
\[
D_4(C_5^3)=30,
\]
then
\[
D_k(C_5^3)=5k+10
\]
for every \(k\ge2\).

### Corollary 3 — exact current interval

The current symbolic evidence gives
\[
D_4(C_5^3)\in\{30,31\}.
\]

Nothing in this paper chooses between those two values.

## 3. Saturation and multiplicity grammar

The finite search is constrained by the committed saturation-defect theorem.

### Theorem 4 — saturation defect

For an odd prime \(p\), let a saturated \(p\)-short-free sequence contain a point \(x\) with multiplicity \(m<p\). Then it has the form
\[
x^mR,
\]
with
\[
|R|\le p-1-m,
\qquad
\sigma(R)=-(m+1)x.
\]

For \(p=5\), multiplicity three is excluded in the registered obstruction grammar. Thus a length-31 candidate uses only multiplicities \(1,2,4\).

Write \(a_1,b_2,c_4\) for the numbers of support points of multiplicity \(1,2,4\). At support size \(s\),
\[
a_1+b_2+c_4=s,
\qquad
a_1+2b_2+4c_4=31.
\]
These equations generate the complete outer multiplicity grammar for the finite replay.

## 4. Exact finite reduction

### 4.1 Parent theorem through support 10

The support-at-least-14 statement has two explicit premises. First, the committed parent reduction already excludes every admissible obstruction of support at most 10. That parent result remains a theorem/evidence dependency of this paper and is not silently re-proved by the Wave-3 M4 run.

Second, M4 handles exactly the previously open supports 11–13.

### 4.2 Complete support-11–13 grammar

The defining equations yield nine registered patterns:

| Support | \((a_1,b_2,c_4)\) | Branches |
|---:|---:|---|
| 11 | \((1,5,5)\) | rank 3 |
| 11 | \((3,2,6)\) | rank 3 |
| 12 | \((1,7,4)\) | rank 3 |
| 12 | \((3,4,5)\) | rank 3 |
| 12 | \((5,1,6)\) | rank 3 |
| 13 | \((1,9,3)\) | rank 3 and rank 2 |
| 13 | \((3,6,4)\) | rank 3 |
| 13 | \((5,3,5)\) | rank 3 |
| 13 | \((7,0,6)\) | rank 3 |

The rank-two branch for \((1,9,3)\) is mandatory. Omitting it would leave a genuine coverage hole.

### 4.3 Two exact state representations

The primary engine stores exact weights in `unsigned __int128`; the corroborating engine stores the same reachability state as explicit bytes. Both use exact arithmetic and deterministic ordering.

For every row they must agree on node, leaf and solution counts. The rank-two branch additionally binds normalized seed candidates, executed and pre-DFS rejected seeds, per-seed fingerprints and aggregate totals.

This is independent implementation structure **within the repository**, not external institutional replication.

### 4.4 Non-generating checker and hostile controls

A separate checker reconstructs the multiplicity list from the two defining equations and verifies source/protocol identities, parent bindings, exact branch fingerprints and authority flags. It does not trust a producer-supplied `all_checks` field.

Re-signed hostile mutations alter scientific content while keeping the outer digest internally consistent. The checker rejects mutations that change a fingerprint, delete required rank-two coverage, or escalate a forbidden theorem-authority flag. These controls show that the validation path checks semantics rather than only file integrity.

## 5. Support-at-least-14 theorem

Every registered support-11, support-12 and support-13 branch returns zero solutions in both exact state representations, with exact agreement on the registered fingerprints.

### Theorem 5 — bounded support exclusion

Let \(S\) be a length-31 sequence over \(C_5^3\) with
\[
\sigma(S)=0
\]
and no nonempty zero-sum subsequence of length at most five. Under the committed parent exclusion through support 10 and the complete M4 exclusion at supports 11–13,
\[
|\operatorname{supp}(S)|\ge14.
\]

**Proof.** The saturation/multiplicity grammar partitions all admissible candidates by support. The parent theorem excludes every support \(\le10\). M4 exhausts the complete multiplicity grammar for supports 11, 12 and 13 and returns no candidate in every required rank branch. Therefore no admissible candidate exists at any support below 14. ∎

The theorem is a computer-assisted finite theorem with explicitly named dependencies. It is not a claim that support 14 itself is attainable.

## 6. Remaining frontier

The larger internal search reporting zero survivors through support 22 remains exploratory because its own authority record withholds theorem promotion. It is retained for search design but does not strengthen Theorem 5.

At support 23, the multiplicity equations give exactly three patterns:

- \(1^{15}2^8\);
- \(1^{17}2^5 4^1\);
- \(1^{19}2^2 4^2\).

These are multiplicity notations: for example \(1^{17}2^5 4^1\) means 17 singleton support points, five doubletons and one quadrupleton. The weights sum to 31 and the support counts sum to 23.

No exploratory failure at this frontier is promoted into theorem authority.

## 7. Explicit nonclaims

This paper does not establish:

- \(31\in C_0(C_5^3)\);
- \(D_4(C_5^3)=30\) or \(31\);
- a support-at-least-23 theorem;
- an explicit upper-line extremal;
- external independent replication;
- novelty of the donor recurrence/localization machinery;
- journal or top-tier authority from finite UNSAT alone.

## 8. Scientific interpretation

Theorem 5 says that any remaining upper-line obstruction must be diffuse: a 31-term candidate with multiplicities restricted to \(1,2,4\) cannot live on thirteen or fewer group elements. This is a meaningful structural reduction even though the final exact Davenport value remains open.

The replay methodology matters only insofar as it supports this bounded theorem: complete outer grammar, two exact inner state representations, deterministic source bindings, a non-generating checker and hostile semantic mutations. Those controls justify the finite exclusion; they do not replace an unresolved global proof.

## 9. Reproducibility

The authoritative M4 packet remains

`research/orion-rg/wave3/orion04-support11-13-v1/`.

The existing deterministic replay, independent checker and dedicated tests remain the reproduction path. General authority of the symbolic corridor and saturation theorem comes from their committed proofs; M4 authority is confined to the finite supports it exhausts.

## 10. Limitations and stop rule

The exact \(D_4\) decision is open. A future successor may close it only with a new prospectively governed proof-producing complete obstruction, an independently verified explicit extremal, or a human-readable theorem ruling out the remaining support.

Do not reopen the present manuscript merely because the support-14+ frontier remains interesting. For journal submission, the bounded theorem is complete at its declared scope.

## 11. Conclusion

The registered mathematics places \(D_k(C_5^3)\) in a one-unit eventual corridor and makes \(D_4\) the decisive low-index branch. Saturation removes multiplicity three from a hypothetical length-31 obstruction. A parent exact reduction excludes supports through 10, and the complete Wave-3 dual replay excludes supports 11–13, proving that any remaining obstruction has support at least 14. Exact \(D_4\) is not established. That bounded structural theorem—and not a stronger unresolved claim—is the scientific submission object.
