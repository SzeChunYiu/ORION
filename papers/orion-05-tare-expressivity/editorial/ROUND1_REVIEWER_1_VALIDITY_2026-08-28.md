# Frozen simulated Reviewer 1 report

Date: 2026-08-28  
Status: mutually blind simulated review, not external peer review  
Frozen manuscript PDF digest: `1039ffa55e7ee8858d53bb95cc6250d0aa95fd9982dbf7b4f2622e5ce919e788`  
Frozen anonymous archive digest: `57f08f31c2abbed8b66fd3bce9aba8a078aac55c1148e17671dd460049fbfb5c`

## Recommendation

**Major revision**, despite a conditionally sound core theorem.

The archive's internal integrity list verified. Both packaged checks passed:

- the proof-sanity check exhausted 192 correction cases, found maximum increase 2, and found no subset-lemma failure for support 3 through 8;
- the sharpness check returned support-two cost 5 and exhaustive support-one cost 6, with every reported witness check true.

All seven PDF pages rendered without visible clipping, overlap, or broken mathematical notation.

## Validity assessment

### Analytic proof

No counterexample was found to the core support-two theorem, conditional on the objective implemented in the archive.

- The correction-exchange lemma is valid. Changing one correction letter can add at most one ordinary support unit. Destroying the sharing discount adds two but cannot simultaneously increase ordinary support.
- The zero-sum-subset lemma is valid. In $\mathbb F_2^2$, a zero class gives a singleton, repetition gives a zero-sum pair, and three distinct nonzero classes sum to zero, contradicting odd first-component parity.
- The theorem follows. Removing the selected proper subset preserves partner anticommutation and the shared syndrome, keeps the frame nonidentity, and exchanges a refund of at least 2 per removed coordinate against an increase of at most 2. Total frame support strictly decreases, so termination is well founded.

### Exact counterexample

The displayed support-two witness checks directly.

- $(YI,XI)$, $(YI,XI)$, and $(ZX,IY)$ are anticommuting pairs.
- $S=XI$ gives common syndrome $(1,0)$.
- The corrections are three copies of $ZI$ on one branch and identities on the other, hence correction cost 1.
- Under the code-implied normalized frame objective, frame cost is 2 and shared-operator cost is 2, totalling 5.
- The packaged exhaustive support-one search returns 6 over 12 ordered support-one pairs per block, their Cartesian cube, four relative target orders, both syndrome orientations, and the optimized remaining constant choices.

### Complexity upper bound

The counting and inference are sound.

- A weight-one first frame has $6n-4$ eligible partners.
- A weight-two first frame has $12n-16$ eligible partners.
- Thus $N_{\mathrm{pair}}=54n^3-108n^2+60n$.
- Three pair choices cost $N_{\mathrm{pair}}^3=O(n^9)$.
- Their active union has at most nine coordinates, making the 64-syndrome shared-operator dynamic program constant-size after an $O(n)$ target scan.
- The claimed $O(n^3)$ memory bound is consistent with storing the pair universe and target preprocessing.

This is correctly described as an upper bound, not a speed or optimal-exponent claim.

### Adverse runtime result

The interpretation is appropriately conservative: all six direct-solver full-subject cells timed out, and the paper claims no runtime or memory improvement. The negative result is not suppressed. Its underlying evidence was aggregate-only in the frozen archive, which motivates Concern O5-R1-MAJ-03.

## Stable concerns and resolution tests

### O5-R1-MAJ-01 — Declared grammar and objective are not fully specified

**Severity:** Major

The manuscript gives frame-cost refunds but not the complete normalized formula. The archive code uses

\[
C_{\rm frame}=\sum_b m_{b0}(w(A_{b0})-1)+m_{b1}(w(A_{b1})-1),
\]

with multipliers $(2,4)$ or $(4,2)$, described as raw cost minus 18. This normalization is necessary to reproduce absolute costs 5 and 6. Likewise, the phrase "same two nonzero symplectic labels" conflicts with allowed syndromes $(1,0)$ and $(0,1)$.

**Resolution test:** Add a complete mathematical definition of the admitted family, exact frame-cost formula and normalization, allowed syndrome set, target-to-branch mapping, and all nonidentity conditions. A reader using only those equations must recompute the displayed witness components $2+2+1=5$ and obtain the same feasible set as the direct solver.

### O5-R1-MAJ-02 — Exact-comparison claims are summary-only

**Severity:** Major

The frozen archive reports extensive comparison against a separate exact referee, but the referee, runner, test-case generator, commands, and detailed receipts are absent. The summary cannot be regenerated from the archive.

**Resolution test:** Either include a clean, genuinely separate referee and one documented regeneration command, or remove the separate-referee claims from the reader-facing paper and review archive.

### O5-R1-MAJ-03 — Runtime study is not reproducible or independently auditable

**Severity:** Major

The frozen archive contains only an aggregate. It omits the pre-measurement specification, 120 attempt rows, subject definitions, commands, environment, per-row measurements, timeout records, and deterministic aggregation.

**Resolution test:** Include a sanitized frozen specification and row-level table with exactly 120 attempts, 108 completions, 12 timeouts, and the six direct full-subject timeouts. Include the available commands, environment, subjects, limits, and success rule. An aggregation script run only on those rows must reproduce the adverse summary, including null direct medians and ratios and a false positive-performance decision. If the complete measurement stack is not included, state that the archive supports row audit rather than a new timing campaign.

### O5-R1-MIN-01 — Exhaustiveness reductions should be explicit

**Severity:** Minor

The manuscript says the sharpness search covers all central choices and every compatible shared operator, while the packaged solver applies analytic reductions.

**Resolution test:** State and prove that global branch-swap symmetry reduces eight target orders to four, the heavier frame independently receives multiplier 2, and a minimum-weight compatible shared operator suffices because no other objective term depends on it.

### O5-R1-MIN-02 — Align the abstract with the theorem statement

**Severity:** Minor

The abstract claims a cost-nonincreasing transformation, whereas the theorem states only optimum equality. The proof supports the stronger statement.

**Resolution test:** State the transformation theorem formally and make optimum equality its corollary, or weaken the abstract.

## Overall conclusion

The mathematical normal-form argument, exact witness mechanism, and $O(n^9)$ upper bound appear valid under the implemented grammar. Publication should nevertheless await a self-contained objective and replayable evidence or appropriately narrowed implementation claims. This is simulated review, not external validation.
