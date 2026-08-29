# ORION-12 literature entailment and novelty subtraction — 2026-08-28

## Search and source boundary

The audit used the manuscript bibliography, retained primary-source records and a 2026-08-28 OpenAlex refresh over three query families: scientific-literature agents, search/stopping/coverage, and evidence-obligation workflows. The broad refresh found no newer work that displaced the nearest-neighbor set; this is not a saturation certificate. TREC-COVID metadata and DOI `10.1145/3451964.3451965` were live-verified through Crossref. Preprints remain identified as preprints where the bibliography so records them.

## Source-entailing propositions

| Citation key | Exact proposition used; no stronger proposition is granted |
|---|---|
| `autoresearchbench2026` | Targeted literature-search agents remain difficult on controlled research tasks. |
| `researcharena2024` | Open-ended research/search remains difficult on benchmarked tasks. |
| `sage2026` | Strong lexical retrieval can outperform large-model retrievers inside a deep-research workflow. |
| `agentir2026` | Reasoning traces can serve as retrieval signals. |
| `sieve2026` | Field-aware admission and selective section fetching trade context for accuracy. |
| `rethinkinglitsearch2026` | Bibliography expansion can recover eligible studies missed by API-only search. |
| `metasyn2026` | Retrieval and eligibility screening are separable evidence-synthesis stages. |
| `agentslr2026` | An agent workflow has been evaluated on expert-annotated systematic-review tasks. |
| `cormack2014tarprotocols` | Technology-assisted review protocols study active screening and recall. |
| `cormack2015autonomycal` | Continuous active learning studies autonomy and high-recall review. |
| `vandeschoot2021asreview` | Active-learning review tools study workload reduction. |
| `callaghan2020stopping` | Systematic-review screening has statistical stopping proposals. |
| `li2020whentostop` | Systematic-review screening has data-driven stopping research. |
| `yang2021heuristicstopping` | Heuristic stopping rules have been evaluated for screening. |
| `decisionstop2026` | Continuation/stopping can be framed decision-theoretically. |
| `deepcontrol2026` | Deep-research control can use marginal-utility or granularity decisions. |
| `halt2026` | Verification-aware completion/stopping is prior work. |
| `donotstopearly2026` | Evidence-coverage warnings against premature stopping are prior work. |
| `micp2026` | Conformal coverage has been applied to adaptive reasoning control. |
| `confidencebasedstop2026` | Confidence/sufficiency judgments have been used for stopping. |
| `multiragstop2026` | Structured gap judgments have been used to decide retrieval continuation. |
| `knowplan2026` | Finite obligation/certificate planning is a strong donor mechanism. |
| `icore2026` | Evidence-bound workflow transitions are a strong donor mechanism. |
| `kastner2009capturerecapture` | Capture–recapture estimates require defensible capture assumptions. |
| `rucker2011boosting` | Dependence can mislead capture–recapture estimates in evidence retrieval. |
| `pirolli1995foragingchi` | Information foraging models continuation versus leaving a local patch. |
| `pirolli1999foraging` | Information-foraging theory concerns local information-patch value. |
| `memchain2026` | Question-conditioned memory organization is prior work. |
| `voorhees2020treccovid` | TREC-COVID defines the public IR evaluation used for the registered external test. |

## Donor subtraction

The strongest donor combination is `knowplan2026` plus `icore2026`: finite obligations/certificates and evidence-bound workflow transitions. The paper therefore does **not** claim generic obligation tracking, stopping, retrieval, screening, coverage estimation, question-conditioned memory or workflow governance as novel. It grants all donor mechanisms to the acquisition policy.

The surviving residual is narrower: for a declared material route that is unavailable, censored or provider-invalid, the route may not silently disappear from the task-closure denominator. The exact-contract comparison changes that aggregation rule while holding strong donor mechanisms fixed. The information-equivalent 400/400 tie further subtracts unique implementation or centralized expressivity. The result is a bounded control-interface contribution, not a priority claim.
