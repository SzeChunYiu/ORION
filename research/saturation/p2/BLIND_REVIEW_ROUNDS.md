# P2 saturation — two adversarial blind-review rounds

Date: 2026-08-19

Internal adversarial reviewer simulations only; no external peer-review claim.

# Round 1

## R1 — IR novelty / baseline reviewer

### Major attacks

1. The manuscript could be read as claiming novelty for search planning, sufficiency judgment, coverage-aware termination or question-conditioned retrieval.
2. The 390-task recall gap looks like an IR superiority result even though the registered inferential margin is not met.
3. A strong IR reviewer will ask why recent retrieval-aware controller and systematic-review stopping work are not treated as parents.

### Resolution

- Round B/C explicitly absorbs retrieval-aware control (RAAC), sufficiency/decision stopping, structured search planning and related work as donor territory.
- The offline result remains descriptive/mechanistic and is labelled underpowered for the frozen superiority margin.
- The invariant claim is the route/task authority boundary, not a better retriever.

**R1: no unresolved blocking/major concern.**

## R2 — methods / statistics / stopping-semantics reviewer

### Major attacks

1. Deterministic repeats could be mistaken for independent statistical units.
2. Provider-invalid external campaigns could be converted into convenient zeros or `NOT_SUPPORTED` results.
3. A reject-everything stopping policy might look safe.
4. `route independence` could be declared by labels rather than earned from acquisition identity.

### Resolution

- Manuscript states repeats nest within task and never increase the statistical unit.
- The OpenAIRE/Crossref 400-row campaign is retained as `P2_WIDE_EXTERNAL_CANNOT_CHECK`: 400 of 1,200 logical provider calls failed and the frozen 0.90 provider-validity threshold was not met; observed zero paired effect has no scientific comparison authority.
- The controlled suite measures reachable-gold recall and clean progress, so a blanket stop/refusal policy does not satisfy the mechanism objective.
- Independence binds backend, query-derivation and capture identity; route names carry no evidential weight.

**R2: no unresolved blocking/major concern.**

## R3 — information-science / reproducibility / editorial reviewer

### Major attacks

1. The controlled, MetaSyn, Deep and Wide stories can read like four disconnected mini-papers.
2. The conclusion's emphasis on a future matched external result can make the present paper sound unfinished.
3. JASIST fallback is not credible without stronger information-science framing.

### Resolution

- Style atlas fixes stage labels and one evidence chain: controlled mechanism test -> bounded external probes -> invalid/blocked stress tests -> authority contract.
- A valid failed external campaign is itself a final `CANNOT_CHECK` result; future superiority is explicitly not a prerequisite for the narrowed manuscript.
- JASIST is marked conditional and may require new human/professional-search evidence; IP&M remains the first-submission fit.

**R3: no unresolved blocking/major concern after the manuscript consistency repair recorded in the final audit.**

# Round 2

## R1b — strongest-combination reviewer

Attack: `If RAAC/HALT/confidence-based stopping + a strong retriever are combined, is P2 redundant?`

Finding: those methods can improve local acquisition and termination. They do not make an unresolved unavailable/censored route obligation disappear, nor establish task-global scientific completeness merely because local evidence is sufficient for one decision. P2 is therefore a control/authority contract under donor composition, not a claim to beat the ideal retriever.

**Verdict: no blocking/major concern.**

## R2b — external-evidence skeptic

Attack: `The external evidence is too weak to publish.`

Finding: it is too weak for external superiority, and the paper says so. The scientific claim is bounded to controlled mechanism behavior plus the systems distinction. MetaSyn/Deep/Wide are retained at their exact authority to demonstrate stage failure, operational constraints and invalidity handling. The paper would fail only if it presented those probes as full-system superiority.

**Verdict: no blocking/major concern for the narrowed claim.**

## R3b — IP&M editor simulation

Attack: `Why should an information-retrieval journal publish a paper that declines to claim better retrieval?`

Finding: the paper makes a critical system-design contribution about how retrieval/search signals are permitted to affect scientific completeness, grounded in TAR/systematic-review/federated-search roots and tested on a complete-denominator controlled index. The manuscript must foreground this systems question and not market itself as an unfinished benchmark paper. The IP&M framing in `STYLE_ATLAS_CORE.md` does so.

**Verdict: no blocking/major concern.**

# Terminal

`P2_INTERNAL_BLIND_REVIEW_CONVERGED__NO_BLOCKING_OR_UNRESOLVED_MAJOR_CONCERN_FOR_NARROWED_CLAIM`
