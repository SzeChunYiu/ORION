# ORION-P2 journal-readiness plan — Open-World Scientific Knowledge Discovery

**Current terminal:** `CANNOT_CHECK` for external recall/discovery benefit / not peer-review ready.  
**Already present:** scoped research object, route/read-ledger mechanics, local complete-gold falsifier, same-call lexical baseline rule, independence and stopping refusal semantics.

## 1. Novelty closure

- [ ] Absorb AutoResearchBench (arXiv:2604.25256) as the primary Wide/Deep discovery benchmark family.
- [ ] Absorb SAGE retrieval benchmark (arXiv:2602.05975): strong BM25/lexical retrieval is a mandatory baseline.
- [ ] Absorb MetaSyn (arXiv:2606.17041): retrieval recall and eligibility/screening recall are separate stages.
- [ ] Absorb AgentSLR (arXiv:2603.22327): end-to-end systematic-review automation is not novel.
- [ ] Absorb the controlled physics/astrophysics/cosmology literature-review comparison (arXiv:2607.25672) as evidence that human-expert overlap/completeness remains an open evaluation problem.
- [ ] Re-search systematic-review stopping, capture-recapture, query diversification, information foraging, federated search and active screening.
- [ ] Preserve the surviving claim as route governance/coverage refusal + cumulative question-conditioned memory + recall-first promotion, not generic agentic retrieval.

## 2. Primary hypotheses

**H1 — discovery recall:** under matched resources, full ORION improves complete-gold paper recall/IoU over strong lexical, dense and agentic single-route baselines.

**H2 — route diversity:** earned independent routes add unique relevant evidence beyond nominally different shared-backend routes.

**H3 — stopping safety:** typed route-stop/task-stop separation reduces premature task closure without unbounded cost.

**H4 — question-conditioned memory:** question/content-version-aware read history avoids redundant processing while preserving necessary rereads when the extraction question changes.

- [ ] Freeze one primary outcome per benchmark family.
- [ ] Freeze equivalence/non-inferiority margin if the main value proposition is safety/coverage at bounded extra cost rather than raw recall only.

## 3. External evaluation suite

- [ ] AutoResearchBench **Deep Research** tasks with official evaluation.
- [ ] AutoResearchBench **Wide Research** tasks with official IoU/coverage evaluation.
- [ ] SAGE scientific retrieval corpus/tasks where licensing permits.
- [ ] MetaSyn retrieval and screening stages where licensing permits.
- [ ] at least one frozen local complete-gold corpus with legally distributable denominator.
- [ ] optional expert literature-review cases modeled after the physics/astrophysics/cosmology controlled study.

For live-provider search:

- [ ] freeze date/time, provider/backend versions and query trajectories;
- [ ] retain raw search results and transport failures;
- [ ] separate provider unavailability from evidence of absence;
- [ ] audit search-time contamination when benchmark questions/answers are public;
- [ ] run an offline/controlled-index companion evaluation so reproducibility does not depend entirely on mutable web results.

## 4. Baselines and ablations

Baselines:

- [ ] BM25/title/keyword retrieval;
- [ ] dense retrieval;
- [ ] hybrid sparse+dense retrieval;
- [ ] one-pass RAG retrieval;
- [ ] agentic single-route search;
- [ ] AgentSLR-like or another strong protocol-driven SLR baseline where runnable.

Ablations:

- [ ] ORION without route-independence checks;
- [ ] ORION without question-conditioned read ledger;
- [ ] ORION where route stop is allowed to certify task stop;
- [ ] ORION without unavailable-route/open-coverage state;
- [ ] ORION with coverage diagnostics allowed to influence stopping (negative/safety ablation);
- [ ] equalized query/tool/token/time budgets.

## 5. Metrics

Retrieval/discovery:

- [ ] paper-level recall where the denominator is complete;
- [ ] Wide Research IoU/official metric;
- [ ] Deep target hit/success under official protocol;
- [ ] precision as a secondary metric;
- [ ] screening recall / false-negative count on MetaSyn-like tasks;
- [ ] nDCG/MRR only where the task is rank-oriented rather than set-complete.

Route/stopping:

- [ ] unique relevant items contributed per route;
- [ ] route overlap by content digest;
- [ ] marginal gain from each additional route;
- [ ] route-stop false-positive/false-negative rate;
- [ ] task-stop false-positive rate (premature closure);
- [ ] unavailable-route count and censored obligations;
- [ ] duplicate/re-read avoidance rate;
- [ ] cost, latency, query count and tokens.

## 6. Required plots

- [ ] **Figure P2-1:** discovery pipeline separating retrieval, screening, route stop and task closure.
- [ ] **Figure P2-2:** recall/IoU vs cost for every baseline.
- [ ] **Figure P2-3:** cumulative unique relevant discoveries vs queries/time.
- [ ] **Figure P2-4:** per-route marginal unique-relevant contribution with earned-independence annotation.
- [ ] **Figure P2-5:** route overlap matrix/heatmap using content identity.
- [ ] **Figure P2-6:** stopping confusion matrix or premature-closure rate by failure family.
- [ ] **Figure P2-7:** Wide vs Deep performance by system.
- [ ] **Table P2-1:** benchmark/data/license/freeze manifest.
- [ ] **Table P2-2:** full baseline + ablation results with intervals and cost.
- [ ] **Table P2-3:** failure taxonomy: present-but-missed, retrieved-but-unused, screening miss, route starvation, transport failure, premature closure.

## 7. Manuscript work missing

- [ ] create a canonical full manuscript under `manuscript/`;
- [ ] introduction must separate discovery from synthesis quality;
- [ ] formalize earned route independence and route/task stop states;
- [ ] methods must define content identity/dedup, read ledger and coverage refusal;
- [ ] evaluation must explain which metrics are valid only with complete denominators;
- [ ] add external Results/Discussion only after frozen runs;
- [ ] include the SAGE lexical-baseline finding and AgentSLR/MetaSyn/AutoResearchBench nearest work;
- [ ] add limitations for mutable providers, incomplete gold sets, language/domain bias and database coverage;
- [ ] add data/code availability and reproducibility statements.

## 8. Reproducibility package

- [ ] benchmark licenses/access notes;
- [ ] frozen corpora/index snapshots where redistribution permits;
- [ ] query derivation and route-definition manifests;
- [ ] raw provider results and request timestamps for live runs;
- [ ] exact dedup/content-identity code version;
- [ ] scripts regenerating all metrics/plots;
- [ ] clean environment and expected runtime/cost;
- [ ] independent reproduction of at least the offline controlled-corpus headline table.

## Done definition

`ORION-P2 = PEER_REVIEW_READY` only after complete-gold/live evaluations demonstrate the claimed recall/stopping trade-off against strong baselines, all `OPEN/CANNOT_CHECK` coverage conditions are reported rather than hidden, and every gate in the programme journal-readiness standard passes.
