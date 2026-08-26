# ORION-09 mock peer review V2

**Subject:** `MANUSCRIPT_V2.md`  
**Mode:** three mutually blind reports + editor synthesis.  
**Authority:** internal adversarial review only.

---

# Reviewer 1 — Quantum compiler / algorithms

## Major R1.1 — the “field” language is plausible but must not outrun three families

The manuscript appropriately says three families are not universal. Still, phrases such as “field claim” risk sounding like a broad established taxonomy.

**Repair:** use “regime-geometry framework/template” throughout the first submission. Reserve “field” for Discussion as a proposed research direction, not an empirical fact.

**Severity:** ORION-11 framing.

## Major R1.2 — cost/objective normalization across families

The cross-family table compares families with different frozen structural objectives. A reader may wrongly compare raw costs/trade counts across them.

**Repair:** explicitly state that cross-family synthesis compares **authority/structural phenomena**, not numerical cost magnitudes. No cross-family normalized performance score should appear.

**Severity:** ORION-11 interpretation guard.

## Decision

Strong synthesis after scope language tightening.

---

# Reviewer 2 — Algorithm selection / Instance Space Analysis

## Major R2.1 — ISA is not just “related work”; it is the closest conceptual parent

The manuscript acknowledges ISA well. It should go one step further and organize a comparison table:

| Dimension | ISA / algorithm selection | QG regime geometry |
| instance features | yes | optional/frozen vocabulary |
| performance footprints | central | secondary |
| exact feasible-family containments | generally no | central where available |
| exact trade witnesses | not required | central |
| theorem-grade global bounds | not required | central where available |
| representation non-identifiability test | can study feature sufficiency, but QG uses exact mixed-cell label contradiction | central QG15b result |
| prospective refutation | compatible | mandatory in registered QG lanes |

Do not imply ISA cannot produce interpretable or exact insights; claim only the additional compiler-mechanism obligations QG imposes.

**Severity:** ORION-11 novelty-positioning blocker.

## Major R2.2 — “mixed cells = information-theoretic” wording

Within the **frozen feature vocabulary**, identical vectors with opposite labels give an irreducible classification error. Calling this “information-theoretic” is acceptable only with that qualifier; it is not a lower bound against all representations.

**Severity:** ORION-11 wording.

## Decision

Novelty survives if ISA is treated as parent rather than distant cousin.

---

# Reviewer 3 — Formal evidence / reproducibility

## Major R3.1 — authority matrix needs exact artifact pointers

The cross-family table is conceptually strong but not audit-ready. Every cell should point to the exact theorem/receipt/prospective result and label its authority class.

**Repair:** generate a machine-readable or Markdown `CROSS_FAMILY_EVIDENCE_MATRIX_V2` from the claim ledgers/wave records and use it as the source for the table/figures.

**Severity:** ORION-11 reproducibility blocker.

## Major R3.2 — publication cut must visibly exclude open stacked QG theorem branches

The manuscript mentions open work but a referee inspecting GitHub will see live QG-9/QG-16/QG-17 branches/PRs. State that they are **not part of this evidence cut**, and why: otherwise the submission appears selectively stale.

**Severity:** ORION-11 provenance/authority.

## Minor R3.3 — prospective failures

For QG15, report the stage-1 prediction digest/freeze identity in supplement/evidence table so the refutation cannot be mistaken for retrospective error analysis.

## Decision

Revision required, no new experiment.

---

# Editor synthesis

## Common conclusion

The manuscript's most publishable result is the negative cross-family finding: **the regime-analysis template transfers while simple/feature-determined boundaries do not.** No reviewer requests another family before submission.

## Minimum-sufficient repair set

1. Replace broad “new field” language with “framework/template” in title/abstract/main claims; frame field-building as Discussion proposal.
2. Explicitly forbid numerical cost comparison across families with different objectives.
3. Add a structured ISA-vs-QG comparison table and treat ISA as the primary conceptual parent.
4. Qualify StabPrep mixed-cell result as non-identifiability **within the frozen feature vocabulary/domain**.
5. Create `CROSS_FAMILY_EVIDENCE_MATRIX_V2` with exact artifact pointers and authority types.
6. Add explicit publication-cut exclusion of open/unmerged successor branches.
7. Bind prospective-refutation digest/protocol identities in the supplement/evidence matrix.

## Editorial disposition

`REVISION_REQUIRED__CROSS_FAMILY_RESULT_SURVIVES__NO_NEW_FAMILY_REQUIRED`