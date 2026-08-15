# Retrieval and stopping rules — absorbed external evidence (v0)

**Status:** SOURCE_PROJECTION. Nothing here mints ORION authority. Every claim is
attributed; vendor self-reports are marked as such and are never treated as
measurement.

**Frame:** before ORION builds a literature-retrieval layer and finalizes its
bounded-saturation criterion, what has the field already established, measured,
or failed at?

## 1. The gap ORION is actually aimed at

Of roughly seventeen autonomous research / deep-research systems surveyed,
**exactly one stops on an estimate of how much relevant literature remains
unfound** (Undermind, which fits an exponential discovery curve
`f = 1 − e^(−n/τ)` and surfaces the estimated completeness fraction).

Everything else stops on one of: a fixed step count, a wall-clock or token
budget, an undisclosed internal budget, or an LLM asserting that it has enough.
PaperQA2 — the system with the strongest published accuracy claim — ships with
`agent.max_timesteps = None` and empirically performs **1.26 ± 0.07 searches per
question**.

This is the same distinction ORION draws between a resource-bounded stop and a
saturation claim, and it is currently unoccupied territory.

## 2. Prior art ORION must not re-derive

Recall-estimating stopping rules were solved statistically in
technology-assisted review long before agents rediscovered a special case:

- capture–recapture as a search stopping rule (Kastner et al., *J Clin
  Epidemiol*; DOI unverified here — CANNOT_CHECK);
- **Chao's estimator as a TAR stopping criterion** — arXiv:2404.01176;
- **confidence-based stopping methods for systematic reviews** —
  arXiv:2606.15380;
- SAFE heuristic (doi:10.1186/s13643-024-02502-7) and statistical stopping
  criteria (doi:10.1186/s13643-020-01521-4).

**Consequence for `kernel/saturation.py`:** the current 7-coordinate growth
vector is a *flatness* rule, which belongs to the weak family above. Flatness
answers "did this round add anything"; it does not answer "how much is left".

**Superseded within this record.** An earlier pass concluded "add a coverage
estimator, reported as diagnostic". Section 8b withdraws that: under adaptive
sampling Chao1 and Good–Turing fail toward *false confidence*, and with a single
adaptive stream Chao1 degenerates outright. The corrected instruction is
stronger — **no coverage estimator may be added until independent capture
occasions are constructed**, because a diagnostic that is biased toward "nearly
done" is worse than none. See §8b and residual 6.

## 3. Two ORION design decisions independently corroborated

**Evidence resolution is the highest-leverage integrity control.** Citation
hallucination is 78–90% without retrieval (OpenScholar, arXiv:2411.14199) and
**still 3–13% of URLs with retrieval**, measured over 221k URLs across ten
systems (arXiv:2604.03173) — deep-research agents hallucinate at *higher* rates
than search-augmented LLMs because they emit more citations. In the wild:
**≥146,932 hallucinated citations in 2025**, from 111M references across 2.5M
papers (arXiv:2605.07723). A URL-health checker cut non-resolving citations
**6–79× to under 1%**.

`kernel/evidence.py` already refuses any citation that does not resolve to a
real artifact at a pinned digest or named revision. That is the same control,
applied earlier — at admission rather than after generation.

**Information forgetting, not hallucination, is the dominant per-step failure.**
FutureSearch's regression over per-step failure rates (arXiv:2506.06287):
hallucination 0.014–0.159/step, repeated tool calls 0.044–0.293/step,
**information forgetting 0.090–0.356/step, the strongest negative predictor of
task score at coefficient −0.843**. Corroborated by OpenScholar's own ablation:
removing the self-feedback loop costs 0.2 correctness, removing the **reranker
costs 19.7 citation F1**. Retrieval quality and context retention beat
deliberation depth.

**Consequence:** the durable ledger and the `(source, digest, schema, frame)`
read receipt are aimed at the measured dominant failure, not the fashionable
one. Deliberation depth is explicitly not where to spend next.

## 4. What the field has failed at, with numbers

- **Vendor recall claims do not survive independent measurement.** Elicit
  self-reports 95.0% search recall; independent peer review measured **39.5%
  average sensitivity (25.5–69.2%) against 94.5% for the original expert
  searches** across four evidence syntheses (Lau & Golder,
  doi:10.1002/cesm.70050). The gap is a pipeline gap: the vendor measures
  semantic retrieval at large K, the study measures end-to-end output.
- **LLM agents lose to keyword search on discovery.** ResearchArena
  (arXiv:2406.10291), over a 12M-paper corpus: "LLM-based approaches
  underperform compared to simpler keyword-based retrieval methods."
- **Recall is the weakest measured dimension.** DeepResearch Bench II
  (arXiv:2601.08536), 9,430 expert rubrics: strongest systems satisfy **<50%**,
  deficits largest in Information Recall.
- **No externally validated in-loop oracle exists.** A coded survey of 26
  systems (arXiv:2608.05179): 83% release code, only 38% release seeds/traces,
  only 38% report any novelty verification; of nine closed-loop systems, none
  demonstrates an externally validated oracle.
- **The ideation advantage does not survive execution.** LLM-generated ideas
  were judged more novel than human ones by 100+ researchers (arXiv:2409.04109);
  when 43 experts spent >100 h each executing them, LLM ideas fell
  significantly further on novelty, excitement, effectiveness and overall
  (arXiv:2506.20803).
- **Self-evaluation inflates.** Agent Laboratory's automated reviewer scored its
  own papers 6.1/10 where humans scored 3.8/10 (arXiv:2501.04227).

## 5. Benchmarks — CORRECTED

**Superseded claim (retained, not deleted):** an earlier pass of this record
stated that almost no benchmark measures literature recall, with the
systematic-review literature as a vague exception, and marked CLEF-TAR /
SYNERGY / CSMeD as un-searched.

**That claim was too strong and is withdrawn.** A substantial recall cluster
exists under IR and systematic-review-automation vocabulary — *technology-
assisted review*, *WSS@95*, *screening prioritisation*, *inclusion recall* —
which shares almost no terminology with the agent-benchmark literature. The
vocabulary gap is why it does not surface from agent-side search. This is a
search-coverage failure of exactly the kind ORION's route families exist to
prevent, found in ORION's own research process.

**Four-tier rubric, adopted:**

- **T3 — genuine recall**, gold set is a protocol-derived *complete* relevant
  set: CLEF eHealth TAR, TREC Total Recall, SYNERGY, CSMeD, TrialReviewBench,
  MetaSyn, AgentSLR, Webis-SR4ALL-26, ResearchArena, ScholarQuest, PaSa,
  DeepScholar-Bench.
- **T2 — pooled/estimated recall**, real but incomplete denominator:
  SciFact-Open, DORIS-MAE, BrowseComp-Plus, PaperFindingBench.
- **T1 — top-k hit rate mislabelled recall**, gold set is *one* paper:
  LitSearch, CiteME, LitQA2-FullText-Search.
- **T0 — no document gold set**: everything else, including all of LitQA2,
  LAB-Bench, BixBench, ScienceAgentBench, CORE-Bench, PaperBench, SciCode,
  RE-Bench, ScholarQA-CS, HLE, DeepResearch Bench.

**Which gold standard to build against.** T3 splits again, and the fork is
decision-relevant. Sahu, Charlin & Pal (arXiv:2605.29234) show
bibliography-derived gold sets are weak ground truth: only **51% of human
citations are judged moderately relevant or higher**, against 86–88% for the
strongest AI re-rankers, and humans are **2.5× more likely to cite a direct
collaborator**. That invalidates the gold sets of ResearchArena,
DeepScholar-Bench, AutoScholarQuery, LitSearch and ScholarQuest. It does *not*
touch Cochrane-style included-study lists, which come from a registered
protocol, an exhaustive search and dual screening.

**Therefore: ORION's recall gold standard must be protocol-derived systematic-
review inclusion lists, never citation lists.** Concrete candidates —
SYNERGY (26 reviews, 169,288 records, 2,834 included, 1.67% prevalence) and
Webis-SR4ALL-26 (301,871 systematic reviews across all OpenAlex fields, with
reference lists and normalized executable Boolean strategies).

## 5b. The finding that most constrains ORION

**Agentic scaffolding has not been shown to improve literature recall.**
Replicated on two independent benchmarks:

- **ResearchArena** (12M papers): a naive survey-title query with BGE scores
  **R@100 = 0.2697, beating every LLM agent** — best agent 0.2547, STORM 0.1441.
- **MetaSyn** (422 expert-curated meta-analyses): one-pass RAG reaches
  **inclusion recall 51.2%** while GPT-Researcher gets **30.3%** and OpenDR
  **27.2%** — a ~20-point deficit for the agentic systems.

Related ceilings: DeepScholar-Bench, **no system above 31%** geometric mean and
all below 40% on Reference Coverage; AgentSLR, no model above field-level
F1 0.67 with up to **96× cost variance**; ScholarQuest R@100 0.314.

**Consequence, and it is a hard acceptance criterion:** ORION may not claim its
recursive loop improves literature discovery until it beats a naive
keyword-query baseline on a T3 benchmark. The prior from the evidence is that
scaffolding *loses*. Any ORION result that skips this comparison is
uninterpretable.

TrialReviewBench is the one recall benchmark with a published human baseline
(TrialMind 0.711–0.834 vs human 0.138–0.232) — useful precisely because it shows
a domain where automation genuinely wins, unlike the two above.

## 6. Retrieval-provider constraints (live-verified 2026-08-15/16)

These are engineering facts that shape the provider layer, not opinions.

| Provider | Hard constraint |
|---|---|
| arXiv | **0.33 req/s, single connection** (Terms of Use, across all your machines). Deep paging is broken: `start≥~10000` returns **HTTP 500**, not the documented 400. Strip the `vN` suffix before keying. |
| Semantic Scholar | **1 RPS even with a key.** Keyless returned 429 immediately on ordinary calls — unusable in production. `/paper/search` caps at 1,000 relevance-ranked results; bulk scrolls to 10M without nested citations. Best ID crosswalk hub. |
| OpenAlex | **API key now required (Feb 2026); `mailto` is ignored.** Keyless budget is $0.1/IP and 429s after ~3 list calls. `page × per_page ≤ 10,000`, then cursor. Abstracts are inverted indexes. |
| Crossref | Rate limits changed Dec 2025: list **1/s** public, 3/s polite; single-DOI 5/s, 10/s polite. `offset + rows ≤ 10,000`; cursor uncapped but tokens expire in 5 min. **Only ~23.9% of works have abstracts** — never the abstract source of record. |
| PubMed E-utilities | Hard ceiling **9,999** (docs say 10,000; implement against 9,999). History server does not lift it. |
| Europe PMC | Real cursor paging, no 10k wall, no key, `resultType=core` returns PMID+PMCID+DOI+abstract in one call. Strictly better than E-utilities for bulk biomedical. |
| Unpaywall | 100k calls/day; snapshots discontinued — use the OpenAlex snapshot. Treat Unpaywall and OpenAlex as **one** OA signal, not two independent ones. |

**Design consequence:** there are five mutually incompatible deep-paging models
(Crossref cursor, OpenAlex cursor behind a 10k wall, S2 bulk token behind a
1,000-result wall, E-utilities inside a 9,999 wall, arXiv effectively broken).
**Do not write one generic paginator**, and budget concurrency per provider
rather than from one global pool.

## 7. Residuals this absorption opens

1. **Coverage estimator missing.** `kernel/saturation.py` reports flatness with
   no estimate of unfound mass. Blocked on reconciling Chao/Good–Turing with
   adaptive sampling; must ship as diagnostic-only.
2. **No recall benchmark for ORION.** Every number above that is trustworthy
   comes from a gold set built by exhaustive human screening. ORION has none, so
   its own recall is currently CANNOT_CHECK, not "untested but probably fine".
3. **Reranking is unimplemented and is the highest-leverage retrieval
   component** (+19.7 citation F1 vs +0.2 for a feedback loop).
4. **Forgetting is unmeasured.** The dominant failure mode in the literature has
   no ORION metric. The ledger addresses it structurally; nothing measures it.

## 8. Stopping rules — ORION's criterion was already known, and measured

**The rule ORION implemented has three prior names.** "N consecutive rounds
with zero new items under a fixed frame" is Francis et al.'s **"10+3"**,
Guest/Namey/Chen's **new-information threshold with the threshold at 0%**
(doi:10.1371/journal.pone.0232076), and TAR's **IH50**. All three literatures
classify it as a heuristic. Guest et al.'s own bootstrap: at the 0% threshold
you have captured **87–89% of themes** (69–76% on their most heterogeneous
data). Callaghan et al. 2024 (doi:10.1186/s13643-024-02699-7) measured the
family directly: the 5th percentile of recall after 50 consecutive exclusions
was **53%**, and they conclude that arbitrary stopping criteria "have no place
in high-quality systematic reviews".

**ORION fails all three of that paper's stated requirements.** Not
target-bound (no recall level is referenced). Not statistically justified (no
confidence statement). Not parameter-independent — `required_flat_rounds` is
exactly the arbitrary X they name, which "a user has no way of knowing a priori".

**The frozen basis was the load-bearing defect.** With the basis frozen, only
kinds already inside the frame can be discovered, so flatness is reachable by
construction. That is *a priori thematic saturation* (Saunders et al.,
doi:10.1007/s13135-017-0574-8 — see note below), not inductive or theoretical
saturation. The frame is not neutral and this is measured, not rhetorical:
Hennink et al. found the *same* 25 interviews saturate at 9 (codes) or 16–24+
(meanings), with one code never saturating.

**Applied:** `SaturationVerdict.BOUNDED_SATURATED` is renamed
`A_PRIORI_FRAME_FLAT`; `certifies_recall` is a property fixed at `False`; the
verdict now states that it says nothing about kinds outside the frame and
reports a rule-of-three residual novelty bound. On a two-flat-round run that
bound prints as `<= 1.500` — i.e. no constraint at all — which is the honest
reading and was previously hidden behind the word "saturated".

### 8b. The upgrade I was about to make would have failed toward false confidence

The obvious next step — add Chao1 `f̂₀ = f₁²/(2f₂)` and Good–Turing `Û ≈ f₁/n`
as a coverage estimate — is wrong here for two compounding reasons:

1. With a **single adaptive stream** every item has multiplicity 1, so `f₂ = 0`
   and Chao1 collapses to its degenerate branch.
2. Worse, an adaptive searcher that follows up on what it just found **converts
   singletons into doubletons**, deflating `f₁` relative to `f₂`, which deflates
   *both* `Û` and `f̂₀`. The diagnostic therefore fails toward **false
   confidence**. "High f₁ ⇒ tail under-sampled" is safe; the operationally
   load-bearing converse, "low f₁ ⇒ near exhaustion", is precisely the artifact
   adaptivity manufactures.

Bron et al. (arXiv:2404.01176) state it flatly: population-size estimators "are
not directly applicable to the general CAL paradigm". Their fix is to
*manufacture* independent capture occasions — a committee of differently-trained
classifiers — and even then their conservative criterion meets a 95% target in
**69.86%** of runs and a 100% target in **53.09%**.

**Consequence for ORION's `evidence_lineage` coordinate:** pairwise-disjoint
lineage is **not** independence. When the query policy is adaptive, the
searcher's own choices correlate the lineages, and positive dependence biases
missing-mass estimates *downward*. Asserting disjointness after the fact buys
nothing; independence has to be constructed (k retrieval policies with disjoint
seeds and tooling that cannot see each other's results).

### 8c. Hard impossibility results that bound what any criterion can claim

- Support size is **unestimable** without a floor on minimum mass (Valiant &
  Valiant, doi:10.1145/1993636.1993727).
- Missing mass is **unlearnable in relative error**, distribution-free (Mossel &
  Ohannessian, doi:10.3390/e21010028) — and relative error is what a stopping
  rule needs.
- Confidence intervals for the number of classes are **necessarily one-sided**
  (Mao & Lindsay, doi:10.1214/009053606000001280), and one-sided in the useless
  direction: "at least this many exist", never "no more than this many remain".

### 8d. What a defensible criterion would require, partitioned by coordinate

ORION's setting does not admit the target every TAR criterion presupposes,
because recall needs a fixed denominator and most ORION coordinates are open.

- **Enumerable coordinates** (evidence over a fixed corpus): **QBCB**
  (Lewis, Yang & Frieder, doi:10.1145/3459637.3482415) — pre-draw a random
  sample of *r* positives **before** the search, stop when the *j*-th is
  rediscovered, *j* from the binomial quantile at (t, α). Distribution-free, and
  it survives arbitrary adaptivity precisely because the certification sample
  was not chosen by the search.
- **Open coordinates** (residual kinds, failure signatures): no recall target is
  definable. The available machinery is **anytime-valid monitoring** — wrap the
  novelty statistic in an e-process and stop at `M_t ≥ 1/α`; Ville's inequality
  gives free peeking, and Howard et al. (doi:10.1214/20-AOS1991) Lemma 3 extends
  validity to random times that need not be stopping times.
- **Missing entirely:** a cost/value model. Stopping is not currently a decision
  problem in ORION. Fletcher & Stevenson (arXiv:2606.07071) derive EVPI-based
  stopping and argue recall targets are the wrong objective when what matters is
  whether the evidence supports the *decision* — which fits an autonomous
  research system better than any recall target.

**Do not** use Heaps' law or knee detection to justify stopping: `β > 0` implies
no asymptote, and Kneedle's own author calls knee detection "inherently
heuristic". Font-Clos & Corral show the fitted exponent *increases* with corpus
size, so a short window under-reads it — in the direction that looks like
levelling off.

### 8e. Residuals opened by this absorption

5. **Growth vector is still wired as a stopping criterion.** It should be
   demoted to telemetry; the stop should come from QBCB (enumerable) or an
   e-process (open). Renaming the verdict was the honest interim step, not the
   fix.
6. **No independent capture occasions exist.** Until they do, no coverage
   estimator may be added at all.
7. **`new_failure_signatures` has no established operationalization** in any of
   the five literatures surveyed — CANNOT_CHECK, and possibly a genuine gap.
8. **No paper analyses Chao's estimator under adaptive query-driven sampling** —
   reported as a genuine gap, which is a candidate ORION research contribution
   rather than a hole to paper over.

*Note: the Saunders et al. DOI is transcribed from the research lane and is not
independently re-verified here — treat as CANNOT_CHECK pending a Crossref
lookup.*
