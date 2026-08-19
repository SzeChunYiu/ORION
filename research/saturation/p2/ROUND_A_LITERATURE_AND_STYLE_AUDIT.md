# P2 saturation — Round A literature and style audit

Date: 2026-08-19  
ORION base: `e5504065dcf1f71b371a611b5d5ad8db7f4a8ce0`  
Nature-skills subject: `Yuan1z0825/nature-skills@96e41d3348748796c239cf5cb85bd947e5b02d38`

This is a first candidate/venue pass, not literature saturation. Source state is marked conservatively.

## 1. Fresh candidate set

| Work | Source state | Role for P2 | Round-A disposition |
|---|---|---|---|
| Mind-ParaWorld / `Evaluating the Search Agent in a Parallel World`, arXiv:2603.04751 | ABSTRACT | benchmark explicitly isolates evidence collection, coverage, sufficiency judgment and when-to-stop failure | BENCHMARK / NEGATIVE_PRESSURE; supports separation of acquisition quality from stopping reliability |
| `Confidence-Based Stopping Methods for Systematic Reviews`, arXiv:2606.15380 | ABSTRACT | systematic-review stopping based on information needed for a decision rather than target recall alone | ADOPT as additional sufficiency/decision-stopping prior art |
| DeepSearchQA, arXiv:2601.20975 | ABSTRACT | exhaustive-list open-search benchmark; exposes premature stopping vs over-retrieval trade-off | BENCHMARK / NEGATIVE_PRESSURE |
| S1-DeepResearch, arXiv:2606.15367 | ABSTRACT | long-horizon deep research beyond search-centric training | BACKGROUND / CONTRAST; acquisition/planning capability is donor territory |
| SIRA, arXiv:2605.06647 | ABSTRACT | corpus-discriminative single-query lexical expansion against multi-round agentic retrieval | DONOR / STRONG_BASELINE pressure against adaptive/multi-round retrieval novelty |
| HALT, arXiv:2608.02009 | already cited / ABSTRACT | verification-aware evidence-coverage stop; generated vs gold hop-claim variants | ADOPT stopping mechanism, not closure authority |
| Decision-Theoretic Stopping Rules for Document Screening, arXiv:2606.07071 | already cited | TAR screening stop under payoff/cost model | ADOPT utility stopping |
| Search, Inspect, Fetch, arXiv:2608.02751 | already cited | structure-rich Boolean retrieval/inspection/fetch | ADOPT acquisition module |
| R-Search, IP&M 2026 article 104732 | PUBLISHER ABSTRACT | reasoning-guided natural-language DAG for multi-source search | STYLE + DONOR pressure; structured search planning is not P2 novelty |
| `Harnessing language models for computational literature review of emerging AI topics`, IP&M 2025 article 104245 | PUBLISHER ABSTRACT | computational literature-review method paper | STYLE / VENUE_CONTEXT |

## 2. Material scientific findings

### F1 — sufficiency-aware stopping is even more crowded than the current manuscript says

The new systematic-review paper explicitly stops based on whether screened evidence contains enough information to support a decision, rather than target recall alone. Combined with HALT and the previously cited decision-theoretic/conformal/learned stopping work, P2 must not imply that `sufficiency` itself is the residual novelty.

Residual remains:

> sufficiency or coverage may guide local acquisition/route stopping, but does not automatically discharge separately registered global scientific-search obligations.

### F2 — search-agent benchmarks independently identify stopping as a bottleneck

Mind-ParaWorld reports evidence collection/coverage and unreliable evidence-sufficiency/when-to-stop behavior as distinct limitations. DeepSearchQA similarly exposes premature stopping and over-retrieval. These works strengthen the **problem motivation and benchmark landscape**, not P2's proof of superiority.

### F3 — sophisticated retrieval/query formation remains donor territory

SIRA and R-Search add additional pressure against any suggestion that multi-round planning, query generation, structured search traces, or retrieval-specific cognition are P2 inventions. This reinforces the current donor-composable acquisition framing.

### F4 — no Round-A source found a direct equivalent of P2's authority contract

This is only a route-scoped observation, not an absence theorem. The fresh papers improve retrieval, stopping decisions, or evaluation; they do not, from the material read in this round, provide the same explicit separation between route-local acquisition signals and task-global scientific closure under unresolved unavailable/censored route obligations.

## 3. IP&M style / venue findings

Current official IP&M scope explicitly accepts:

- research at the intersection of computing and information science;
- **methods manuscripts**;
- **critical applications/system design research**.

That is a strong fit for P2's narrowed object.

Observed 2026 IP&M articles tend to expose the method/system contribution immediately in title/abstract, include explicit highlights, use multiple public datasets/baselines when claiming performance, and frame implications at the computing/information-science intersection. Recent RAG/search papers are performance-oriented, which creates a reviewer risk for P2: the manuscript must make very clear that the contribution is an **authority/system-design contract** rather than trying to compete as a new retriever with an intentionally incomplete external superiority study.

### IP&M implication for P2

- keep the current title direction `Acquisition Is Not Closure`;
- make the systems problem legible to an information-retrieval reader in the first paragraph;
- give historical TAR/systematic-review stopping roots enough space so the paper does not look LLM-agent-only;
- present the 390-task controlled result as a mechanism test with a complete denominator;
- use external failures/nulls to establish operational constraints, not as a substitute for a matched benchmark win;
- prepare 3–5 crisp highlights after content stabilizes.

## 4. JASIST fallback findings

JASIST's current author guidance expects explicit engagement with information representation/organization, human-information interaction, or the impacts/uses of information systems, and Research Articles should be grounded in theory and connected directly to information-science scholarship.

P2 can plausibly fit, but JASIST is **not only a formatting fallback**. A strong JASIST version would need to foreground the informational meaning of coverage/obligation/processing state and connect more explicitly to professional/systematic search practice. Depending on review pressure, it may also benefit from human/professional search evidence. Do not pretend that requirement is already met.

## 5. Writing architecture diagnosis

### Current strengths

- title states the conceptual distinction directly;
- abstract preserves underpowered/CANNOT_CHECK boundaries;
- route-stop versus task-stop distinction is easy to state;
- historical TAR and capture-recapture roots are already present;
- external provider failures are retained rather than hidden.

### Main risks

1. Abstract is too dense with benchmark implementation detail before the reader fully owns the authority question.
2. `Nearest work` is donor-complete but can be reorganized more explicitly by IR function and authority consequence.
3. The controlled + MetaSyn + Wide/Deep narrative can feel like several partially connected studies; stage labels need to be visually/rhetorically unmistakable.
4. The conclusion currently says the matched external claim remains open; because the *paper* is intentionally narrowed, wording should avoid making that future result sound like an unfinished prerequisite for the present manuscript.
5. JASIST fallback would need more direct information-science conceptual framing than the current AI-agent-centered opening.

## 6. Round-A state

`MATERIAL_CHANGE = YES` for literature coverage and likely citation additions, but `CLAIM_TERMINAL_CHANGE = NO`.

Next actions:

- add/cite the strongest new benchmark/stopping donors without citation padding;
- build the citation-role ledger and strict reference audit;
- study more IP&M/JASIST full papers to quantify section/abstract/highlight patterns;
- run Round B after edits. Two no-material-change rounds have not been achieved.