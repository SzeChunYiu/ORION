# ORION-02 mock peer review V2

**Subject:** `MANUSCRIPT_V2.md`  
**Mode:** three mutually blind reports + post-review editor synthesis.  
**Authority:** internal adversarial review only.

---

# Reviewer 1 — Scientific method / research workflow

## Major R1.1 — define the successor-license rule more formally

The manuscript has a compelling narrative but the central object—what a predecessor disposition is allowed to license—remains partly procedural prose.

**Repair:** add a transition schema:

`SuccessorAllowed(P,S) := predecessor_terminal_bound ∧ responsibility_supported ∧ donor_first_refusal_recorded ∧ S.protocol_frozen_after(P.result) ∧ S.outcome_unread_at_freeze ∧ predecessor_bytes_immutable`.

Not every field needs to be executable today, but the paper should state which invariants the repository checker can verify automatically versus which require scientific judgment.

**Severity:** ORION-11 methodological formalization.

## Major R1.2 — define eligibility for representative chains

The paper says it reconstructs representative chains. Without a total inventory or selection rule, a reviewer can suspect survivorship/cherry-picking.

**Repair:** enumerate all eligible negative/donor/CANNOT_CHECK successor chains at the publication cut, then state a deterministic rule for which enter main text (e.g. one per terminal/transition class, all central R6 chain transitions) and put the rest in supplement.

**Severity:** ORION-11 reporting blocker.

## Decision

Promising methods paper after formalization; no new experiment.

---

# Reviewer 2 — Autonomous-science / novelty

## Major R2.1 — ScientistOne materially narrows the abstract novelty sentence

The manuscript now credits Chain-of-Evidence, but “negative-result recovery” can still sound like provenance plus preregistration. The final literature review must search adaptive/preregistered experimental design, workflow systems that branch on failed experiments, truth-maintenance/CEGAR-style counterexample-guided refinement, and negative-results infrastructure.

**Repair:** create an exact donor matrix with columns:
- evidence traceability;
- immutable negative history;
- failure responsibility;
- donor first refusal;
- successor freeze after predecessor result;
- counterexample-guided model/family refinement;
- authority separation.

The residual must survive the matrix, not a keyword search.

**Severity:** ORION-11 novelty gate.

## Major R2.2 — avoid claiming scientific “monotonicity” in a way that conflicts with belief revision

The phrase “monotone scientific history” is intuitive but can be misunderstood as monotone beliefs/knowledge. What is monotone is **the audit log / retained disposition history**, not scientific belief truth.

**Severity:** ORION-11 terminology.

## Decision

Novelty plausible but not closed.

---

# Reviewer 3 — Reproducibility / quantum-domain overlap

## Major R3.1 — case-study numbers should be minimized and linked to companions

The manuscript mostly succeeds, but the TARE chain still risks becoming a duplicate ORION-01/QG summary. Use the smallest quantitative detail needed to prove that each transition is real, then cite the companion evidence ledger.

**Repair:** main-text transition table; move detailed witness costs/configuration counts to companion citations/supplement.

**Severity:** ORION-11 overlap/editorial.

## Major R3.2 — receipt index needs a machine-checkable transition graph

A human-readable `RECEIPT_INDEX` is good, but the methodological claim is much stronger if the publication package ships a small JSON/CSV graph whose nodes are protocol/result/disposition artifacts and whose edges encode `successor_of`, `donor_absorbs`, `refutes`, `strengthens_scope`.

**Severity:** ORION-11 reproducibility/package.

## Decision

Revision required, no new science.

---

# Editor synthesis

## Shared conclusion

All reviewers agree ORION-02 is scientifically viable as a methodology/case-study paper, but **external novelty is not yet closed** and the successor relation needs a more formal/auditable representation.

## Minimum-sufficient repairs

1. Formalize `SuccessorAllowed` and mark machine-checkable vs judgment-dependent fields.
2. Build total eligible-transition inventory and deterministic main-text selection rule.
3. Build donor matrix against CoE/preregistration/adaptive experimentation/truth-maintenance/counterexample-guided refinement.
4. Replace “monotone scientific history” with “append-only/immutable disposition history” or define the phrase precisely.
5. Compress ORION-01/QG mathematics to transition evidence only.
6. Create machine-readable transition graph and bind the human receipt index to it.

## Editorial disposition

`REVISION_REQUIRED__METHOD_OBJECT_SURVIVES__EXTERNAL_NOVELTY_NOT_YET_CLOSED`