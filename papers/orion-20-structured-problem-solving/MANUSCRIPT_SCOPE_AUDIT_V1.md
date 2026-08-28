# ORION-20 manuscript scope audit V1

```text
scientific_authority_delta = NONE
edit_policy                = CLAIM_NARROWING_ONLY__NEVER_RESTATE_MATHEMATICS
sweep_scope                = manuscript/main.tex + manuscript/sections/*.tex (242 lines, 17 files, as of before this pass)
```

Wave-2 (`papers/publication_closure/wave2/WAVE2_DISPOSITION_V1.json`) assigns
ORION-20 the lane `FORMAL_OCME_THEORY_AND_MEASUREMENT_CONTRACT`, with the
donor-complete empirical campaign as
`SEPARATE_SUCCESSOR_DOES_NOT_BLOCK_FORMAL_SUBMISSION`. This audit sweeps the
current manuscript for empirical claims, benchmark results, comparative
performance statements, and any language implying that campaign supports the
headline; then applies claim-narrowing corrections.

---

## 1. Headline finding — there is nothing empirical to delete

Two exhaustive sweeps over all 242 manuscript lines:

| Sweep | Pattern | Hits |
|---|---|---|
| Asserted-result language | `superiority\|achieves\|outperform\|we show\|we demonstrate\|we prove\|results show\|establishes\|beat\|better than\|improves over\|significant` | **10**, in 7 files (§2) |
| Numeric results / benchmark results | `NN%`, multi-digit numbers, `miniF2F`, `EvalPlus`, `SyGuS`, `cvc5`, `Fast Downward`, `p = 0`, `accuracy of` | **0** |

**The manuscript reports no number, no benchmark outcome, and no measured
comparison anywhere.** Every section is either a *specification of a future
test* (imperative voice: "Freeze…", "Measure…", "Compare under matched
budgets…") or a preserved negative. The donor-complete campaign is already
absent from the manuscript rather than wrongly credited in it.

Consequently the default verdict throughout is **REFRAME**, not REMOVE. A
literal REMOVE pass would delete the input contract — which the disposition
explicitly names as part of the current paper — and leave an empty document.

The defect is one of **placement and framing**, not of fabricated evidence:
the title asserts *Superiority*, while the sentence that scopes the whole
document honestly (`16:5`) sits on the final page.

---

## 2. Claim register — every hit, verdict, replacement

| # | File:line | Quoted text | Verdict | Replacement / action |
|---|---|---|---|---|
| C1 | `main.tex:12` | `\title{Verified Structured Problem-Solving Superiority and Obstruction-Certified Method-Language Expansion}` | **REFRAME** | Title must not assert an unmeasured superiority. → `Obstruction-Certified Method-Language Expansion: Formal Closure Theory and an Exact Measurement Contract` |
| C2 | `main.tex:13` | `\author{ORION Paper X Ultimate-Successor Working Manuscript}` | **REFRAME** | Not an author. Placeholder retained but marked; real attribution is a journal-package OPEN item. |
| C3 | `main.tex:20` (abstract, final sentence) | "The intended terminal is replicated verified problem-solving superiority plus at least one independently verified outside-closure method-language expansion…" | **KEEP + SCOPE** | Correctly worded as *intended*. Retain verbatim; add an explicit sentence stating what the paper does and does not establish, so the reader learns the execution status in the abstract, not on the last page. |
| C4 | `main.tex:20` (abstract, opening) | "ORION Paper X therefore targets a claim strictly above those donor mechanisms" | **KEEP** | "targets" is prospective and accurate. No change. |
| C5 | `sections/02-nearest-work-pressure.tex:15` | bold `VERIFIED_PROBLEM_SOLVING_AND_METHOD_SPACE_EXPANSION_SUPERIORITY` | **REFRAME** | Preceded by "The intended terminal remains", so honest in context, but typographically reads as a result. Add `(not established; see Scope and status)`. |
| C6 | `sections/03-immutable-negative-history.tex:9` | "P10-U must beat those stronger explanations in a new regime rather than rewrite old outcomes." | **KEEP** | This is a preserved adverse constraint. Must not be softened. |
| C7 | `sections/11-primary-hypotheses.tex:2,5` | `\paragraph{H1, verified problem-solving superiority.}` / `\paragraph{H2, search-efficiency superiority.}` | **KEEP + SCOPE** | Hypothesis labels inside a section titled "Primary hypotheses". Scoped by the section preamble added below. |
| C8 | `sections/11-primary-hypotheses.tex:3` | "Across heterogeneous verifier-backed tasks, ORION **achieves** higher verified solve/success utility than the strongest runnable donor-complete comparator…" | **REFRAME** | Present indicative reads as a result when quoted out of context. Scoped by an explicit prospective preamble stating all six are `PROSPECTIVE_NOT_EXECUTED`, 0 of 12,960 cells run. |
| C9 | `sections/11-primary-hypotheses.tex:6,9,12,15,18` | H2–H6, same present-indicative pattern | **REFRAME** | Same preamble covers all. |
| C10 | `sections/12-statistics-and-units.tex:2` | "Freeze family weighting, superiority/non-inferiority margins…" | **KEEP** | Specifies a future analysis plan; part of the measurement contract. |
| C11 | `sections/13-framework-consistency.tex:9` | "general method-space expansion superiority" | **KEEP** | Appears inside the list of things ORION does **not** yet have. Removing it would weaken a disclaimer. |
| C12 | `sections/16-claim-ladder-and-status.tex:3` | bold `VERIFIED_…_SUPERIORITY` | **REFRAME** | Same treatment as C5. |
| C13 | `sections/16-claim-ladder-and-status.tex:5` | "This TeX file is a prospective maximum-claim manuscript. It does not alter historical P10/P11 evidence, does not convert pending #618 executions into results…" | **KEEP, PROMOTE** | The single most important honest sentence in the document. Retained here and its substance also placed at the front. |

## 3. Omissions — what the formal lane needs that the manuscript lacks

Not overclaims; gaps against the disposition. Recorded, not silently invented.

| # | Missing | Evidence |
|---|---|---|
| O1 | The five formal objects appear **nowhere** in the tex | *[verified]* `pdftotext manuscript/main.pdf` contains 0 occurrences each of `affine`, `AND2`, `SQUARE`, `decidab`, `minimality`, `donor frontier`, `T1` |
| O2 | Neither OCME study (hand-declared or generated) is in the manuscript | `TOP_TIER_PROMOTION_V1.md` gate box "manuscript/result binding updated to include generated OCME and all surviving negatives" is **unchecked** |
| O3 | No statement of the zero-execution input contract in the front matter | `P10-DES-01/PRIMARY_RESULT_V1.json`: `run_cells_executed = 0` of `12,960` |
| O4 | Theorem statements are defective (see audit F-1, G-2, G-3, G-9, G-12) | [`THEOREM_PROOF_AUDIT_V1.md`](THEOREM_PROOF_AUDIT_V1.md) |

O1–O3 are addressed by the new scope section (§5). **O4 is deliberately not
applied**: correcting a theorem statement is a scientific-authority act, and
this pass carries `scientific_authority_delta: NONE`. The defects are
recorded for the claim authority to act on.

---

## 4. Frozen — listed, not edited

Per the edit policy, none of the following was modified. Where frozen status
was ambiguous, the file was left alone and the reason recorded.

| Path | Why not edited |
|---|---|
| `protocol/` (all) | Prospectively frozen protocol + checker + freeze JSON |
| `evidence/` (all) | Frozen attainability record |
| `top_tier/*RECEIPT*`, `*PROTOCOL*`, `*cases*.json`, `check_*.py`, `run_*.py` | Content-bound receipts and their SHA-256-pinned inputs |
| `CLAIM_EVIDENCE_LEDGER.md` | Ledger |
| `P10_ACTIVE_CLAIM_AUTHORITY_V1.json` | Machine-readable active claim authority |
| `SHA256SUMS`, `CONTENT_MANIFEST_V1.json` | Integrity manifests; invalidation recorded in the journal package status instead of silently regenerated |
| `TOP_TIER_PROMOTION_V1.md` | Promotion-gate record with checked/unchecked boxes; a status record, not a manuscript surface |
| `TOP_TIER_DYNAMIC_EPISTEMIC_MANUSCRIPT_V1.md` | **Ambiguous.** Named a manuscript, but it is the sole carrier of the `ORION-20-T1..T5` statements and of the `P10_FULL_FROZEN_DONOR_EVALUATOR_INPUTS_ABSENT` terminal. Editing it would restate mathematics. **Decision: treat as a claim record, not a manuscript surface; not edited.** |
| `top_tier/P10_OCME_MANUSCRIPT_ADDENDUM_V1.md` | **Ambiguous.** Labelled a manuscript addendum, but hash-bound and structured as a restatement of two receipts under "Canonical authority" pointers. **Decision: treat as receipt-derived, not edited.** Its "finite closures" wording defect (audit G-3) is recorded, not fixed. |
| `successor/P10_U_MANUSCRIPT.tex` / `.pdf` | Predecessor snapshot; the addendum is defined as superseding its outcome layer. Editing it would desynchronise it from its own PDF and from the addendum's reference. Not edited. |

---

## 5. Corrections applied

All are claim-**narrowing**. None adds a result, restates a theorem, or
softens an adverse finding.

| # | File | Change |
|---|---|---|
| E1 | `manuscript/main.tex:12` | Title no longer asserts Superiority (C1) |
| E2 | `manuscript/sections/00-scope-and-status.tex` **(new)** | Front-matter section: what the paper establishes, what it does not, execution status, pointers to the formal receipts and to this audit (O1–O3) |
| E3 | `manuscript/main.tex` | `\input{sections/00-scope-and-status}` inserted immediately after `\maketitle` |
| E4 | `manuscript/main.tex:20` | One scope sentence appended to the abstract (C3) |
| E5 | `manuscript/sections/11-primary-hypotheses.tex` | Prospective preamble: all six are `PROSPECTIVE_NOT_EXECUTED`, 0 of 12,960 cells executed (C8, C9) |
| E6 | `manuscript/sections/02-nearest-work-pressure.tex:15` | "(not established)" qualifier on the bold terminal (C5) |
| E7 | `manuscript/sections/16-claim-ladder-and-status.tex:3` | Same qualifier (C12) |

**Manifest impact.** E1–E7 invalidate these `SHA256SUMS` entries:
`manuscript/main.tex`, `manuscript/sections/02-nearest-work-pressure.tex`,
`manuscript/sections/11-primary-hypotheses.tex`,
`manuscript/sections/16-claim-ladder-and-status.tex`; and the new
`manuscript/sections/00-scope-and-status.tex` is uncovered. Recorded as an
OPEN item with its regeneration command in
[`JOURNAL_PACKAGE_STATUS_V1.md`](JOURNAL_PACKAGE_STATUS_V1.md) rather than
silently regenerated. `manuscript/main.pdf` is now behind its sources.

---

## 6. Preserved-adverse register

Verifiable list of every adverse or `CANNOT_CHECK` finding that must survive
the rewrite. **None was removed, reworded, or softened.** Removing an
empirical claim from the headline must not delete the record that it was
tested and failed.

| Finding | Location | Status after this pass |
|---|---|---|
| `CANNOT_CHECK_NATIVE_STATE_COVERAGE` — 457 files traced, 11,842 candidate transitions, **0** eligible under the frozen contract; explicitly not a timeout | `top_tier/P10_NATIVE_LEAN_CANNOT_CHECK_HANDOFF_V1.md` | untouched |
| 480 `CANNOT_CHECK` rows, 0 of 12,960 planned cells executed, terminal `P10_FULL_FROZEN_DONOR_EVALUATOR_INPUTS_ABSENT` | `research/orion-epistemic-state-v1/results/P10-DES-01/PRIMARY_RESULT_V1.json` | untouched; now also stated in front matter |
| Module negatives (Control −0.033333, CategoryTheory −0.005780) re-attributed to measurement resolution, with the CategoryTheory `calculation` context retained as a genuine localized failure | `top_tier/P10_MODULE_NEGATIVE_REVIVAL_RECEIPT_V1.md` | untouched |
| Four regimes in which **no** invention claim is permitted (exhaustive search matches ORION; representation change suffices; more search closes the case; generated tactic is a macro) | `sections/03-immutable-negative-history.tex:3-8` | untouched |
| "Repository-level integrity is not scientific authority… a perfectly replayed run of a flawed protocol replays the flaw exactly." | `sections/13-framework-consistency.tex:11-19` | untouched |
| Four capabilities ORION does **not** have | `sections/13-framework-consistency.tex:6-9` | untouched |
| External novelty: 75/75 atoms `CANNOT_CHECK`, `INACCESSIBLE_WORK_MAY_ABSORB_CLAIM` | `research/orion-epistemic-state-v1/results/DES-NOVELTY-01/` | untouched |
| Both OCME receipts' explicit denial of autonomous invention and of native superiority | `P10_OCME_FORMAL_RESULT_RECEIPT_V1.md:53`, `P10_GENERATED_OCME_RESULT_RECEIPT_V1.md:55-57` | untouched |
