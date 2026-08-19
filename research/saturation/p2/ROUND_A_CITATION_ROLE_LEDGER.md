# P2 Round-A citation-role ledger

Date: 2026-08-19

This is the first `nature-citation`-style role pass. `SUPPORT_GRADE` refers to the proposition used in P2, not general paper quality.

| Source/family | Citation role | Proposition it supports/pressures | Support grade | Action |
|---|---|---|---|---|
| AutoResearchBench | BENCHMARK / NEGATIVE_PRESSURE | complex scientific literature discovery remains difficult | DIRECT for benchmark motivation | KEEP |
| SAGE | STRONG_BASELINE / DONOR | lexical+metadata retrieval can be strong in deep research | DIRECT | KEEP; generic lexical retrieval not novel |
| AgentIR | DONOR | reasoning-aware retrieval is prior art | DIRECT | KEEP |
| SIEVE | DONOR | Boolean/fielded/inspect/fetch retrieval is prior art | DIRECT | KEEP |
| MetaSyn | BENCHMARK / CLAIM_BOUNDARY | retrieval and screening are distinct stages; ID-only public evaluation exists | DIRECT | KEEP |
| AgentSLR | DONOR / BENCHMARK | systematic-review automation is active prior work | DIRECT | KEEP |
| capture-recapture literature | FORMAL/EVALUATION_PRECEDENT | search completeness estimation/stopping has historical precedent and assumptions | DIRECT/PARTIAL by exact proposition | KEEP |
| TAR/CAL stopping literature | FORMAL_PRECEDENT | screening and recall-based stopping are mature IR/review problems | DIRECT | KEEP |
| DeepControl | DONOR | marginal-information/utility continuation control is prior art | DIRECT | KEEP |
| HALT | DONOR | verification/evidence-coverage stopping is prior art | DIRECT | KEEP |
| Decision-Theoretic Stopping | DONOR | utility/cost stopping is prior art | DIRECT | KEEP |
| MiCP | DONOR | adaptive/conformal stopping is prior art | DIRECT | KEEP |
| Search-R1 structured STOP judgments | DONOR | learned sufficiency/gap STOP/CONTINUE is prior art | DIRECT | KEEP |
| MemChain | DONOR / CONTRAST | question-conditioned memory/evidence plans are prior art | DIRECT | KEEP; P2 residual is dual identity/processing bookkeeping |
| Mind-ParaWorld | BENCHMARK / NEGATIVE_PRESSURE | evidence collection/coverage and sufficiency/when-to-stop can fail separately | DIRECT from reported benchmark analysis | ADD in saturation revision |
| Confidence-Based Stopping Methods for Systematic Reviews | DONOR | stopping can monitor whether enough information exists for a decision, not only target recall | DIRECT from abstract; full-text review pending | ADD after deep read |
| DeepSearchQA | BENCHMARK / NEGATIVE_PRESSURE | open-ended exhaustive search exposes premature stopping vs over-retrieval | DIRECT from benchmark paper | ADD after deep read |
| SIRA | DONOR / STRONG_BASELINE | sophisticated corpus-aware lexical query formation can beat multi-round retrieval | DIRECT from abstract; full-text review pending | ADD only if useful for acquisition non-novelty, avoid padding |
| R-Search (IP&M) | VENUE_CONTEXT / DONOR | structured multi-step/multi-source search planning is active IP&M work | DIRECT from publisher abstract | STYLE corpus first; cite only if needed in nearest work |

## Residual after this pass

The literature ledger should make the following subtraction visible:

`better retrieval + query planning + screening + coverage estimation + sufficiency judgment + stopping` **does not equal** `authority to declare global scientific search complete`.

P2's residual is not that no one has stopping criteria. It is the typed authority contract that keeps unresolved registered obligations open when local acquisition signals look favorable.

## Next citation work

- full-text deep-read the ADD candidates before citing central propositions;
- run strict metadata verification for the entire bibliography;
- segment abstract/introduction/nearest-work/history claims and assign support grades;
- remove any citation whose only role is prestige/keyword proximity;
- add classical information-science roots if the JASIST overlay is retained.