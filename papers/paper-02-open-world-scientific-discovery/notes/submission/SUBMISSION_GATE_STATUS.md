# P2 submission gate status

State of every submission-gate checkbox, as of **2026-08-17**.

**Numbering note.** `JOURNAL_READINESS.md` has nine numbered sections; the
submission gate is **section 9**, and there is no section 10. This file covers
section 9 in full, plus the three section 8 (reproducibility package) items that
belong to the submission gate rather than to the experiment.

States are `DONE`, `BLOCKED_ON <what>`, `DEFERRED <condition>`. Where a checkbox's
own precondition is unmet, that is stated rather than absorbed into a `DONE`.

## Section 9 — submission gate

| # | Checkbox | State | Justifying artifact / reason |
| --- | --- | --- | --- |
| 9.1 | literature closure within 14 days of submission | `DEFERRED until a submission date exists` | The requirement is time-boxed to a date not yet set, so it cannot be satisfied early — closing it now would only expire again. Standing basis: `notes/NEAREST_WORK_AUDIT_2026-08.md`, `notes/nearest-work/*.md`, `evidence/literature/*.json`, and `tests/unit/p2/test_p2_literature_closure.py`. Owner: literature lane. Action: re-run the closure sweep inside the 14-day window. |
| 9.2 | target-journal scope check after external results stabilize | `DONE` | `notes/submission/JOURNAL_SCOPE_CHECK.md`. Four venues assessed against pages fetched 2026-08-17; recommendation **TMLR**, with reasoning tied to what the claim ledger supports. Four further venues marked `CANNOT_CHECK` because their pages would not load. |
| 9.2b | scope check re-verification once external results stabilize | `BLOCKED_ON external result stabilization` | The checkbox's stated precondition is **not** met: no Wide/Deep system result is archived, so the check above was necessarily made under `CANNOT_CHECK` external status. The recommendation is contingent by construction — TMLR fits *because* external superiority is unproven; if an external campaign lands, Research Synthesis Methods becomes viable and the venue decision must be retaken. |
| 9.3a | cover letter | `DONE` | `notes/submission/COVER_LETTER_DRAFT.md`. Claims exactly what the ledger supports; names the four limits (synthetic index, external families under declared deviations, one inherited unseeded upstream metric, live-provider mutability); no superlatives, no invented endorsements, no reviewer suggestions. Must not be sent before defects `P2-D01`/`P2-D02` are fixed. |
| 9.3b | supplement | `DONE` (plan) / `BLOCKED_ON assembly` | `notes/submission/SUPPLEMENT_PLAN.md` enumerates included, deferred and licence-excluded contents plus a pre-submission checklist. The ZIP itself has not been built, and building it requires the anonymisation in 9.3c. |
| 9.3c | journal formatting | `BLOCKED_ON TMLR style adoption and anonymisation` | `manuscript/main.tex` is `\documentclass[11pt]{article}`. TMLR requires its official LaTeX style file and double-blind anonymisation (<https://jmlr.org/tmlr/author-guide.html>, fetched 2026-08-17), and neither is applied. The author line is the placeholder `\author{Working framework draft}` and no acknowledgements or funding text exists, so anonymisation is unstarted rather than violated — but real author metadata must never be added except on the TMLR anonymised template. Owner: manuscript lane. |
| 9.4 | final reference-metadata and figure-legibility audit | `BLOCKED_ON the manuscript compile and reference-audit workflow` | Depends on the ChatGPT lane's compile + reference audit (`chatgpt/p2-remaining-closure`, PR #170). Not startable from this lane: a legibility audit needs a rendered PDF, and there is no compile artifact to inspect. |
| 9.5 | independent final PDF/claim proofread | `BLOCKED_ON 9.3c, 9.4 and defects P2-D01/P2-D02` | Two prerequisites are mechanical (a compiled, correctly formatted PDF) and one is substantive: the manuscript currently contains two statements the archive contradicts. Proofreading against a known-wrong text would certify the error. The claim half of this gate is now mechanised — `scripts/check_claim_ledger.py --check` is green in 0.04 s — but a human still owns the prose read. |

## Section 8 — reproducibility package items owned by the gate

| # | Checkbox | State | Justifying artifact / reason |
| --- | --- | --- | --- |
| 8.4 | raw final live-provider results and request timestamps | `BLOCKED_ON the final live-provider campaign` | Capture machinery exists and has been exercised (`protocol/LIVE_CAMPAIGN_PROTOCOL_V1.md`, `tests/unit/p2/test_p2_live_campaign.py`); no final campaign archive exists. Tier 3 in `ARCHIVE_AND_COST_LEDGER.md`. |
| 8.8 | clean-environment expected external runtime/cost ledger | `DONE` (structure and the one completed item) / `BLOCKED_ON campaign execution` (remaining rows) | `notes/submission/ARCHIVE_AND_COST_LEDGER.md` §2. The completed MetaSyn probe carries verified figures: **7 min 34 s** wall clock and **$0** metered cost, 0 LLM API calls, read from Actions run `31973786111`. Every unexecuted row is `UNKNOWN_PENDING_RUN`, never an estimate. Tier 1 runtimes are also `UNKNOWN_PENDING_RUN` because they have not been timed in a clean environment — only the ledger checker has an observed time. |
| 8.10 | permanent archive/DOI | `BLOCKED_ON archive creation` | Contents and licence exclusions are now specified (`ARCHIVE_AND_COST_LEDGER.md` §1); nothing has been deposited. **Time-critical:** the MetaSyn probe's raw Actions artifact expires `2026-09-15T21:39:53Z` per `METASYN_ID_ONLY_PROBE_V1.json`. Mirror it into the archive before that date or the raw evidence is lost, leaving only its digests. |

## New gate row added by this lane

| Item | State | Artifact |
| --- | --- | --- |
| Claim ledger mechanised and machine-checked | `DONE` | `protocol/CLAIM_LEDGER_V1.json` (43 rows), `scripts/check_claim_ledger.py`, `tests/unit/p2/test_p2_claim_ledger.py` (45 tests: injected-defect coverage plus the no-alarm case). Green on the committed tree; `--strict` fails only on the two recorded manuscript defects. |

All four ledgered regions — abstract, conclusion, Limitations and Results prose —
hard-fail on an unledgered outcome sentence. Every outcome sentence in those
regions is currently either a ledger claim, an explicitly reasoned non-claim, or a
recorded defect, so the check is green with no suppressions. **Consequence for
other lanes:** the checker runs against the committed manuscript, so any lane that
adds or rewords a result-bearing sentence in `main.tex` or `sections/results.tex`
will turn CI red until the ledger is re-verified. That is intended — the failure
message prints both the ledger sentence and the current manuscript text so the
re-verification is guided rather than a manual sweep — but it was not scoped as a
cross-lane gate and the lead should know it now behaves as one.

## Open defects blocking submission

Both are recorded in `protocol/CLAIM_LEDGER_V1.json` under `known_defects` and are
printed on **every** checker run, so they cannot rot quietly. Neither file is
editable from this lane.

| ID | Location | Problem | Required fix |
| --- | --- | --- | --- |
| `P2-D01` | `manuscript/sections/results.tex` | States that no external MetaSyn performance result is reported in this revision. The archived probe scored **all released test reviews** under the pinned official ID-only evaluator. | Remove MetaSyn from the negative list; report the probe with its declared scope (keyless BM25 + deterministic screening candidate, not the matched multi-provider system). Then promote ledger row `P2-X01` from `NOT_ASSERTED_ARCHIVED_ONLY` to `ASSERTED`. |
| `P2-D02` | `manuscript/main.tex`, Limitations | States that MetaSyn retrieval/screening is "runnable by source audit but unexecuted here". It was executed; the archive carries authority `OFFICIAL_METASYN_ID_ONLY_EVALUATOR`. | Replace the "unexecuted here" clause. The Wide, Deep and SAGE clauses in the same sentence are accurate and should be kept. |

Both are **under**-claims, not over-claims, so neither inflates the paper — but a
submitted manuscript that denies its own archived evidence is a reviewer-visible
integrity problem, and `evidence/CLAIM_LEDGER_V1.md` already lists the MetaSyn row
as `SUPPORTED`, so the paper currently contradicts its own ledger.

A third, smaller item: `manuscript/main.tex` points readers at
`evidence/CLAIM_LEDGER_V1.md` only. It should also cite
`protocol/CLAIM_LEDGER_V1.json` and the checker, since the machine-checkable form
is now the authoritative one and the prose table is the human view.

## Honest summary

Of the eight section 9 rows, **three are `DONE`** (scope check, cover letter,
supplement plan), one is `DONE` as a plan awaiting assembly, **one is `DEFERRED`**
by its own time-box, and **three are `BLOCKED_ON`** work owned by other lanes
(formatting/anonymisation, compile + reference audit, final proofread). Of the
three section 8 rows, one is `DONE`, two are `BLOCKED_ON` unexecuted campaigns.

Nothing in this lane's output moves the paper's terminal status. It remains
`CANNOT_CHECK` on externally supported discovery superiority, and no gate row
above changes that — the gate work makes the narrow claim auditable and the paper
submittable, not stronger.

## `BLOCKED_ON` list

1. External result stabilization — venue decision re-verification (9.2b).
2. TMLR style adoption and double-blind anonymisation (9.3c) — blocks supplement assembly (9.3b).
3. Manuscript compile and reference-audit workflow, ChatGPT lane PR #170 (9.4).
4. Items 2 and 3 plus defects `P2-D01`/`P2-D02` — final PDF/claim proofread (9.5).
5. Final live-provider campaign — raw archive (8.4) and remaining cost-ledger rows (8.8).
6. Archive deposit (8.10), with a hard deadline of 2026-09-15 to mirror the expiring MetaSyn artifact.
7. Defect fixes `P2-D01` and `P2-D02` — owned by the results/manuscript lanes.
