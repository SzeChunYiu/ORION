# SAGE short-form as an external task family under declared scoring

Binds `PROTOCOL_V1.json` / `STATISTICAL_PLAN_V1.json`. Runner `scripts/run_sage_shortform.py`; tests `tests/unit/p2/test_p2_sage_shortform.py`. Upstream `HughieHu/Sage` at `bc62257a13d81ae233ecbd508037614746d2776b`, which carries **no LICENSE**: records are fetched and hashed, never vendored here.

**Obtainable** 600 short-form records in four domain files (150 each): `paper_id`, `paper_title`, `complete_query`, `ground_truth{paperId,title}`. **Not obtainable** the 200k retrieval corpus and any official evaluator — neither is published, and no budget changes that. So **every number here is a declared deviation; none may be called official.** Gold ids are Semantic Scholar `paperId`s this paper cannot resolve keyless, so the join is normalised-title matching (§4).

Framing dependency, not yet on `main`: the usability verdict keeping this family in the paper is on `claude/p2-sage-usability` — `notes/access/SAGE_USABILITY_REVISION_3.md` (blob `0f10ddfc2aebdcc5fe24b5adfe5734b5a7634d3c`) and that branch's `usable_task_family_under_declared_deviation` key in `EXTERNAL_ACCESS_AUDIT_V1.json` (blob `3e15c6d682363222810dfae43fdd4e7e075ed172`). `main`'s audit still says `NO_ARTIFACT_MISSING`; if that branch does not merge, the family reverts to struck and this document is void.

## 1. Parsed inventory — re-verified on every `prepare`, never read off a README

| Quantity | Value |
|---|---|
| Records parsed | 600 (150 per domain) |
| With `ground_truth` | **599** |
| Without `ground_truth` | **1** — `healthcare[63]`, `paper_id bbecae5da4f5a7bc59e560f253fe0c3a4d305884` |
| `paper_id`==`ground_truth.paperId` and `paper_title`==`ground_truth.title` | 599/599 |
| Distinct query strings | 587 — 13 duplicate groups, **all agreeing on gold** |
| Eligible tasks after dedup | **586** |
| Distinct gold targets among them | 584 (2 targets answer two queries each) |

Two corrections to this lane's briefing, both verified above: gold is on 599 records, not 600; and `paper_id`/`paper_title` **are** gold under another name, so hiding only `ground_truth` would leak the answer twice.

The gold-less record is excluded from the eligible pool before any draw and named in the split manifest — 1/600 = 0.17%, far inside the frozen 0.05 exclusion budget. Its `paper_title` would be a well-supported fallback (599/599 equality), but that is a host-invented answer, so it is excluded instead. Duplicate-query records are dropped because identical query text with identical gold is one task twice, and keeping both inflates N while understating variance; `prepare` **raises** if any duplicate group disagrees about its gold, since exact match would then have no defined target.

Aggregation unit is the **query**. Two targets answer two queries each, so tasks are not fully independent Bernoulli trials; that count is reported with every interval rather than assumed away.

## 2. Custody, subsample, budgets

`prepare` is the only command permitted to read gold. It emits a public file whose records carry exactly `{task_id, domain, complete_query}` plus a host-only gold file, and asserts that no key naming an answer (`ground_truth`, `paper_id`, `paper_title`, `paperId`, `gold`, `answer`, `target`) appears at any nesting depth in the public file. `run` re-checks the same property and refuses a file carrying gold; it has no parameter that could accept a gold path.

Subsample: seed `20260816`, stratified across four domains, **N = 385** (97/96/96/96), task-id sha256 `c5c9b81e00a66c088305eb6a52d7e7f4f2d6894a2fb6561e7559522c78a122f1`, frozen before scoring. A separate 8-task pilot is drawn **first** and is disjoint by construction: the frozen policy requires the cap to come from a declared pilot and bars pilot tasks from the test. The pilot is also where the §3 derivations were fixed.

Budget: 3 provider requests per task per system. Maximum pilot consumption was 3, so the cap is the next `query_count` ladder rung, **10**, identical for both systems and written to the manifest `resource_limits` before any outcome is accessed. `run` **raises** on a cap or budget mismatch, because the frozen policy calls such a family INVALID rather than merely noteworthy.

Why 385 and not all 586: both land in `TIER_B_committed` and both are labelled `UNDERPOWERED` (§5), so the extra 201 tasks change neither, at 1.5x the load on three keyless APIs. Even the full eligible pool cannot reach `TIER_A_full` (N ≥ 1068).

## 3. Systems and route derivations

| Route kind | Derivation | Signal | Multiroute backend |
|---|---|---|---|
| `CURRENT_VOCABULARY` | `content_vocabulary` | 4 salient terms, double-quoted spans removed first | OpenAIRE |
| `LEXICAL_VARIANT` | `bibliographic_shape` | title-shape hint + venue + year + 3 terms | DBLP |
| `CITATION_NEIGHBORHOOD` | `citation_neighbourhood` | the co-cited titles the query quotes verbatim | Crossref |

Double-quoted spans leave the content route because they are the titles of **other** papers the target co-cites; searching them retrieves those instead. Four content terms is pilot-measured, not taste: OpenAIRE conjoins keyword terms, and one pilot probe returned 16871 / 407 / 18 / 1 / 0 results at 2 / 3 / 4 / 5 / 8 terms.

- `sage_governed_multiroute` — system under test. Derivation *i* to backend *i*, dedup on content digest, route control via `FrozenRouteControlPolicy`.
- `sage_single_backend` — matched-budget internal contrast. The **same three derivations**, all on Crossref (`query.bibliographic`, the strongest general bibliographic matcher of the three). Only backend allocation differs, so the contrast isolates backend diversity rather than confounding it with a weaker query strategy.

`sage_single_backend` is **not** a frozen baseline here. The frozen SAGE baseline set is `bm25_keyword` (gate), `dense_retrieval`, `sparse_dense_hybrid`; `agentic_single_route` is not listed for SAGE. It therefore cannot be the `strongest_matched_baseline`, whose frozen definition draws from the frozen set only.

Dedup is on a normalised-title digest, never a DOI or DBLP key, per bindings B4/B7: a source that re-mints ids makes two routes that found one paper look disjoint and inflates every unique-yield number built on overlap. Route independence is **constructed then checked** by `assess_pair`, not asserted — the pilot returned `INDEPENDENT` for all 24 multiroute pairs and `SHARED_BACKEND` for all 24 single-backend pairs, the intended structural difference.

## 4. Declared scoring

Both variants are ordered transform lists (`STRICT_TRANSFORMS` / `RELAXED_TRANSFORMS` in code).

**strict** — normalised equality. In order: NFKD; drop combining marks; typographic quotes and dashes to ASCII; casefold; every run of non-`[a-z0-9]` to one space; collapse and strip. So `"Graph Title."` matches `"Graph Title"`, which matters because DBLP appends a full stop.

**relaxed** — strict, or the gold token run appears as a contiguous token subsequence of the candidate, absorbing publisher-appended subtitles. Gold titles under three tokens are not relaxed. Truncating at the first colon was **rejected**: it collapses `"ReConcile: ..."` to `"reconcile"`, and the collision check below is what rejected it.

Validated before scoring, over the gold set alone: at N = 385, **0** distinct gold titles share a strict normalised form and **0** gold title is contained in another under relaxed. Neither variant is ambiguous on this task set.

Metrics: `{strict, relaxed} × hit@{1, 10, 50}`; retrieval depth 50 per request. Declared deviations: (a) no official evaluator used or approximated; (b) matching on titles, not on the unresolvable `paperId`; (c) `hit@k` is host-chosen — SAGE states no rank cutoff; (d) the open-ended tier is **not run**, its weighted recall needing tier weights the README never states; (e) the authors' closed-index setting is not reproduced, so this is the open-world setting, not theirs.

## 5. Precision, and the gate this family serves

`family_n_policy.sage_scientific_retrieval` reads "Gate family; achieved precision reported, no primary." So: N = 385, `TIER_B_committed`, worst-case Wilson half-width **0.0497**, exceeding `delta_sup` 0.03 — the family is labelled **UNDERPOWERED** as mandated. The label is descriptive: no promoted primary rests here either way. Intervals come from `research/paper-programme-v1/protocols/publication_stats.py` (`wilson_interval`, `paired_bootstrap_difference_ci`, 10000 resamples, seed 20260816), imported by path because the plan sets `reimplementation_forbidden`; a test asserts the library function is the one called rather than that a local copy agrees with it.

The family's role is `lexical_baseline_promotion_gate` — a real lexical baseline, not a straw man. **Pre-declared before any score existed** (amended while the run was still executing, recorded as such): the gate rests on `strict_hit_at_10`, three-state on the paired interval for `governed − lexical` — entirely below zero → `BASELINE_AHEAD`, the gate **fires**; entirely above → `CANDIDATE_AHEAD`; containing zero → `CANNOT_DISCRIMINATE`, informing the gate in **neither** direction, additionally flagged `floor_artifact` when both point estimates are zero. No ordering is claimed in the third state: a plain `lexical >= governed` boolean is vacuously true when both rates are zero and would report the gate as firing on a comparison that distinguished nothing.

`hit@10` rather than `hit@1` because hit@1 is not ordering-neutral between these systems — the single-backend system's early candidates carry Crossref's ranking, while the multiroute system fills first slots from whichever route answered first, and its route-1 backend often returns nothing. hit@1 is still reported, with that asymmetry recorded in the summary.

The frozen gate `sage_lexical_gate` (`bm25_keyword`) stays **OPEN** regardless: it is defined over SAGE's own corpus, so provider-side ranking over three external indices can inform it, never close it.

Stage integrity: `score` refuses unless the run manifest's `candidate_input_sha256` equals the split manifest's `custody.public_sha256` and the gold file hashes to the value that split declared, so a stale run cannot be scored against a fresh split.

## 6. Contamination

Gold is public plaintext in the same record as the query, so exposure is measured, not assumed away. Offline on N = 385: mean gold-title token overlap with the query **0.532** (median 0.533); **234/385** at or above half; **5** records where every gold token appears somewhere in the query; longest common token run mean 2.39, max 8, with **22** records sharing a run of five or more; **0** records contain the gold title verbatim.

Reading: queries describe the target by year, venue, title shape, a figure or table, and co-citation structure, and they quote the titles of *other* papers — so the overlap is mostly shared topical vocabulary, and the zero verbatim count is what would otherwise make declared exact match a string-recovery exercise. Whether OpenAIRE, DBLP or Crossref indexed the SAGE repository itself is **CANNOT_CHECK**: not observable through their search APIs, and not the same as absent.

## 7. Valid and invalid metrics with no retrieval corpus

| Metric | Status | Why |
|---|---|---|
| `{strict,relaxed}_hit_at_{1,10,50}` | **VALID (declared)** | Denominator is the task set; gold is one known target |
| achieved precision / tier | **VALID** | From N and the frozen tier table |
| route independence verdicts; per-route retrieved / novel digests | **VALID** | Structural or content-digest identity; no gold needed |
| `route_stop_false_{positive,negative}_rate` | **CANNOT_CHECK** | Need B8 `oracle.route_residual_yield` under a frozen index |
| `premature_task_closure_rate` | **CANNOT_CHECK** | Needs B10; the fixed budget declares no closure |
| `complete_gold_recall` | **CANNOT_CHECK** | No complete gold set over an unpublished corpus |
| `precision`, `screening_recall` | **CANNOT_CHECK** | Relevance beyond the single target is undefined |
| `unique_relevant_per_route`, `marginal_relevant_gain` | **CANNOT_CHECK** | Require a relevance oracle |
| any official SAGE metric | **NOT_OBTAINABLE** | No evaluator, no corpus, no stated tier weights |

`CANNOT_CHECK` is distinct from a measured zero, and `score` emits it as such rather than a convenient number. Binding B6 (`gold_set_complete`) is declared **true** for short-form: the task asks for one target and upstream ships exactly one gold record per query, so the denominator is 1 by construction — a declared reading of a targeted-identification task, not an upstream statement.

## 8. Backend availability and an open obligation

Direct probe, 2026-08-17: OpenAIRE 200, DBLP 200, Crossref 200, **Semantic Scholar 429 keyless**, matching the note already in `src/orion/knowledge/rate.py`. Under `exclusion_policy.retained_always`, provider unavailability is **retained, never excluded**, and is not evidence of absence. Resolving SAGE's `paperId` gold to titles directly — which would remove the need for the title join in §4 — remains an **open obligation** requiring a Semantic Scholar key this paper does not use.

Rate discipline: `RateGate` with per-provider budgets. Crossref uses the existing published `crossref_list` budget (1.0 s). OpenAIRE (1.0 s) and DBLP (1.5 s) publish no verifiable per-second figure, so they follow the `europepmc` precedent already in that module — `basis=ASSUMED`, stated as assumed, deliberately conservative, injected per run rather than added to the shared table.

**No arXiv request is issued by any command in this family**, and no credential is read anywhere.
