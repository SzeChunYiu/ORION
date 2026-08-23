# P2 open-world acquisition successor — prospective freeze

- **Record id**: `P2_OPEN_WORLD_ACQUISITION_FREEZE`
- **Date**: 2026-08-22
- **Status**: `FROZEN_BEFORE_EXECUTION`
- **Machine-readable twin**: `P2_OPEN_WORLD_ACQUISITION_FREEZE_2026-08-22.json`
- **Runner**: `src/orion/study/p2/acq_campaign.py`
- **World**: `src/orion/study/p2/acq_world.py`
- **Mechanics**: `src/orion/study/p2/acq_mechanics.py`
- **Parameter digest (`parameters_sha256`)**: `ad7e4c6afd66943693ae732b2dde9131aa5bddd13b5632dc97c38223149f769a`
- **Expected result artifact**:
  `../evidence/successor_results/P2_OPEN_WORLD_ACQUISITION_RESULT_2026-08-22.json`
- **Claim scope**: `CONSTRUCTED_REPRODUCTION_ONLY__DEVELOPMENT_EVIDENCE`

This document, its twin and the three modules above were written, dated and
hashed **before the world was generated and before any arm was executed**. The
world preconditions in §4 were evaluated on the corpus alone, before any query
was issued. Every threshold in §5 is set here. Nothing may be retuned after a
number is seen; if a gate fails, the failure is the result.

---

## 1. What this reopens, and under which rule

`JOURNAL_READINESS_V2.md` closed the V2 acquisition campaign at
`P2_V2_ACQUISITION_NOT_PROMOTED` and states that a reopen

> must be a materially new prospectively frozen campaign — e.g. a new independent
> development basis, a genuinely stronger runnable retrieval implementation, or a
> materially different external benchmark/authority.

This freeze claims the first two and neither of the others. It is an **offline
development** campaign. It cannot promote L1–L4, it does not touch the burned
24-task Wide development slice, it does not open the unexecuted 48-task fresh
confirmation (task-ID hash `f4af8ac3…`), and the manuscript's authorized
scientific terminal remains `P2_NARROWED`.

### 1.1 Why the committed offline gold world is not the new basis

The obvious candidate for a fresh basis was a new seed of
`papers/paper-02-open-world-scientific-discovery/evidence/offline_gold/`, whose
generator `corpus.build_world(seed)` is seed-parameterised. It does not work, and
the reason is recorded here rather than discovered later by a reader:

`corpus._TOPIC_PLANS` is a module constant. The topic labels, required concepts,
lexical/semantic/reformulation/restricted access keys and every gold record's
title and abstract are fixed at import time; `build_world`'s `seed` varies only
venue, year, author block, and the noise concept tags of non-gold records.
Comparing `build_world(20260816)` with `build_world(11223344)`: identical
document-id set, **0 title differences, 0 access-key differences, 0 question
differences, 0 protected-gold differences**. A new seed is therefore *not* a new
development basis for anything that reads document text or issues a query. This
is pinned by `test_committed_offline_gold_world_is_seed_invariant_for_retrieval`.

A second reason rules the same artifact out independently: it is not a
query-formulation benchmark, and `OFFLINE_GOLD_WORLD_V1.md` says so — probe
vocabularies are published and screening is deliberately easy. Its abstracts
embed the full topic label, so a free-text derivation over its text is close to
saturated, and ORION's recorded recall on it is already 0.979487.

The basis used instead is a **new constructed world** (§3), generated from seed
`20260822`, in the pattern the programme already sanctioned for
`P2_LEXICAL_ECHO_SUCCESSOR_FREEZE_2026-08-21`.

---

## 2. The negative under repair, read from the archive rather than from memory

The authoritative artifact is
`../evidence/external_results/P2_V2_ACQUISITION_DEV3R_RESULT_2026-08-18.json`,
supported by `P2_V2_WIDE_BOUNDED_STAGE_DIAGNOSTIC_2026-08-18.json`.

| Quantity | Archived value |
|---|---|
| provider calls per task | 3 (both arms, `72/72 OK`) |
| results per call | 20 |
| candidate cap | 20 |
| `mean_candidates_returned` | **20.0**, both arms |
| baseline `avg_recall` | 0.051422 |
| candidate `avg_recall` | 0.044213 |
| `zero_hit_tasks` | 19 / 24, both arms |
| per-task gold size | 2 to 21 |
| dominant attributed failure | `CANDIDATE_GENERATION` |

Two facts in that table constrain what may honestly be modelled, and both cut
against a natural but wrong reading of the negative:

1. **The queries were not coming back empty.** `mean_candidates_returned = 20.0`
   on every task. The failure is twenty topically-wrong records filling a hard
   cap, not an over-constrained conjunction returning nothing.
2. **The archived baseline was not a naive six-way `AND`.** Its three calls, from
   `scripts/run_autoresearchbench_wide_acq_dev3.py`, were `BASE_PRIMARY`
   (`(all:a AND all:b) OR (all:b AND all:c) OR …` over four adjacent pairs),
   `BASE_CORE` (a two-term `AND`) and `BASE_BROAD` (a plain `OR` over six
   tokens). A fully disjunctive rung was already in the baseline plan and it
   still returned 0.051422.

Any reproduction that made the baseline fail by emptying its result set would
therefore be modelling a failure the archive says did not occur. The world in §3
is built so the baseline returns a **full** candidate list and misses anyway.

A third archived fact sets the repair's target. The stage diagnostic records
tasks — `arb-wide-0253` among them — where the provider returned a gold
identifier (`governed_raw_route_gold_hits.arxiv = 1`) and the task still finished
with `governed_hit_count = 0`. Across the slice, the arXiv route's raw results
carried 7 gold identifiers while only 4 tasks ended with any hit at all. Gold was
acquired and then lost at the merge. That is a **selection** defect sitting
downstream of acquisition, and it is one of the two things `D5` repairs.

---

## 3. The world

Generated by `acq_world.build_acquisition_world(20260822)`. Every parameter is in
the twin's `parameters.world` block and is hashed into `parameters_sha256`.

### 3.1 Strata

- **Scaffold vocabulary** — six framing words, all of which survive
  `arb_runtime._STOPWORDS` so they genuinely enter a shipped query. Sprayed with
  repetition across most non-gold records, so their document frequency is high
  corpus-wide.
- **Domain vocabulary** — 110 content terms. Each is shared by roughly a dozen
  topics, so no single content term identifies a task.
- **Variant vocabulary** — 50 alternate surface forms, disjoint from the domain
  lexicon, used only by the two vocabulary-gap families.
- **Neutral vocabulary** — 20 connectives present in every stratum and in **no**
  question, so document length discriminates nothing and they never enter a query.

### 3.2 Per task

Five content terms and two scaffold terms are drawn. Gold records carry **three
of the five** content terms; the adjacent neighbourhood (24 records) carries
**two**. Gold records carry reference edges into each other, so
`D3_CITATION_NEIGHBORHOOD` is a live route rather than one that can never return
anything. Gold set size is 3–6 per task, inside the archived 2–21 range.

The two structural assumptions this rests on are stated plainly because they are
the study's exposure, not its result:

- **A1. A relevant paper does not recite every term of the asker's question.**
  Three of five, not five of five. This is why a wide conjunction over the
  question's vocabulary is unsatisfiable, and it is an assumption about the live
  setting, not a finding of this study.
- **A2. Gold records do not carry the question's framing vocabulary.** This is
  `echo_world`'s already-validated property 2 (`the needle does not contain the
  apparatus word`), inherited rather than re-invented. It is **assumed** of the
  live setting on the strength of
  `DEEP_ZERO_HIT_STAGE_ATTRIBUTION_2026-08-17.json` and is not established here.

### 3.3 Families

| Family | N | What it is for |
|---|---:|---|
| `distinguishable` | 120 | The primary family. Gold is separable from its neighbourhood, but only by *coordination-level* evidence over gated terms — how many distinct topic terms a record agrees with. |
| `undistinguished` | 40 | **Negative control.** Gold is written exactly like an adjacent record: same term count, same apparatus spray. Nothing lexical separates it. Pre-committed: no arm, successor included, may lift recall here. |
| `well_posed` | 40 | No-harm control. The question carries no scaffold vocabulary and gold carries four of five terms, so the baseline should do well and the successor must not undo that. |
| `variant_gap` | 40 | Half of each task's gold is written in variant surface forms, with three bridge records per task that use both vocabularies. |
| `no_bridge` | 40 | Identical to `variant_gap` with the bridge records removed. Specificity control for grounded expansion. |

The `undistinguished` family is the point of §7 and exists so that a positive
result on `distinguishable` cannot be read as a claim about the live benchmark.

### 3.4 Question templates

Every connective word in both templates is in `arb_runtime._STOPWORDS`, so the
tokens a shipped derivation sees are exactly the placeholders. On the wide
template, `D1_CURRENT_VOCABULARY` at width 6 selects **two scaffold terms and
four content terms**; on the well-posed template it selects content terms only.
Pinned by `test_question_templates_yield_the_intended_query_composition`.

---

## 4. World preconditions

Evaluated on the corpus and tasks alone, before any query. A world failing any of
them is not the reproduction this document describes, and the runner reports no
arm numbers over it.

| Check | Requirement |
|---|---|
| **P1** | every scaffold term's df/N ≥ 0.20 |
| **P2** | every domain term's df/N ≤ 0.06 |
| **P3** | every task has ≥ 2 gold records |
| **P4** | on `distinguishable`, every gold record carries ≥ 3 distinct topic terms and no neighbourhood record carries more than 2 |
| **P5** | every task's neighbourhood is at least as large as the 20-result cap |
| **P6** | on `distinguishable`, no gold record carries any of its question's scaffold terms |

---

## 5. Arms, budgets, metric, statistic and gates

### 5.1 Budgets — matched, and taken from the archive

Three provider calls per task, twenty results per call, a twenty-candidate output
cap, for **every** arm. `run_arm` raises if an arm issues any other number of
calls. Query width is 6 for every arm, so the candidate gets no term-budget gift.

### 5.2 Arms

| Arm | Queries | Merge |
|---|---|---|
| **B0** `ARCHIVED_WIDE_LEXICAL_V3` | `BASE_PRIMARY` / `BASE_CORE` / `BASE_BROAD`, reimplemented from the archived script | round-robin |
| **B1** `SHIPPED_D1_D2_D3` | the three shipped `arb_runtime` derivations, unedited: D1 conjunctive, D2 free text, D3 citation seed | round-robin |
| **S2** `D5_GROUNDED_SPECIFICITY_LADDER` | the candidate (§5.3) | coverage-first |
| **A1** `D5_QUERIES_ROUND_ROBIN` | S2's queries | round-robin |
| **A2** `D1_TERMS_COVERAGE_MERGE` | D1's ungated terms through the ladder | coverage-first |
| **A3** `D5_NO_EXPANSION` | S2 without the grounded-expansion rung | coverage-first |

`arb_runtime`'s `D1`/`D2`/`D3` are **not edited** by this study. `D5` is added
alongside them, in a separate module, and B1 calls the shipped functions
directly.

### 5.3 The candidate mechanism, `D5_GROUNDED_SPECIFICITY_LADDER`

Derived from the three archived facts in §2, in the order they appear there.

1. **Ground.** Drop question tokens the index has never seen. `D1` never asks; a
   token absent from the collection contributes nothing to a disjunction and
   empties any conjunction it enters.
2. **Gate.** Drop tokens in more than 5% of the collection. This is `D4`'s
   validated finding, inherited at `D4`'s threshold
   (`echo_mechanics.INCIDENTAL_DF_FRACTION`) and deliberately **not** re-fitted
   here. If the gate empties the term set the mechanic degrades to the grounded
   set ranked by idf — the exposure `P2_LEXICAL_ECHO_SUCCESSOR_RESULT_2026-08-21`
   §4 named and left untested.
3. **Rank by discriminativeness**, not by within-question repetition.
4. **Bound the conjunction width by arithmetic.** A conjunction over a prefix of
   length *k* matches `N · Π df(t)/N` documents in expectation. Take the widest
   prefix, between 2 and 4 terms, whose expectation is ≥ 5. Independence
   under-predicts co-occurring topical terms, so the estimate errs toward
   accepting a width the collection can satisfy. Refusing prospectively costs
   nothing; discovering over-constraint by issuing the query costs one of three
   calls.
5. **Descend a three-rung specificity ladder** inside the same three-call budget:
   the satisfiable conjunction, then the full gated disjunction, then one
   expansion rung. Rungs are issued unconditionally, never conditioned on what
   the previous rung returned, because an arm whose call count depends on the
   outcome is no longer matched.
6. **Bridge vocabulary from the corpus, not from a model.** The third rung adds
   relevance-model terms — `w(t) = (fraction of feedback records carrying t) ·
   idf(t)`, subject to the same apparatus gate — drawn from the top feedback
   records of the first two rungs. This can only reach a record sharing no token
   with the question when the collection itself holds a record using both
   vocabularies. Gate G5 checks that rather than assuming it.
7. **Merge coverage-first instead of round-robin.** Order the whole pooled set by
   how many *distinct* gated query terms each candidate agrees with, then by an
   idf-weighted saturating score with expansion terms discounted, then by id.
   Coordination level first, magnitude second. Low-coverage candidates are
   demoted, never deleted, so the rule cannot manufacture recall by hiding
   documents. This is the repair for the archived observation that gold was
   retrieved raw and then lost at selection.

`D5` uses the question text and index document frequencies. It never reads a
topic, a gold set, a family label, a concept tag or an access key.

### 5.4 Primary outcome and statistic

**Primary outcome**: mean recall at the 20-candidate cap on the
`distinguishable` family, S2 versus B0. Recall is the archived campaign's own
primary metric.

**Statistic**: exact two-sided sign test on paired per-task recall (ties dropped),
plus a 95% percentile paired bootstrap over tasks, 10,000 resamples, seed
20260822.

### 5.5 Gates

| Gate | Statement | Blocking |
|---|---|---|
| **G1 REPRODUCTION** | on `distinguishable`: B0 mean recall ≤ 0.12 **and** B0 zero-hit fraction ≥ 0.60 **and** B0 mean candidates returned ≥ 18 | yes |
| **G2 CANDIDATE** | on `distinguishable`: S2 − B0 mean recall ≥ +0.30 **and** S2 mean recall ≥ 0.40 **and** sign-test *p* < 0.01 **and** bootstrap 95% lower bound > 0 | yes |
| **G3 MARGIN OVER SHIPPED** | on `distinguishable`: S2 − B1 mean recall ≥ +0.10 | yes |
| **G4 NO HARM** | on `well_posed`: S2 mean recall ≥ max(B0, B1) − 0.05, vacuity floor max(B0, B1) ≥ 0.30 | yes |
| **G5 BRIDGE SPECIFICITY** | on `no_bridge`: S2 − A3 mean recall ≤ +0.10 | no |
| **G6 UNDISTINGUISHED CEILING** | on `undistinguished`: S2 − B0 mean recall ≤ +0.10 | no |

G1's thresholds are calibrated to the archived numbers (0.051422 recall, 19/24 =
0.7917 zero-hit, 20.0 candidates returned) with slack, not chosen to be easy: a
world in which the baseline does *well* is not a reproduction and voids the
study.

G3 is blocking on purpose. If the entire repair is already available from the
shipped `D1`/`D2`/`D3` under a different merge, then the candidate is not a
materially stronger *mechanism*, and this freeze commits in advance to reporting
that instead.

### 5.6 Verdict rule

- ¬G1 → `REPRODUCTION_FAILED__NO_CANDIDATE_CLAIM`
- G1 ∧ G2 ∧ G3 ∧ G4 → `MATERIALLY_STRONGER_MECHANISM_ON_CONSTRUCTED_REPRODUCTION`
- G1 ∧ G2 ∧ G4 ∧ ¬G3 → `GAIN_OVER_ARCHIVED_BASELINE_ONLY__NOT_MARGINAL_OVER_SHIPPED`
- G1 ∧ G2 ∧ ¬G4 → `GAIN_ON_MODE__HARM_OFF_MODE__NO_CANDIDATE_CLAIM`
- otherwise → `CANDIDATE_NOT_VALIDATED__NEGATIVE_STANDS`

---

## 6. One run

One world, one seed, one execution of every arm. There is no second seed and no
second measurement under this freeze. A further attempt requires a further seed
and a further prospective freeze, and the fact that a further attempt was taken
must be reported.

---

## 7. What a pass would and would not license

**Would license.**

1. That a candidate-generation mechanic materially stronger than both the
   archived Wide lexical baseline and the shipped `arb_runtime` derivations
   exists, is runnable, is deterministic, and operates inside the archived
   campaign's own budgets.
2. That the repair decomposes: the ablations A1/A2/A3 separate the query half,
   the selection half and the bridging half, so a reader is told *which* part
   carries the gain rather than being handed a black box.

**Would not license.**

1. Any statement about mean recall on the official AutoResearchBench Wide
   benchmark. This world is synthetic; no provider was called; external providers
   are unreachable from the execution environment.
2. Promotion of L1 `P2_EXTERNAL_MECHANISM_SUPPORTED` or L2
   `P2_EXTERNAL_DISCOVERY_SUPPORTED`. Both require an admissible confirmatory
   external result and neither is opened here.
3. Any revision of `P2_V2_ACQUISITION_DEV3R_RESULT_2026-08-18` or of
   `JOURNAL_READINESS_V2.md`'s terminal. That negative stands.
4. Any change to the authorized scientific terminal, which remains `P2_NARROWED`.
5. **Any inference that the live Wide gold is repairable by this mechanic.** The
   `undistinguished` family exists precisely because it may not be: if the live
   gold references are not separable from adjacent literature by surface lexical
   evidence, then G6's ceiling is the live ceiling and no query-derivation upgrade
   moves it. This study cannot tell which case the live benchmark is in, because
   the benchmark bundle is not present in this environment and the providers are
   unreachable.

The correct summary of a pass is therefore: *the precondition the failed campaign
lacked — a materially stronger candidate generator, ready to run — is now met,
and the question of whether the live setting has the structure this mechanic
needs is open and separately testable.*

---

## 8. Environment boundary

- `export.arxiv.org`, `arxiv.org` and `api.openalex.org` are unreachable from the
  execution environment (curl exit code 000).
- The AutoResearchBench bundle (`ORION_ARB_BUNDLE`) is not present.
- No provider call was made, attempted or simulated as if made.
