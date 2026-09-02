# O12FNA1 — ORION-12 filing-number binding audit (protocol V1)

Status: FROZEN 2026-09-03, BEFORE any binding below was executed, logged, or
adjudicated by the driver. The binding table in Section 5 was transcribed from
the frozen artifacts and surfaces by reading them as text only; no comparison
in this table has been executed programmatically before this freeze (the shell
greps used to design the study located files and keys, they did not adjudicate
any binding).

Study id: `O12FNA1`. Lane: `development/orion-12-filing-number-binding-2026-09-03/`.
Driver: `development/orion-12-filing-number-binding-2026-09-03/o12fna1_filing_number_audit.py`.
This is an AUDIT, not new science. It grants no claim, no freeze, no novelty,
no submission authority. Its only possible products are (a) machine evidence
that every load-bearing number printed on ORION-12's frozen filing surfaces
equals its frozen evidence-artifact value, plus a re-adjudication of the
`submission/FILING_METADATA_V1.json` pre-filing blockers against the current
tree, or (b) a named drift/defect finding with the exact slots listed.

## 1. Question and motivation

The 2026-09-02 IP&M honesty pass (ORION PR #2126) hand-edited superiority
hedges, the underpower Limitations paragraph, and the cover letter; the V2
freeze addendum (2026-09-01) records the TREC-COVID negative numbers and the
V2/V3 BEIR stopping-successor identity claims in prose. The repo's existing
ledger checker (`scripts/check_claim_ledger.py`) binds only the older
integrated manuscript against `protocol/CLAIM_LEDGER_V1.json`; NO checker
binds the CURRENT frozen filing surfaces — freeze addendum V2, the IP&M cover
letter, `FILING_METADATA_V1.json`, `ipm_submission.tex`, `main.tex`, the
public-screening section, `JOURNAL_READINESS_V2.md` — to the frozen evidence
artifacts. Every one of those numbers is currently hand-transcribed. The same
metadata file lists four `blocking_before_filing` items whose truth on the
current tree is unrecorded since the #2136-era rebind.

O12FNA1 asks exactly: does every load-bearing number on the current frozen
filing surfaces equal the value in the frozen evidence artifact it came from,
and which of the four recorded pre-filing blockers are still open on the
current tree?

## 2. Frozen inputs (read-only; imported by path, never copied or re-derived)

All paths relative to `papers/orion-12-open-world-scientific-discovery/`.

- A1 `external/P2_TREC_COVID_ARMS_V1.json`
- A2 `evidence/P2_INTEGRATED_CLAIM_BINDINGS_V1.json`
- A3 `evidence/p2x/P2_X_CLAIM_VALUES_V1.json`
- A4 `manuscript/generated/suite_facts.json`
- A5 `protocol/STATISTICAL_PLAN_V1.json`
- A6 `experiments/beir-route-aware-stopping-v1/RESULTS_V1.json`
- A7 `experiments/beir-route-aware-stopping-v2-density/RESULTS_V2.json`
- A8 `experiments/beir-route-aware-stopping-v3-conditional/RESULTS_V3.json`
- A9 `evidence/external_results/P2_V2_ACQUISITION_DEV3R_RESULT_2026-08-18.json`
- M1 `journal_package/SHA256SUMS` (paper-root-relative digests)
- M2 `submission/SHA256SUMS` (submission/-relative digests)
- M3 `submission/SUBMISSION_MANIFEST.sha256` (paper-root-relative digests)
- M4 `experiments/beir-route-aware-stopping-v1/SHA256SUMS`
  (experiment-dir-relative digests)
- M5 `journal_package/current_revision/SUBMISSION_MANIFEST.json`

No mathematical constant, threshold, or aggregation rule is defined locally.
Every expected value comes from a JSON key of a frozen artifact listed above.

## 3. Frozen surfaces audited (read-only; never edited by this study)

- S1 `PUBLICATION_FREEZE_ADDENDUM_V2.md`
- S2 `journal_package/elsevier-cas/cover_letter_ipm_20260902.md`
- S3 `submission/FILING_METADATA_V1.json`
- S4 `manuscript/ipm_submission.tex`
- S5 `manuscript/main.tex`
- S6 `manuscript/sections/05a-public-screening-transport.tex`
- S7 `JOURNAL_READINESS_V2.md`
- S8 `manuscript/generated/suite_facts.tex` (macro bodies audited against A4)

## 4. Integrity preconditions (hard gates; failure = defect, not a terminal)

- G0 existence: every input of Section 2 and every surface of Section 3 must
  exist on disk at the registered base revision. Any absence → the
  CANNOT_CHECK terminal (Section 7); the run refuses to adjudicate bindings.
- G1 `journal_package/SHA256SUMS`: every listed digest equals the on-disk file.
- G2 `submission/SHA256SUMS`: every listed digest equals the on-disk file.
- G3 `submission/SUBMISSION_MANIFEST.sha256` and
  `experiments/beir-route-aware-stopping-v1/SHA256SUMS`: same.
- G4 non-vacuity: the registered binding set (Section 5) must be non-empty
  (registered count N >= 35) and every binding's artifact key must resolve.
  An unresolvable key is an internal defect (exit 4), never a pass.

Digest mismatch in G1–G3 is terminal `..._DRIFT_DETECTED` with the mismatching
paths listed (that is the strongest possible finding: the audited bytes are not
the bound bytes).

## 5. Registered binding table (frozen)

Two comparator classes:

- `NUMBER(p)`: the surface must contain the decimal literal equal to the
  artifact value rounded to p decimals (`round(value, p)` then fixed-point
  formatting with exactly p decimals; `p=None` means exact string of the JSON
  value). Match is by substring occurrence in the surface text (LaTeX
  math-mode `$...$` included as plain text). Unless a row states a higher
  minimum, one occurrence suffices; the receipt records the observed count.
- `TEXT`: exact substring (whitespace-normalized per Section 6) must occur.

### 5.1 Cover letter (S2)

| # | surface substring | artifact key | class |
|---|---|---|---|
| 1 | `0.110334` | A1 `arms_macro.bm25.recall_at_100` | NUMBER(6) |
| 2 | `0.092642` | A1 `arms_macro.orion_full.recall_at_100` | NUMBER(6) |
| 3 | `$-0.01769$` (as `-0.01769`) | A1 `pass_gate_verdict.criteria.recall_noninferiority.delta_mean` | NUMBER(5) |
| 4 | `-0.02729` | A1 `...recall_noninferiority.bootstrap_ci95[0]` | NUMBER(5) |
| 5 | `-0.00906` | A1 `...recall_noninferiority.bootstrap_ci95[1]` | NUMBER(5) |
| 6 | `175.7` | A1 `pass_gate_verdict.criteria.cost_reduction.reads_vs_comparator_pct` | NUMBER(1) |
| 7 | `0.1488` | A1 `pass_gate_verdict.not_a_gate_criterion_but_measured.ndcg_at_10_delta_mean` | NUMBER(4) |
| 8 | `matches 400 of` (as `{p2x_correct} of`) | A3 `p2x_correct` | TEXT-derived |
| 9 | `250 of 400` | A3 `b1_correct`, A3 `n` | TEXT-derived |
| 10 | `0.0496` | A4 `OfflineAchievedHalfWidth` | NUMBER(4) |
| 11 | `0.03` (as ` 0.03 ` token) | A5 tier `TIER_A_full.half_width` | NUMBER(2) |
| 12 | `78-topic` (as `{OfflineTopicCount}-topic`) | A4 `OfflineTopicCount` | TEXT-derived |
| 13 | `390` (as ` 390 ` token) | A4 `OfflineTaskCount` | NUMBER(0) |

### 5.2 Freeze addendum V2 (S1)

| # | surface substring | artifact key | class |
|---|---|---|---|
| 14 | `-0.01769` | A1 delta_mean (as #3) | NUMBER(5) |
| 15 | `[-0.02729,-0.00906]` | A1 bootstrap_ci95 (both ends, no spaces) | TEXT-derived |
| 16 | `175.7` | A1 reads_vs_comparator_pct | NUMBER(1) |
| 17 | `recall@100` appears with the CI sentence | — (text anchor only) | TEXT |
| 18 | stopping-identity (Section 5.5 I1) | A6 vs A7 arguana | IDENTITY |
| 19 | stopping-identity (Section 5.5 I2) | A6 vs A8 arguana | IDENTITY |
| 20 | stopping-identity (Section 5.5 I3) | A6 vs A8 scifact | IDENTITY |
| 21 | stopping-identity (Section 5.5 I4) | A6 vs A8 nfcorpus | INEQUALITY |

### 5.3 IP&M filing source (S4 `ipm_submission.tex`)

| # | surface substring | artifact key | class |
|---|---|---|---|
| 22 | `matches 400 of` | A3 `p2x_correct` | TEXT-derived |
| 23 | `250 of 400` | A3 `b1_correct`, `n` | TEXT-derived |
| 24 | `lower by 0.01769` | A1 `abs(delta_mean)` | NUMBER(5) |
| 25 | `[-0.02729,-0.00906]` | A1 bootstrap_ci95 | TEXT-derived |
| 26 | `175.7` | A1 reads_vs_comparator_pct | NUMBER(1) |
| 27 | `0.1488` | A1 ndcg_at_10_delta_mean | NUMBER(4) |
| 28 | `1068 at half-width $0.03$` | A5 TIER_A_full `required_n`, `half_width` | TEXT-derived |
| 29 | `385 at $0.05$` | A5 TIER_B_committed `required_n`, `half_width` | TEXT-derived |
| 30 | `171 at $0.075$` | A5 TIER_C_reduced `required_n`, `half_width` | TEXT-derived |
| 31 | `97 at $0.10$` | A5 TIER_D_minimum_inferential `required_n`, `half_width` | TEXT-derived |
| 32 | macro references `\OfflineUnderpowered`, `\OfflineAchievedHalfWidth`, `\OfflineTaskCount`, `\OfflineSystemCount`, `\OfflineRepeatCount`, `\OfflineTopicCount` each occur | S8 macro defined | TEXT |

### 5.4 Manuscript main + screening section + readiness (S5, S6, S7)

Minimum occurrence counts below were transcribed from the surfaces at design
time; the gate is `occurrences >= registered minimum`.

| # | surface substring | artifact key | class |
|---|---|---|---|
| 33 | `0.722444` (S5, >=2; S6, >=1) | A2 `facts.zenodo.active_audit_u4_recall_at_10` | NUMBER(6) |
| 34 | `0.703409` (S5, >=2; S6, >=2) | A2 `facts.zenodo.active_audit_candidate_recall_at_10` | NUMBER(6) |
| 35 | `0.744744` (S5, >=1; S6, >=1) | A2 `facts.zenodo.active_audit_candidate_wss_at_95` | NUMBER(6) |
| 36 | `+0.148820` (S5, >=1) | A2 `facts.kifms_v7.learner_balancer_mean_recall_at_10` | NUMBER(6) |
| 37 | `+0.119813` (S5, >=1) | A2 `facts.kifms_v7.learner_balancer_mean_wss_at_95` | NUMBER(6) |
| 38 | `0.051422` (S7, >=1) | A9 `official_metrics.baseline.avg_recall` | NUMBER(6) |
| 39 | `0.044213` (S7, >=1) | A9 `official_metrics.candidate.avg_recall` | NUMBER(6) |
| 40 | `-0.007209` (S7, >=1) | A9 `official_metrics.candidate_minus_baseline.avg_recall` | NUMBER(6) |

### 5.5 Stopping-identity class (exact structural equality)

Let `stop(V, corpus, depth)` = the `corpora.<corpus>.by_depth.<depth>.
route_aware_stop` sub-dict of result V. Registered claims, from the addendum
V2 text: "On ArguAna, all five stopping decisions remain identical to V1"
(V2 row) and "ArguAna again remains identical to V1 at all five depths;
SciFact is also unchanged, while NFCorpus changes slightly" (V3 row).

- I1: `stop(A7,arguana,d) == stop(A6,arguana,d)` for all five depths
  {10,20,50,100,200}.
- I2: `stop(A8,arguana,d) == stop(A6,arguana,d)` for all five depths.
- I3: `stop(A8,scifact,d) == stop(A6,scifact,d)` for all five depths.
- I4: `stop(A8,nfcorpus,d) != stop(A6,nfcorpus,d)` for at least one depth
  (registered INEQUALITY; "changes slightly").

Equality is exact dict equality of the frozen JSON values (floats compared
bitwise as parsed). No tolerance.

### 5.6 Macro↔JSON and derived-arithmetic bindings

- M-A: every macro defined in S8 equals the same-named key of A4 (string
  compare after stripping LaTeX thousands separators `{,}`): TaskCount 390,
  DocumentCount 1210, TopicCount 78, SuiteSeed 20260816, SystemCount 14,
  RepeatCount 3, RunRecordCount 16380, AchievedHalfWidth 0.0496,
  Underpowered `yes`, plus the fingerprint short form.
- M-B: derived product `OfflineTaskCount * OfflineSystemCount *
  OfflineRepeatCount == OfflineRunRecordCount` (integer arithmetic on A4
  values only; 390*14*3 == 16380).

### 5.7 Filing-metadata consistency (S3)

- F-A: `FILING_METADATA_V1.json.title` equals the `\title{...}` literal of S5
  (whitespace-normalized, `--` kept as-is).
- F-B: `title_ipm_adapted` equals the `\title[mode=title]{...}` literal of S4
  (whitespace-normalized across the line break).
- F-C: every path listed in M5 `artifacts[].path` and `reader_facing_uploads[]`
  exists on disk (resolved against the paper root and the
  `journal_package/current_revision/` dir).

## 6. Recorded findings (non-gating; reported either way)

1. FILING_METADATA `blocking_before_filing` re-adjudication:
   - b1 title divergence: OPEN iff S5 title literal != S4 title literal.
   - b2 "declared PDF absent": record STALE_RESOLVED iff F-C passes and the
     M5-declared `manuscript.pdf` exists; else CONFIRMED_OPEN.
   - b3 anonymous author block: OPEN iff S4 still contains
     `Anonymous authors` in `\author`.
   - b4 live IP&M guide verification: `CANNOT_CHECK_EXTERNAL` (this study
     makes no network call; distinct from "checked and fine").
2. Binding-status census: for each audited surface/input, which manifest
   (M1–M4) covers it, or `UNBOUND`. Unbound is a recorded property, not a
   failure.
3. Count of registered bindings and pass/fail per class.

These findings do not gate the terminal; the terminal is decided by Section 4
gates plus the Section 5 bindings only.

## 7. Frozen verdict space (terminals; no post-hoc weakening)

- `O12_FNA1_FILING_NUMBER_BINDING_VERIFIED__ZERO_DRIFT` — G0–G4 pass and
  every Section 5 binding holds. Exit 0.
- `O12_FNA1_FILING_NUMBER_DRIFT_DETECTED` — any G1–G3 digest mismatch or any
  Section 5 binding inequality; the failing slots are listed verbatim
  (surface, expected literal, artifact path+key, artifact value). Exit 2.
- `O12_FNA1_CANNOT_CHECK__FROZEN_INPUT_OR_SURFACE_ABSENT` — G0 fails; the
  missing paths are listed; NO binding is adjudicated. Exit 3.

Any internal exception (unresolvable registered key, JSON parse failure of a
supposedly frozen artifact, empty binding set) is a defect: exit 4 with the
exception recorded. It is never a pass and never conflated with a terminal.

## 8. Frozen claim boundary and authority

A VERIFIED terminal claims ONLY: at the registered base revision, on the
audited byte ranges, each registered literal on the listed frozen filing
surfaces equals its listed frozen-artifact value, the package digests listed
in M1–M4 reproduce, and the recorded pre-filing blocker states are as
reported. It is NOT a claim of external validity, NOT new science, NOT a
manuscript edit, NOT a rebind, NOT a submission authorization, and does NOT
close the operator-only filing boxes of ORION-paper #78. A DRIFT terminal is
a defect report localizing transcription drift (or byte drift) to the named
slots; its one-stage attribution is surface-side transcription or package
digest staleness, and the named revival lever is regenerating the affected
surface from the artifact value under the paper's rebind procedure.

Authority string (recorded in the receipt):
`AUDIT_ONLY__BINDING_VERIFICATION_NOT_NEW_SCIENCE_NOT_A_CLAIM_CHANGE_NOT_A_REBIND`.
`novelty_authority: false`, `physical_quantum_advantage_claim: false`.

## 9. Integrity and reproducibility

- Protocol SHA-256 recorded in the receipt; run at the registration commit
  (`base_revision` recorded).
- Determinism: the registered run is executed twice; the two result JSONs
  must be byte-identical (the receipt contains no timestamps or randomness).
- Smoke mode: `--smoke` evaluates G0 plus the first 6 bindings only, writes
  nothing, exit 0/2/3/4 with the same semantics; used before registration
  commit only.
- Outputs: `O12FNA1_RESULTS.json` in this lane dir (canonical sorted JSON,
  schema `ORION.ORION12.FilingNumberAudit.v1`), `RUN_O12FNA1.log` capturing
  both run transcripts.
- No committed file is modified; only this protocol, the driver, the result
  JSON, and the run log are added.
