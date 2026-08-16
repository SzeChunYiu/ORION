# ORION-P2 journal-readiness plan — Open-World Scientific Knowledge Discovery

**Current terminal:** `CANNOT_CHECK` for externally supported recall/discovery benefit; **not** `PEER_REVIEW_READY`.

**Completed result-bearing evidence:** frozen 20-task offline complete-gold companion, 14 systems × 3 repeat seeds = 840 normalized run records, authority `DESCRIPTIVE_ONLY`. Full ORION mean recall 0.994444; strongest frozen confirmatory comparator 0.666667; descriptive difference +0.327777. The immutable mechanism projection now regenerates P2-3/P2-4/P2-5 from the same bound records, and the complete-gold O1 replay reports both route-stop FP and FN. The external Wide/Deep/MetaSyn/SAGE campaign is not complete, so this evidence cannot be promoted to real-web superiority.

## 1. Novelty closure

- [x] Absorb AutoResearchBench as the primary Wide/Deep discovery benchmark family.
- [x] Absorb SAGE: strong BM25/lexical retrieval is a mandatory promotion gate.
- [x] Absorb MetaSyn: retrieval recall and eligibility/screening recall are separate stages.
- [x] Absorb AgentSLR: end-to-end systematic-review automation is not novel.
- [x] Absorb controlled AI-vs-human literature-review evidence as evidence that expert overlap/completeness remains open.
- [x] Re-search systematic-review stopping, capture-recapture, query diversification, information foraging, federated search and active screening.
- [x] Preserve the surviving claim as route governance/coverage refusal + cumulative question-conditioned memory + recall-first promotion, not generic agentic retrieval.

## 2. Primary hypotheses / prospective rules

- [x] Freeze one primary outcome per benchmark family.
- [x] Freeze superiority, safety/non-inferiority margins, resource ceilings, exclusions and multiple-comparison policy before final outcomes.
- [x] Freeze the offline execution manifest before first outcome access (`OFFLINE_RUN_MANIFEST_V1.json`, `outcome_accessed_before_freeze=false`).
- [x] Bind exact subject/data/system/evaluator identities and repeat seeds; the bound subject revision passed CI before the first result snapshot.

## 3. External evaluation suite

- [ ] AutoResearchBench **Deep Research** official result — tasks/gold obtained, but official title judge still needs an OpenAI-compatible endpoint.
- [ ] AutoResearchBench **Wide Research** official ORION-vs-baseline result — evaluator is credential-free/runnable; a gold-blind keyless external probe is executing, but the final ORION-vs-baseline result is not yet archived.
- [ ] SAGE scientific retrieval — **STRUCK:** published 200k corpus and official evaluator are unavailable; do not fabricate a substitute as “official”.
- [ ] MetaSyn retrieval + screening result — code/data and ID-only scorer are credential-free; a gold-blind retrieval/screening probe is executing, but no result is checked complete before the official evaluator artifact is archived.
- [x] Frozen local complete-gold corpus with legally distributable denominator (`evidence/offline_gold/`).
- [ ] Optional expert review cases — deferred until domain experts are available.

For live-provider search:

- [x] Freeze provider/backend/query-derivation capture identities and campaign manifest.
- [x] Capture code retains raw request/response bytes, timestamps and typed transport failures when exercised.
- [x] Separate provider unavailability from evidence of absence.
- [ ] Complete benchmark-wide search-time contamination-rate audit (structural exposure + spot checks only so far).
- [x] Run the offline controlled-index companion so the completed headline mechanism evidence is reproducible without mutable web results.
- [ ] Execute and archive the **final result-bearing** live-provider campaign with cost/wall-clock ledger.

## 4. Baselines and ablations — offline companion

The checked systems below are matched-budget controlled-index mechanism comparators. They are not claimed as external production replications.

Baselines:

- [x] BM25/title/keyword comparator (`bm25_keyword`).
- [x] dense-route comparator (`dense_retrieval`).
- [x] sparse+dense hybrid (`sparse_dense_hybrid`).
- [x] one-pass RAG retrieval (`one_pass_rag`).
- [x] agentic single-route search (`agentic_single_route`).
- [x] strong protocol-driven systematic-review comparator (`protocol_driven_systematic_review`).
- [ ] strongest *external* new baseline from the nearest-work audit — not yet run end to end.
- [x] additional adaptive multiroute comparator kept explicitly exploratory (`adaptive_multiroute_exploratory`), not retrofitted into the frozen confirmatory set.

Ablations:

- [x] no route-independence check.
- [x] no question-conditioned read ledger.
- [x] allow route stop to certify task stop.
- [x] remove unavailable-route/open-coverage state.
- [x] allow coverage diagnostics to become stopping authority (negative safety ablation).
- [x] no content-level cross-route dedup.
- [x] resource-match all variants through the same host-owned session and frozen budgets.

## 5. Metrics / statistics

Retrieval/discovery:

- [x] paper-level recall where the denominator is complete (offline complete-gold).
- [ ] Wide official IoU/set metric on an ORION candidate run.
- [ ] Deep official target-success metric on an ORION candidate run.
- [x] precision as a secondary complete-gold metric.
- [ ] external retrieval → screening recall / false-negative analysis.
- [x] rank metrics are not emitted for the set-complete offline tasks; the conditional “rank-only” rule is enforced.

Route/stopping:

- [x] unique relevant contribution by route in rich run records.
- [x] route overlap by content identity/digest.
- [x] marginal relevant gain after additional routes.
- [x] publication-complete route-stop FP **and** FN table (`evidence/offline_results/ROUTE_STOP_ORACLE_V1.json` + `TABLE_P2-S1_route_stop_oracle.md`): full ORION records 1/100 O1 route-stop FP on the deliberately unavailable restricted-route case and 0/99 FN among routes reaching oracle exhaustion; the O4 open obligation prevents that route-level FP from becoming a false task closure.
- [x] task-stop premature-closure rate.
- [x] unavailable/censored route obligations.
- [x] duplicate processing and legitimate-reread diagnostics.
- [ ] final empirical cost/latency/query/token comparison for the external campaign.

Statistics:

- [x] multiple repeat seeds are frozen and executed; deterministic repeats are collapsed within task and do not inflate `n`.
- [x] power/precision authority rule is enforced: n=20 < frozen inferential n=97 → `DESCRIPTIVE_ONLY`.
- [x] paired-comparison, margin and multiple-comparison policies are frozen prospectively for any admissible external confirmatory run.
- [ ] inferential uncertainty interval for the offline headline — intentionally **not** produced because the frozen authority ladder forbids promotion at n=20.

## 6. Required plots / tables

- [x] **Figure P2-1:** discovery pipeline separating retrieval, screening, route stop and task closure.
- [ ] **Figure P2-2:** recall/IoU vs empirical cost for every system — needs final cost-bearing campaign.
- [x] **Figure P2-3:** cumulative complete-gold discovery trajectory vs host-recorded search-query count (`OFFLINE_MECHANISMS_V1.json` → `P2-3_cumulative_discovery.{svg,tex}`); synthetic wall-clock is intentionally not claimed.
- [x] **Figure P2-4:** per-route first relevant content-identity contribution with earned-independence annotation (`P2-4_route_contribution.{svg,tex}`).
- [x] **Figure P2-5:** task-mean route-overlap matrix by content identity, with structural independence kept separate from observed overlap (`P2-5_route_overlap.{svg,tex}`).
- [x] **Figure P2-6:** stopping-safety failure figure generated from the immutable offline summary and CI-checked (`manuscript/figures/P2-6_stopping_failures.{svg,tex}`).
- [ ] **Figure P2-7:** Wide vs Deep external performance by system.
- [x] **Table P2-1:** benchmark/data/license/provider/freeze manifest.
- [ ] **Table P2-2:** final baseline + ablation + cost results **with intervals** — offline result is descriptive and therefore cannot satisfy the interval requirement.
- [x] **Table P2-3 (offline companion):** frozen terminal failure taxonomy, with unobserved lower-precedence categories called out explicitly (`evidence/offline_results/TABLE_P2-3_failure_taxonomy.md`).

## 7. Manuscript

- [x] Canonical full manuscript under `manuscript/`.
- [x] Separate discovery from synthesis quality and generic agentic automation.
- [x] Formalize earned route independence and route/task stop states.
- [x] Methods define content identity/dedup, question-conditioned read ledger, fail-closed coverage and prospective execution binding.
- [x] Evaluation text states denominator-validity requirements and the offline `DESCRIPTIVE_ONLY` authority.
- [x] Results are written only from archived immutable offline artifacts; external result slots remain `CANNOT_CHECK` rather than being filled from access audits.
- [x] Include SAGE lexical-baseline finding and AgentSLR/MetaSyn/AutoResearchBench nearest work.
- [x] Report synthetic-world, provider mutability, incomplete-gold, contamination, language/domain and database-coverage limitations.
- [x] Add data/code availability and reproducibility statements that distinguish completed offline evidence from unexecuted external/live evidence.
- [x] Add a claim ledger mapping abstract/results/conclusion claims to immutable artifacts (`evidence/CLAIM_LEDGER_V1.md`).
- [x] Add controlled-index failure analysis, including null-on-recall mechanism findings rather than hiding them.

## 8. Reproducibility package

- [x] benchmark licences/access notes.
- [x] frozen controlled corpus/index snapshots where redistribution permits.
- [x] query derivation and route-definition manifests.
- [ ] raw **final live-provider** results and request timestamps (capture machinery exists; final campaign archive does not).
- [x] exact result-bearing subject/content-dedup code version bound in the run manifest by commit/blob identity.
- [x] command regenerates the complete 840-run offline record/artifact set and checks the committed publication summary: `python3 papers/paper-02-open-world-scientific-discovery/scripts/run_offline_companion.py --check` (use `--write-raw DIR` for all generated records/artifacts).
- [x] scripts regenerate every currently completed offline metric/plot/table, including P2-3/P2-4/P2-5, P2-6, P2-3 failure taxonomy and P2-S1 route-stop FP/FN; final external-only plots remain intentionally absent until their result artifacts exist.
- [ ] clean-environment expected **external** runtime/cost ledger.
- [x] independent clean-CI reproduction of the offline headline publication summary from the frozen suite/manifest.
- [ ] permanent archive/DOI.

## 9. Submission gate

- [ ] literature closure within 14 days of submission.
- [ ] target-journal scope check after external results stabilize.
- [ ] journal formatting/supplement/cover letter.
- [ ] final reference-metadata and figure-legibility audit.
- [ ] independent final PDF/claim proofread.

## Done definition

`ORION-P2 = PEER_REVIEW_READY` only after admissible external complete-gold/Wide/Deep or equivalent evaluations support the final discovery/stopping claim against strong baselines, all `OPEN/CANNOT_CHECK` conditions remain visible, and the final journal gate passes. The completed offline companion validates mechanism behavior but **does not** by itself satisfy this terminal.
