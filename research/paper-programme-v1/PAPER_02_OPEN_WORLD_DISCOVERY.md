# Paper II research object — Open-World Scientific Knowledge Discovery

## Candidate claim after nearest-work challenge

ORION is not novel merely because it searches papers with an agent or performs RAG.  The scoped candidate is:

> A scientific-literature discovery process that treats heterogeneous search routes as **earned capture occasions**, records question-framed read history, distinguishes route stopping from task closure, exposes unavailable routes as open coverage obligations, evaluates discovery with recall-first complete-gold protocols where available, and refuses to promote route flatness or unseen-mass diagnostics into global completeness.

## Atoms

1. route-family definition;
2. query derivation independence;
3. provider/backend independence;
4. source/content identity and cross-route deduplication;
5. question-framed read/re-read decisions;
6. route stopping/reformulation/switching;
7. task-level search closure;
8. recall/coverage measurement;
9. wide versus deep literature discovery;
10. baseline and resource matching.

## Nearest work and mechanisms absorbed

### ResearchArena — arXiv:2406.10291
Mechanisms: separates academic survey work into discovery, selection and organization; builds an offline scientific corpus and evaluates each stage; reports that LLM research approaches can underperform keyword retrieval.

**Absorb:** stage-attributed evaluation; strong lexical baseline; separate discovery from organization quality.

**Consequence:** ORION cannot claim search progress because synthesis looks good. Discovery recall is its own gate.

### AutoResearchBench — arXiv:2604.25256
Mechanisms: complementary **Deep Research** (find a specific paper through multi-step probing) and **Wide Research** (collect an open-ended qualifying set) tasks; very low baseline performance exposes literature search as an independent capability bottleneck.

**Absorb:** frozen wide+deep trial structure; exact task split; open-ended set evaluation; explicit search trajectory.

### MetaSyn — arXiv:2606.17041
Mechanisms: meta-analysis-grounded corpus with PI/ECO criteria, verified positives, hard negatives, complete search strategies; stage-attributed metrics show screening is a major bottleneck and retrieval ceiling does not imply inclusion recall.

**Absorb:** eligibility-aware screening; verified-positive gold sets; stage-local error attribution; separate retrieval recall from semantic eligibility.

### OpenScholar — arXiv:2411.14199
Mechanisms: large scientific datastore, retrieval-augmented synthesis, citation-backed responses, self-feedback loop, multi-domain benchmark.

**Absorb:** passage-level retrieval; corpus-scale indexing; citation-backed downstream synthesis; retrieval feedback.

**Not a surviving novelty:** scientific RAG, large literature datastore, self-feedback during synthesis.

### Systematic-review screening/evaluation
LLM4SCREENLIT and related screening work emphasize lost evidence/recall, imbalance-aware metrics, complete confusion matrices and cost-sensitive evaluation.

**Absorb:** false negatives are primary harm; report full stage confusion/censoring; workload-saving claims require retained recall; baseline comparisons are mandatory.

### Capture-recapture / systematic-review completeness literature
Capture-recapture is a historical method for estimating missed studies and is therefore not ORION novelty.  The lesson transferred into ORION is stronger: adaptive routes are not automatically independent capture occasions, so independence must be constructed and diagnosed rather than assumed.

## ORION mechanics already present

Current main has provider-specific rate discipline, arXiv/OpenAlex retrieval, content-digest identity, cross-route aliases, a durable read ledger, route control, route ensembles, recall evaluation, question-to-multi-route `ResearchPacket` construction, unavailable-route gaps and content-based growth accounting.

## Surviving candidate deltas

- `P2.D1.EARNED_ROUTE_INDEPENDENCE`: route labels do not create independence; backend, query derivation and capture identity must support it.
- `P2.D2.QUESTION_FRAMED_READ_LEDGER`: "paper already seen" is weaker than "paper already processed for this question/extraction schema/content version".
- `P2.D3.ROUTE_TASK_SEPARATION`: route stop/reformulate/switch/budget-stop are typed outcomes that cannot certify task saturation.
- `P2.D4.COVERAGE_REFUSAL`: missing backends, no route overlap, resource censoring or incomplete gold sets produce `OPEN/CANNOT_CHECK`, not flattering estimates.
- `P2.D5.RECALL_FIRST_PROMOTION`: sophisticated agent retrieval must beat a simple lexical baseline on frozen discovery tasks before promotion.

## Falsifiers / benchmarks

### Benchmark suite
Use at least:
- ResearchArena discovery stage;
- AutoResearchBench Wide + Deep;
- MetaSyn retrieval/screening where licensing permits;
- a frozen local known-answer literature set with complete gold coverage.

### Baselines
- BM25/title/keyword retrieval;
- one-pass dense/RAG retrieval;
- agentic single-route search;
- ORION multi-route without independence checks;
- full ORION.

### Metrics
- paper-level recall / IoU where gold is complete;
- screening recall and false-negative count;
- precision only as a secondary coordinate;
- unique relevant evidence per route;
- route overlap by content digest;
- unavailable-route count;
- cost and latency;
- number of route/task stopping errors.

### Hostile cases
1. same backend and same query under two route names — must receive no independence credit;
2. same paper with re-minted IDs — must deduplicate by content/identity;
3. route returns zero due transport failure — must not become evidence of absence;
4. selection window starves a lower-priority route — must not become flatness;
5. zero overlap between independent routes — unseen population is unbounded; diagnostic must refuse a confident estimate.

## Paper claim boundary

Paper II must not claim:
- first agentic literature search;
- first scientific RAG;
- first capture-recapture use in literature review;
- completeness of the open scientific literature.

It may test whether **earned route diversity + cumulative question-framed memory + fail-closed coverage/stopping + recall-first promotion** improves open-world scientific discovery relative to strong simple and agentic baselines.
