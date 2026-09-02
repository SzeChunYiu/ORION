# The fourth generalized Davenport constant of \(C_5^3\)

**ORION-04 — exact-theorem successor V4**  
**Supersedes for journal science:** `WAVE3_SCOPED_MANUSCRIPT_V3.md`  
**Preserves:** the exact theorem, adverse boundaries, historical evidence, and all distinctions between local verification and external peer review.

## Abstract

We determine the fourth generalized Davenport constant of the elementary abelian group \(C_5^3\). The committed symbolic argument reduces the remaining case to the nonexistence of a length-31 total-zero sequence with no nonempty zero-sum subsequence of length at most five. Saturation restricts positive multiplicities to \(1,2,4\). The admissible outer grammar contains 60 multiplicity patterns; a rank/plane decomposition yields 78 exhaustive branches. Two exact engines execute 156 registered runs and find zero survivors. A separately implemented Python/DP reconstruction independently regenerates the 60-pattern/78-branch cover without importing the production branch list or C search engines, and hostile mutations of the multiplicity equation, rank split, branch count, and result binding are rejected. Independent solver calibration and route-disagreement controls further test the primitive zero-sum predicate without consuming the protected target computation as authority. Therefore no length-31 obstruction exists, \(31\in C_0(C_5^3)\), and
\[
D_4(C_5^3)=30.
\]
The committed recurrence then yields \(D_k(C_5^3)=5k+10\) for every \(k\ge2\). A submission-date priority audit found no retrieved source already establishing this exact value; accordingly the paper claims the exact theorem but avoids absolute “first” language. External human proof review, externally checked per-branch certificates, and final custody/sign-off remain deferred to journal review or later independent validation and are not represented as locally earned authority.

## 1. Problem and theorem

For a finite abelian group \(G\), let \(D_k(G)\) be the least length forcing \(k\) pairwise disjoint nonempty zero-sum subsequences. Earlier ORION-04 work established
\[
5k+10\le D_k(C_5^3)\le 5k+11\qquad(k\ge4),
\]
with the conditional implication
\[
D_4(C_5^3)=30\Longrightarrow D_k(C_5^3)=5k+10\qquad(k\ge2).
\]
Thus the unresolved numerical question was whether a length-31 total-zero sequence could avoid every zero-sum subsequence of lengths one through five.

> **Theorem 1.** No length-31 total-zero sequence over \(C_5^3\) is free of nonempty zero-sum subsequences of lengths one through five. Consequently \(31\in C_0(C_5^3)\), \(D_4(C_5^3)=30\), and \(D_k(C_5^3)=5k+10\) for every \(k\ge2\).

The proof is finite and computer-assisted. Generic recurrence, localization, saturation, and projective-space results used as premises remain donor mathematics.

## 2. Finite grammar and branch cover

Let \(S\) be a hypothetical obstruction. Saturation restricts every positive multiplicity to \(1,2,4\). If \(a_1,b_2,c_4\) count support points of those multiplicities, then
\[
a_1+b_2+c_4=s,\qquad a_1+2b_2+4c_4=31.
\]
These equations generate 60 admissible multiplicity patterns. Prior exact work excludes support at most 13. The remaining supports 14--31 are covered by a rank/plane decomposition with 51 lower-support branches and 27 upper-support branches.

For supports 14--22, the high-multiplicity subsequence either forces rank three through the \(\eta(C_5^2)=13\) bound, supplies a rank-three basis through four multiplicity-four points, or enters an explicit rank-two plane case when \(c_4=3\). For supports 23--31, the high-support set is partitioned by rank and multiplicity profile; normalized bases and the same \(\eta(C_5^2)\) restriction remove impossible rank-two cases. The resulting cover contains exactly 78 branches.

## 3. Exact search

The frozen target computation uses two exact engines with different state representations. Each tracks all group sums reachable at exact weights zero through five and rejects a partial sequence as soon as zero becomes reachable in a forbidden weight layer. Across 78 branches and two engines, 156 registered runs complete with agreement on the frozen branch fingerprints and zero solution count in every branch.

An off-host replay using the same committed source but a different compiler major version and native instruction target reproduces the exact result and cover digests. This replay is an independent execution of the same source; it is not used as the independent implementation claim.

## 4. Independent reconstruction and adversarial verification

The independent A1 reconstruction does not import the production branch list, the production C engines, current fingerprints, or generator output. Starting from the multiplicity equations and rank/plane lemmas, it independently regenerates:

- the 60 admissible multiplicity patterns;
- the projective-line admissibility structure;
- the 51 lower-support branches;
- the 27 upper-support branches;
- the exact 78-branch partition.

Only after reconstruction is the independently generated tuple set compared with the committed production cover. The comparison is exact: no missing and no extra branches.

The independent route uses a materially different Python/DP representation rather than a line-by-line translation of the production C search. Additional Z3/SMT calibration tests the primitive disjoint-zero-sum predicate on frozen published small-group controls and agrees with separately implemented brute-force occurrence assignment on exhaustive small domains. Route-disagreement controls require unanimity among distinct routes and terminate adversely or `CANNOT_CHECK` rather than using majority vote when routes disagree or disappear.

Hostile controls reject, among others, an omitted branch, an altered total-length equation, a deleted or modified rank split, an altered eta threshold, a forged zero-solution digest, and a checksum-consistent forged nonzero-survivor result. These controls test that acceptance depends on mathematical and semantic content rather than only on file identity.

## 5. Proof of Theorem 1

Assume a length-31 total-zero short-zero-free sequence exists. Saturation forces its positive multiplicities into \(\{1,2,4\}\), hence its support belongs to the 60-pattern equation-generated grammar. Prior work excludes support at most 13. The independently reconstructed rank/plane decomposition covers every remaining admissible support pattern by one of the 78 branches. The frozen exact computation exhausts every branch using two representations and records zero survivors in all 156 runs. Therefore the assumed obstruction does not exist. Hence \(31\in C_0(C_5^3)\). Combined with the previously established corridor, this gives \(D_4(C_5^3)=30\); the committed recurrence then yields \(D_k(C_5^3)=5k+10\) for every \(k\ge2\). \(\square\)

## 6. Priority and novelty scope

A dedicated priority audit searched the closest generalized/multiwise Davenport-constant literature and found no retrieved source that already establishes the exact value \(D_4(C_5^3)=30\). This closes the local literature-audit task but is not an omniscient global priority certificate. The manuscript therefore states the exact theorem and its relation to the closest retrieved work while avoiding absolute “first”, “unique”, or equivalent language.

The paper does not claim novelty of generic Davenport machinery, saturation, projective-space methods, recurrence arguments, or exact-search methodology in the abstract. The contribution claimed here is the exact bounded theorem, its finite branch reduction, and the independently reconstructed verification path for this instance.

## 7. External-review boundary

The following items remain intentionally external and are **not** represented as locally completed:

1. a signed independent mathematical proof review by a person outside the authoring process;
2. externally checked per-branch certificate and output manifests;
3. final independent custody/authorization receipts where a venue or archive requires them;
4. journal peer review and editorial acceptance.

These items are deferred to journal review or later independent validation. Their absence does not erase the locally established theorem or block completion of the local submission package, but it does block any claim that external peer review, external custody, or independent human proof validation has already occurred.

## 8. Reproducibility and evidence map

The exact authority packet is `evidence/global-obstruction-v1/`. Independent reconstruction material is in `evidence/a1-independent-branch-audit-v1/`. The archive-readiness machinery is in `evidence/a1-theorem-packet-archive-v1/`. The latter is designed to fail closed when external review/custody receipts are absent; that fail-closed status is preserved rather than bypassed.

The local submission posture is therefore:

- exact theorem: established by the committed finite computation and proof chain;
- independent implementation/reconstruction: locally complete;
- mutation/adversarial controls: locally complete;
- priority audit: locally complete, with absolute priority language withheld;
- external human proof review/custody: deferred and explicitly unclaimed;
- editorial acceptance: unclaimed.

## 9. Conclusion

The remaining one-unit branch for the fourth generalized Davenport constant of \(C_5^3\) is closed: \(D_4(C_5^3)=30\). The committed recurrence then gives \(D_k(C_5^3)=5k+10\) for every \(k\ge2\). The result is supported by an exhaustive 60-pattern/78-branch reduction, two exact target-search representations, an independently regenerated Python/DP cover, solver calibration, off-host replay, and hostile semantic controls. The paper is locally ready for submission-package completion. External human proof audit, external certificate checking, and journal review remain visible deferred validation rather than artificial blockers on local completion.
