# Q1 mock peer review V2

**Subject:** `MANUSCRIPT_V2.md`  
**Method:** three mutually blind reviews, then post-review editor synthesis.  
**Authority:** internal adversarial review only.

---

# Reviewer 1 — Quantum algorithms / compilation theory

## Major R1.1 — theorem statement is now the right headline, but the objective must travel with it everywhere

The manuscript correctly promotes R6S and demotes the two-trade taxonomy. However, “support two is an exact all-`n` ceiling” can still escape its qualifier in captions, title fragments and discussion sentences.

**Repair:** define a short canonical scope label (e.g. `R6M/raw-support`) and attach it to every theorem-level summary/caption. The abstract already states the frozen objective; maintain that discipline in figures/tables.

**Severity:** P1 framing, no new science.

## Major R1.2 — prove the reader can distinguish support ceiling from Tag support / family cardinality

“Frame support ≤2” could be misread as Tag weight ≤2 or as a bound on number of active blocks. Add one explicit statement defining the support measure used by the theorem and what it does not bound.

**Severity:** P1 clarity/formal definition.

## Minor R1.3 — chemistry

Keep chemistry as validation late in the paper. The theorem does not need chemistry evidence; moving chemistry too early weakens the mathematical spine.

## Decision

Strong theory paper after scope/notation tightening.

---

# Reviewer 2 — Formal methods / exact algorithms

## Major R2.1 — machine-checked theorem needs a compact proof obligation table

The text summarizes the R6S proof, but a skeptical referee needs to know which steps are mathematical arguments and which are exhaustively checked finite lemmas.

**Repair:** include a theorem-proof table:
- parity/class lemma: written combinatorial argument + finite corroboration boundary;
- Lemma E: complete 18,432-case check;
- induction measure/descent: mathematical step;
- D++ equality: dependence on registered Tag-relaxation identity.

Do not call a computationally checked finite lemma a proof for arbitrary `n` unless the all-`n` reduction is explicit.

**Severity:** P1 proof-audit blocker.

## Major R2.2 — independent verifier/referee chain should be visible

Add a reproducibility map showing primary exact DP, brute-force bindings, R6S analyzer/protocol, and any independent generic verification used by the companion boundary results. This makes the “exact counterexample” phrase auditable.

**Severity:** P1 package blocker.

## Decision

Revision required; no new proof requested if the existing proof/check chain is exposed accurately.

---

# Reviewer 3 — Novelty / journal editor

## Major R3.1 — current title avoids the stale two-trade overclaim; keep QG1 overlap controlled

The manuscript uses later QG5/QG7 only to delimit Q1, which is appropriate. Do not expand the later trade taxonomy or objective-phase story here. A single compact boundary subsection is enough.

**Severity:** overlap guard.

## Major R3.2 — nearest-work claim still needs full-text cards

The paper credits TARE but the final novelty residual has not yet been stress-tested against exact synthesis/Pauli compiler characterization, compiler-support bounds, or algorithm-selection/instance-space analogues. The submission novelty sentence should remain provisional.

**Repair:** deep cards for TARE plus 3–5 strongest exact/structural compiler analogues; classify `ADOPT/NOT_SUBSTITUTE/CLOSES_CLAIM` against the exact residual.

**Severity:** P1 pre-submission novelty gate.

## Minor R3.3 — contribution class

Sell this as **theory + exact counterexamples**, not a performance paper. Avoid benchmark vocabulary around 9,771/15 unless immediately labeled finite/prospective validation.

## Decision

Potentially strong publishable theory result; novelty finalization pending literature closure.

---

# Editor synthesis

## Shared conclusion

All reviewers agree the old scientific problem is repaired: Q1 no longer relies on an obsolete two-trade-completeness story. The current all-`n` support theorem is a coherent publication spine. No reviewer requests another scientific experiment or new theorem.

## Minimum-sufficient repair set

1. Canonical theorem scope label in every theorem-level summary/figure.
2. Explicitly define **frame support** and distinguish it from Tag weight/number of blocks.
3. Add proof-obligation table separating all-`n` reasoning from finite exhaustive checks.
4. Add exact-referee/replay/independent-verification map.
5. Keep QG later-regime material compact and boundary-only.
6. Complete deep nearest-work cards before freezing external novelty language.

## Editorial disposition

`REVISION_REQUIRED__ALL_N_THEORY_SPINE_ACCEPTED__NOVELTY_SEARCH_PENDING`