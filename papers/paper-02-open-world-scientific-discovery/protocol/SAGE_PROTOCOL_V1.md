# SAGE short-form as an external task family under declared scoring

Binds `PROTOCOL_V1.json` / `STATISTICAL_PLAN_V1.json`. Runner:
`scripts/run_sage_shortform.py`. Tests: `tests/unit/p2/test_p2_sage_shortform.py`.

Upstream `HughieHu/Sage` at `bc62257a13d81ae233ecbd508037614746d2776b`. No LICENSE at that
revision, so records are fetched and hashed but never vendored into this repository.

## 1. What is and is not available

Obtainable: 600 short-form records across four domain files (150 each), fields `paper_id`,
`paper_title`, `complete_query`, `ground_truth{paperId,title}`.

Not obtainable: the 200k retrieval corpus and any official evaluator. Neither is published, and no
budget changes that. **Every number this family produces is a declared deviation and none may be
labelled official.** Gold identifiers are Semantic Scholar `paperId`s that this paper cannot resolve
keyless, so the join is normalised-title matching, declared in §4.

Framing dependency, recorded because it is not yet on `main`: the usability verdict that keeps this
family in the paper lives on branch `claude/p2-sage-usability` — `notes/access/SAGE_USABILITY_REVISION_3.md`
(blob `0f10ddfc2aebdcc5fe24b5adfe5734b5a7634d3c`) and the `usable_task_family_under_declared_deviation`
key of that branch's `EXTERNAL_ACCESS_AUDIT_V1.json` (blob `3e15c6d682363222810dfae43fdd4e7e075ed172`).
`main`'s audit still records `sage_scientific_retrieval: NO_ARTIFACT_MISSING`. This protocol assumes
that branch merges; if it does not, the family reverts to struck and this document is void.

## 2. Parsed inventory (re-verified on every `prepare`, not read off a README)

| Quantity | Value |
|---|---|
| Records parsed | 600 (150 per domain file) |
| Records with `ground_truth` | **599** |
| Records without `ground_truth` | **1** — `healthcare[63]`, `paper_id bbecae5da4f5a7bc59e560f253fe0c3a4d305884` |
| `paper_id` == `ground_truth.paperId` and `paper_title` == `ground_truth.title` | 599/599 |
| Distinct query strings | 587 (13 duplicate groups, **all agreeing on gold**) |
| Eligible tasks after dedup | **586** |
| Distinct gold targets in the eligible pool | 584 (2 targets answer two queries each) |

Two corrections to the briefing this lane received, both verified above: gold is present on 599
records, not 600; and `paper_id`/`paper_title` **are** gold under another name, so a custody check
that hid only `ground_truth` would have leaked the answer twice.

The single gold-less record is excluded from the eligible pool before any subsample is drawn, and is
recorded in the split manifest with its id. That is 1/600 = 0.17%, far inside the frozen 0.05
exclusion budget. Its `paper_title` would in fact be a well-supported gold fallback (599/599
equality), but using it would be a host-invented answer, so it is excluded instead.

Duplicate-query records are dropped because identical query text with identical gold is the same
task twice: keeping both inflates N and understates variance. `prepare` **raises** if any duplicate
group disagrees about its gold, since declared exact match would then have no defined target.

Aggregation unit is the **query**. Two gold targets answer two queries each, so tasks are not fully
independent Bernoulli trials; that count is reported alongside every interval rather than assumed away.

## 3. Custody split, subsample, budgets

`prepare` is the only command permitted to read gold. It emits a public candidate file whose records
carry exactly `{task_id, domain, complete_query}` and a host-only gold file. It asserts that no key
naming an answer (`ground_truth`, `paper_id`, `paper_title`, `paperId`, `gold`, `answer`, `target`)
appears anywhere in the candidate file, at any nesting depth. `run` re-checks the same property on
its input and refuses a file carrying gold; it has no parameter that could accept a gold path.

Subsample: seeded (`20260816`), stratified across the four domains, **N = 385** (97/96/96/96).
Frozen before scoring: task ids and their sha256 `c5c9b81e00a66c088305eb6a52d7e7f4f2d6894a2fb6561e7559522c78a122f1`.

A separate 8-task pilot is drawn **first** and is disjoint from the test set by construction. The
frozen budget policy requires the cap to come from a declared pilot and forbids pilot tasks from the
final test; the pilot was also where the derivations in §5 were fixed.

Budget: 3 provider requests per task per system. Maximum pilot consumption was 3, so the cap is the
next rung of the frozen `query_count` ladder, **10**, identical for both systems and written into
the run manifest `resource_limits` before any outcome is accessed. `run` **raises** on a cap or
budget mismatch, because the frozen policy calls such a family INVALID rather than merely noteworthy.

Why 385 and not the full 586: both land in `TIER_B_committed` and both are labelled `UNDERPOWERED`
(§6), so the extra 201 tasks would change neither the tier nor the label, at 1.5x the load on three
keyless public APIs. Even the whole eligible pool cannot reach `TIER_A_full` (N ≥ 1068).

## 4. Declared scoring rules

Both variants are ordered transform lists, named in code as `STRICT_TRANSFORMS` / `RELAXED_TRANSFORMS`.

**strict** — normalised equality. Transforms, in order: NFKD; drop combining marks; map typographic
quotes and dashes to ASCII; casefold; every run of non-`[a-z0-9]` to a single space; collapse and
strip. So `"Graph Title."` matches `"Graph Title"`, which matters because DBLP appends a full stop.

**relaxed** — strict, or the gold token run appears as a contiguous token subsequence of the
candidate. This absorbs publisher-appended subtitles and trailing artefacts. Gold titles shorter
than three tokens are not relaxed. Truncating titles at the first colon was **rejected**: it
collapses `"ReConcile: ..."` to `"reconcile"`, and the collision check below is what rejected it.

Validation before any scoring: both variants are run over the gold set alone. On the N = 385
subsample, **0 distinct gold titles share a strict normalised form** and **0 gold title is contained
in another** under relaxed. Neither variant is ambiguous on this task set.

Reported metrics: `{strict, relaxed} × hit@{1, 10, 50}`. Retrieval depth is 50 per request.

Deviations from upstream, each declared: (a) no official evaluator is used or approximated;
(b) matching is on titles, not on Semantic Scholar `paperId`, which is unresolvable keyless here;
(c) `hit@k` is host-chosen — SAGE never states a rank cutoff; (d) the open-ended tier is **not run**,
because its weighted recall needs tier weights the README never states; (e) the authors' closed-index
setting is not reproduced, so this is the open-world setting, not theirs.

## 5. Systems and route derivations

Three derivations draw on genuinely different parts of the query — the target's described content,
its bibliographic shape, and the citation neighbourhood it sits in:

| Route kind | Derivation | Signal |
|---|---|---|
| `CURRENT_VOCABULARY` | `content_vocabulary` | 4 salient terms, double-quoted spans removed first |
| `LEXICAL_VARIANT` | `bibliographic_shape` | title-shape hint + venue + year + 3 terms |
| `CITATION_NEIGHBORHOOD` | `citation_neighbourhood` | the co-cited titles the query quotes verbatim |

Double-quoted spans are removed from the content route because they are the titles of **other**
papers the target co-cites; searching them retrieves those papers instead. Four content terms is a
pilot-measured value, not taste: OpenAIRE conjoins keyword terms, and one pilot probe returned
16871 / 407 / 18 / 1 / 0 results at 2 / 3 / 4 / 5 / 8 terms.

- `sage_governed_multiroute` — system under test. Derivation *i* to backend *i* over OpenAIRE, DBLP
  and Crossref, dedup on content digest, route control via `FrozenRouteControlPolicy`.
- `sage_single_backend` — matched-budget internal contrast. The **same three derivations**, all on
  Crossref (`query.bibliographic`, the strongest general bibliographic matcher of the three). Only
  the backend allocation differs, so the contrast isolates backend diversity rather than confounding
  it with a weaker query strategy.

`sage_single_backend` is **not** a frozen baseline for this family. The frozen SAGE baseline set is
`bm25_keyword` (gate), `dense_retrieval` and `sparse_dense_hybrid`; `agentic_single_route` is not
listed for SAGE. It therefore cannot be the `strongest_matched_baseline`, whose frozen definition
draws from the frozen set only.

Dedup is on a normalised-title digest, never a DOI or DBLP key, per bindings B4/B7: a source that
re-mints ids makes two routes that found one paper look disjoint and inflates every unique-yield
number built on overlap. Route independence is **constructed and then checked** by `assess_pair`,
not asserted — the pilot returned `INDEPENDENT` for all 24 multiroute pairs and `SHARED_BACKEND` for
all 24 single-backend pairs, which is the intended structural difference.

## 6. Precision, and the gate this family actually serves

`family_n_policy.sage_scientific_retrieval` reads "Gate family; achieved precision reported, no
primary." So: N = 385, achieved tier `TIER_B_committed`, worst-case Wilson half-width **0.0497**,
which exceeds `delta_sup` 0.03, so the family is labelled **UNDERPOWERED** as the plan mandates. The
label is descriptive here — no promoted primary rests on this family either way.

Intervals come from `research/paper-programme-v1/protocols/publication_stats.py`
(`wilson_interval`, `paired_bootstrap_difference_ci`, 10000 resamples, seed 20260816). The plan sets
`reimplementation_forbidden`, so the library is imported by path and a test asserts the library
function is the one actually called rather than that a local copy agrees with it.

`non_primary_bearing_families.sage_scientific_retrieval` gives this family the role
`lexical_baseline_promotion_gate` — it exists to run a real lexical baseline, not a straw man.
**Pre-declared before scoring:** if `sage_single_backend` matches or beats
`sage_governed_multiroute`, that is the gate firing and is reported as such, not as a footnote.

The frozen gate `sage_lexical_gate` (`bm25_keyword`) nonetheless stays **OPEN**. It is defined over
SAGE's own 200k corpus; provider-side ranking over three external indices can inform it and cannot
close it.

## 7. Contamination

Gold is public plaintext in the same record as the query, so exposure is measured, not assumed away.
Measured offline on the N = 385 subsample: mean gold-title token overlap with the query **0.532**
(median 0.533); **234/385** records at or above half; **5** records where every gold-title token
appears somewhere in the query; longest common token run mean 2.39, max 8, with **22** records
sharing a run of five or more. **0** records contain the gold title verbatim.

Reading: the queries describe the target by year, venue, title shape, a figure or table, and
co-citation structure, and they quote the titles of *other* papers. The overlap is therefore mostly
shared topical vocabulary, and the zero verbatim count is what would otherwise make declared exact
match a string-recovery exercise. Whether OpenAIRE, DBLP or Crossref indexed the SAGE repository
itself is **CANNOT_CHECK** — not observable through their search APIs, and not the same as absent.

## 8. Valid and invalid metrics with no retrieval corpus

| Metric | Status | Why |
|---|---|---|
| `{strict,relaxed}_hit_at_{1,10,50}` | **VALID (declared)** | Denominator is the task set; gold is one known target |
| achieved precision / tier | **VALID** | From N and the frozen tier table |
| route independence verdicts | **VALID** | Structural, from backend and derivation identity |
| per-route retrieved / novel digests | **VALID** | Content-digest identity, no gold needed |
| `route_stop_false_positive_rate` | **CANNOT_CHECK** | Needs B8 `oracle.route_residual_yield` under a frozen index |
| `route_stop_false_negative_rate` | **CANNOT_CHECK** | Same |
| `premature_task_closure_rate` | **CANNOT_CHECK** | Needs B10, and the fixed budget declares no closure |
| `complete_gold_recall` | **CANNOT_CHECK** | No complete gold set over an unpublished corpus |
| `precision`, `screening_recall` | **CANNOT_CHECK** | Relevance beyond the single target is undefined here |
| `unique_relevant_per_route`, `marginal_relevant_gain` | **CANNOT_CHECK** | Require a relevance oracle |
| any official SAGE metric | **NOT_OBTAINABLE** | No evaluator, no corpus, no stated tier weights |

`CANNOT_CHECK` is a distinct outcome from a measured zero, and `score` emits these as
`CANNOT_CHECK` rather than reporting a convenient number. Binding B6 (`gold_set_complete`) is
declared **true** for short-form: the task asks for one target and upstream ships exactly one gold
record per query, so the denominator is 1 by construction. That is a declared reading of a
targeted-identification task, not an upstream statement.

## 9. Backend availability, and an open obligation

Verified by direct probe on 2026-08-17: OpenAIRE 200, DBLP 200, Crossref 200. Semantic Scholar
returned **429 keyless**, matching the note already in `src/orion/knowledge/rate.py`. Under
`exclusion_policy.retained_always`, provider unavailability is **retained, never excluded**, and it
is not evidence of absence. Resolving SAGE's Semantic Scholar `paperId` gold to titles directly —
which would remove the need for the title join in §4 — remains an **open obligation** requiring a
Semantic Scholar key this paper does not use.

Rate discipline: `RateGate` with per-provider budgets. Crossref uses the existing published
`crossref_list` budget (1.0 s). OpenAIRE (1.0 s) and DBLP (1.5 s) publish no verifiable per-second
figure, so they follow the `europepmc` precedent already in that module — `basis=ASSUMED`, stated as
assumed, deliberately conservative, injected per-run rather than added to the shared table.

**No arXiv request is issued by any command in this family**, and no credential is read anywhere.
