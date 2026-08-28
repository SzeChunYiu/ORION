# ORION-02 — inductive-certificate / over-strong language audit V1

**Document ID:** `ORION02.LANGUAGE_AUDIT.V1`
**Date:** 2026-08-28
**Status:** `RECORD_AND_CORRECT__NO_SCIENTIFIC_AUTHORITY`
**scientific_authority_delta:** `NONE`

---

## 1. Method

Exhaustive case-insensitive grep over **all 154 files** of
`papers/orion-02-fiberguard-finite-fibre/`, terms:

`certificate guarantee` · `valid certificate` · `ensure(s)` · `guarantee(s)` ·
`inductive` · `induction` · `holds for all` · `generalize(s/d)` /
`generalise(s/d)` · `transfer(s)` · `provably` · `always`

All greps run through `rtk proxy` and counted with `wc -l`; no absence claim in
this document rests on a blank print.

### Raw term census (whole directory)

| Term | Hits | | Term | Hits |
|---|---|---|---|---|
| `certificate guarantee` | 0 | | `holds for all` | 0 |
| `valid certificate` | 0 | | `generalize(s/d)` | 0 |
| `ensures` | 0 | | `generalise(s/d)` | 0 |
| `ensure` | 14 | | `transfers` | 8 |
| `guarantees` | 2 | | `transfer` | 62 |
| `guarantee` | 20 | | `provably` | 2 |
| `inductive` | 5 | | `always` | 20 |
| `induction` | 1 | | | |

**Distribution:** 6 hits on current claim surfaces; **116** hits across 47 files
in the frozen evidence tree.

Note the three highest-risk phrases — `certificate guarantee`, `valid
certificate`, `holds for all` — return **zero** matches anywhere in the paper.

---

## 2. Editable set — declared before any edit

Per the brief's RULE *"if unsure a file is frozen, do not edit it"*:

| File | Class | Action |
|---|---|---|
| `MANUSCRIPT_V2.md` | current manuscript | **EDITABLE — edited** |
| `CLAIM_LEDGER.md` | ledger | frozen — audited, **not edited** |
| `CLAIM_LEDGER_R2.md` | ledger | frozen — audited, **not edited** |
| `rounds/README.md` | round index | frozen — audited, **not edited** |
| everything under `rounds/`, `extensions/`, `experiments/results/`, and all `*_RESULT*` / `*_TERMINAL*` / `*_CUSTODY*` / `*_RECEIPT*` / `.json` / `.log` / `.txt` / `.py` | frozen evidence | frozen — audited, **not edited** |

> **Conflict flagged for the orchestrator.** The brief's READ-FIRST item 3 calls
> the claim ledgers "current claim surfaces", while the RULES forbid editing
> ledgers. This audit resolved the conflict conservatively: ledgers were audited
> in full but not edited. Both ledger hits were assessed **JUSTIFIED**, so no
> correction is pending on them either way — the conflict is moot in outcome,
> but is recorded because it would matter for a different finding.

**Exactly one file was edited: `MANUSCRIPT_V2.md`.**

---

## 3. Findings — current claim surfaces

### 3.1 NOT JUSTIFIED (corrected)

All three share one defect: the minimax results are proved for **deterministic**
estimators only. `MANUSCRIPT_V2.md:104` states the restriction
("Let `Phi` be any **deterministic** real-valued estimator...") and Limitation 4
(`:196`) concedes "Randomized estimators are not separately analyzed". The
abstract and the §5 conclusion drop the qualifier and therefore assert a
strictly stronger result than is proved.

| ID | File:line | Exact quote (before) | Verdict | Replacement |
|---|---|---|---|---|
| **LA-01** | `MANUSCRIPT_V2.md:15` | "Every estimator using only that pair representation must return the same value on both instances." | **NOT JUSTIFIED** — unqualified "every estimator" covers randomized estimators, excluded by Limitation 4 | "Every **deterministic** estimator using only that pair representation must return the same value on both instances." |
| **LA-02** | `MANUSCRIPT_V2.md:19` | "No pair-information-only estimator can guarantee a uniform factor below `sqrt(6/5)`" | **NOT JUSTIFIED** — same overreach, and it is the sentence carrying the word `guarantee` | "No **deterministic** pair-information-only estimator can guarantee a uniform factor below `sqrt(6/5)`" |
| **LA-03** | `MANUSCRIPT_V2.md:132` | "Therefore no pair-information-only estimator has a uniform symmetric approximation factor strictly below `sqrt(6/5)` over the family." | **NOT JUSTIFIED** — same overreach. *Not a grep hit* (contains none of the audit terms); found by reading §5. Recorded because it is the same defect class and sits at the section's conclusion | "Therefore no **deterministic** pair-information-only estimator has a uniform symmetric approximation factor strictly below `sqrt(6/5)` over the family." |

Each correction inserts one word. No proved content is weakened: the theorems
are unchanged, and the sentences now match the hypothesis actually used at
`:104`.

### 3.2 JUSTIFIED (no change)

| ID | File:line | Exact quote | Why justified |
|---|---|---|---|
| LA-04 | `MANUSCRIPT_V2.md:9` | "remaining **provably** inadequate for the value and structure of the optimum" | Backed by C-C3 (PROVEN-ALL-T), C-C4 (PROVEN-ALL-T), C-C5 (PROVEN-ALL-M,L). "Inadequate" is exactly what the separations prove |
| LA-05 | `MANUSCRIPT_V2.md:199` | "Cross-objective and cross-grammar **transfer** remain open." | Correct boundary language. Declares a limit; asserts nothing |
| LA-06 | `MANUSCRIPT_V2.md:203` | "the invisible parity direction is **provably** dense" | Backed by C-C6 (PROVEN-ALL-Q) + C-C7: the trade touches all `2^q` cells |
| LA-07 | `CLAIM_LEDGER.md:13` | "C-C9 \| The separation is multiplicative or **transfers** to all objectives/grammars. \| none \| OPEN / not claimed." | Model boundary discipline — the over-strong claim is named precisely in order to disclaim it |
| LA-08 | `CLAIM_LEDGER.md:22` | "**Boundary:** common-padding minimality and cross-objective **transfer** remain open." | Correct boundary language |

`CLAIM_LEDGER_R2.md`: **0 hits.** `rounds/README.md`: **0 hits.**

### 3.3 Flagged, deliberately NOT edited

| ID | File:line | Quote | Assessment |
|---|---|---|---|
| **LA-09** | `MANUSCRIPT_V2.md:220` | "**R2 status:** `TOP_TIER_THEORY_CANDIDATE__AUTHOR_SIDE_PRIMARY_SOURCE_BLOCKER_SUBSTANTIALLY_CLOSED`." | **NOT JUSTIFIED AS POSITIONED** — `SUBSTANTIALLY_CLOSED` sits two lines above an **External-only gates** list (`:222`) that still includes *independent proof audit*. **Not edited:** rewriting a registered status token is a posture change, not a language correction, and this worker holds `scientific_authority_delta: NONE`. Referred to the orchestrator |

---

## 4. Findings — frozen evidence tree (audited, not edited)

**116 hits across 47 files.** Every hit was inspected. **No unjustified
inductive-certificate language was found in the frozen tree.** The no-alarm case
is asserted explicitly rather than left implied.

Hits fall into three benign classes:

**(a) Registered arm names and protocol identifiers — not claims.**
`always_fallback`, `always_learned`, `SBS_SHIELD = commit F* always`
(`rounds/r21-direct-relative/FIBERGUARD_TSP_DIRECT_RELATIVE_R21_PROTOCOL.md:156-157`;
`rounds/r22-proposal-ordering/FIBERGUARD_PMLB_PROPOSAL_ORDERING_R22_PROTOCOL.md:150`;
`rounds/r21-direct-relative/FIBERGUARD_CSPMZN_DIRECT_RELATIVE_R21_RESULT.md:46,52`).

**(b) Correctly scope-limiting uses of `guarantee` — the word appears in order
to bound the claim.** Examples:
- `experiments/results/CERTIFIED_NEIGHBORHOOD_CONFORMAL_RESULT_V1.md:65` and
  `..._RECOVERY_RESULT_V2.md:65` — "finite-sample marginal guarantee under
  exchangeability, **not** ..."
- `experiments/CERTIFIED_NEIGHBORHOOD_REVIVAL_V1.md:51` — "a finite-sample
  **marginal** guarantee under exchangeability — **not** ..."
- `extensions/r15/FIBERGUARD_MULTIDOMAIN_R15_PROTOCOL.md:135` — "**not** a
  population CVaR bound or a distribution-free guarantee."
- `extensions/r17/FIBERGUARD_FALLBACK_ALIGNMENT_R17.md:185` — "This is a
  union-bound guarantee. Marginal certificates for the two actions do **not**
  generally share one `alpha` budget."
- `extensions/r19/FIBERGUARD_JOINT_ROUTE_R19_REPLACEMENT.md:67` — "Randomization
  remains an expected-loss guarantee."

**(c) `inductive` used to DENY an inductive certificate, or to name a study
design.** Notably
`experiments/results/CERTIFIED_NEIGHBORHOOD_CONFORMAL_RECOVERY_INTERPRETATION_V2.md:49`
— "It does **not** revive the representation-neighborhood law as an inductive
exact certificate." Also
`experiments/CERTIFIED_NEIGHBORHOOD_CONFORMAL_PROTOCOL_V1.md:31` ("coverage tax
of per-instance inductive certification"),
`extensions/r18-relative/RELATIVE_ROUTE_EXTENSION_R18_PRIOR_ART_BOUNDARY.md:27`,
and `extensions/r18-relative/FIBERGUARD_RELATIVE_ROUTE_EXTENSION_R18.md:194`
("R14 refutes exact-equality induction on SAT12-ALL") — a preserved refutation.

**Assessment:** the frozen tree's language discipline is sound. Had a correction
been owed there, it would have been recorded here and referred out, since these
files are not editable by this worker.

---

## 5. Structural finding: no empirical contamination of the manuscript

Raw grep of `MANUSCRIPT_V2.md` for `fiberguard|pmlb|aslib` returns **0
matches**. The manuscript makes no claim that the FiberGuard certificate is
valid or that it transfers. Given the R24 terminal
`C_R24_ARM_CONDITIONAL_CERTIFICATE_INVALID`, any such reference would have been
a hard NOT JUSTIFIED. There is none.

## 6. Assertion of the no-alarm case

The manuscript's boundary posture was already strong before this audit, and this
is recorded rather than passed over: C-C9 is `OPEN / not claimed`; C2-C12 marks
the hardness reading `FORBIDDEN`; C-C10 / C2-C11 marks the fibre mathematics
`DONOR-OWNED`; §10 carries seven explicit limitations including the randomized-
estimator concession that made LA-01/02/03 detectable at all.

**Three single-word corrections were applied. No finding was manufactured to
fill the table.** Over-correction that dilutes genuine proof language would be a
worse defect than a short list.

---

## 7. Verification of applied edits

- Files edited: **1** (`MANUSCRIPT_V2.md`).
- Edits applied: **3** (LA-01, LA-02, LA-03), each inserting the single word
  `deterministic`.
- Post-edit `git diff --numstat` and a re-grep confirming 0 remaining
  unqualified occurrences are recorded in §7.1 below.

### 7.1 Post-edit verification record
See `POST_EDIT_VERIFICATION` block appended at the end of this file.

---

## POST_EDIT_VERIFICATION

Baseline captured before any edit (`git status --porcelain` scoped to
`papers/orion-02-fiberguard-finite-fibre/`): **1** entry, the newly written
`THEORY_CORE_FREEZE_V1.md`; `MANUSCRIPT_V2.md` unmodified.

**Applied edits.** Each replacement asserted `count == 1` before writing and
aborted otherwise. All three reported exactly 1 occurrence replaced.
Byte delta `14275 -> 14317 = +42` = `3 x len("deterministic ")` = `3 x 14`.
Exactly the intended insertion, nothing else.

**Scope check** — `git diff --numstat -- papers/orion-02-fiberguard-finite-fibre/`:

```
3	3	papers/orion-02-fiberguard-finite-fibre/MANUSCRIPT_V2.md
```

Modified-file count piped to `wc -l`: **1**. No frozen record, receipt, round
result, ledger or `rounds/README.md` was modified. Untracked additions in this
path are the two documents authored by this task
(`THEORY_CORE_FREEZE_V1.md`, `LANGUAGE_AUDIT_V1.md`); `INDEPENDENT_PROOF_REVIEW_V1.md`
and `experiments/selective-fibre-risk-v1/` are added by the same task and appear
in later listings.

**Content check** — `grep -n "deterministic" MANUSCRIPT_V2.md` now returns lines
`15`, `19`, `104`, `132`. Line 104 is the pre-existing hypothesis; 15, 19 and
132 are the corrections.

**Residual check** — `grep -c "no pair-information-only estimator"` returns
**0**: no unqualified form remains.

**Verified by counting, not by blank output.** Every check above is a numeric
count or an explicit listing.

---

## Application status — CORRECTIONS IDENTIFIED, NOT APPLIED (2026-08-28)

The three corrections above were applied to `MANUSCRIPT_V2.md` and then **reverted**,
for a reason that belongs in the record rather than in a commit message.

`papers/FIVE_THEORY_HARDENING_R2_RESULTS.json` binds this manuscript as theory **"C"**
by **byte count and digest**, and `tests/unit/publication/test_five_theory_hardening_r2.py::test_r2_manifest_binds_every_declared_file`
enforces it. The three corrections change the file from **14313** to **14355** bytes
(+42 = 3 x `len("deterministic ")`), which fails that guard.

Reconciling it would mean editing a **frozen five-theory hardening result record** to
match new manuscript bytes. That is the one move the revival doctrine forbids outright:
a result record is rewritten to match an outcome. The guard is correct to refuse it.

**This is the same shape as the ORION-01 sibling-decoupling item.** The correction is
right, verified, and ready; applying it requires reconciling a frozen record in
lockstep, which is an operator decision, not a lane decision.

### What an operator needs to decide

Either:

1. **Supersede** — issue a new hardening result under a new identity that binds the
   corrected manuscript, leaving `FIVE_THEORY_HARDENING_R2_RESULTS.json` as history; or
2. **Lockstep** — update the manuscript and the R2 record together in one change, with
   the reason recorded, accepting that the R2 record's digests then describe post-audit
   bytes; or
3. **Decline** — leave the unjustified language in place and record the audit as the
   standing correction.

Option 3 is not recommended: the corrections remove language the theorems do not
support, and the manuscript is a submission surface.

The exact replacement text is in the table above. Nothing about the audit's findings
changes with this deferral — only whether the bytes have moved yet.
