# Q4 refinement round 1 — foundation, analogue calibration and review preflight

**Frozen manuscript:** `papers/orion-08-typed-state/MANUSCRIPT_V2.md`  
**Stretch:** Nature Machine Intelligence  
**Fallback:** npj Artificial Intelligence  
**Reviewer isolation:** `MUTUAL_BLINDNESS_NOT_GUARANTEED`.

## 1. Foundation spine

### Question

When two scientific decision systems receive the same visible partial facts, under what conditions can explicit bindings for role, applicability scope, uncertainty, transformation history and decision relevance change the decision?

### Answer

Across six frozen exact-synthetic matched-information studies, distinct epistemic bindings are load-bearing in different decision problems, while strong donor and no-value regimes identify where the same structure adds no value. The common hypothesis is not “typed memory is better,” but that scientific facts are often useful only together with metadata describing **where they apply and how they affect a downstream decision**.

### Decisive evidence chain

1. Type-conditioned prior changes otherwise identical VoI decisions.
2. Scope-bound failure reuse distinguishes relevant from irrelevant context changes.
3. Decision-specific Pareto ambiguity changes which uncertainty should be verified.
4. Full-chain transport state detects invalid deep evidence reuse that last-hop state misses.
5. Decision-coupled acquisition rejects high-entropy but decision-irrelevant decoys.
6. Typed remint/transport helps only in the mixed-transport regime and ties exactly when remint is unnecessary.
7. N1-C and N2-F5B donor comparisons explicitly subtract policy/crossover novelty.

### Boundary

All headline evidence is exact-synthetic. The suite does not establish real-agent performance, a universal typed-memory theorem, security, or transfer to live scientific workflows. The six studies test different decisions and may not be pooled into one universal effect size.

### Meaning

Scientific-agent memory/state design should distinguish truth-bearing content from validity/applicability/decision metadata. The suite provides controlled mechanism tests and null regimes that can guide a real-domain matched-information benchmark without conflating more structure with more facts.

## 2. Proposed unifying taxonomy

The six studies can be organized by the epistemic relation that the downstream decision requires:

| Binding axis | Decision question | Frozen study | Strongest key control |
|---|---|---|---|
| `TYPE_PRIOR` | what prior should unknown feasibility receive? | N4-A | identical VoI with uniform prior |
| `APPLICABILITY_SCOPE` | does an old failure still license closure? | N4-B | irrelevant NOISE changes |
| `DECISION_RELEVANT_UNCERTAINTY` | which unknown blocks Pareto choice? | N4-C | matched-budget random/midpoint alternatives |
| `TRANSPORT_LINEAGE` | does evidence survive the full transformation chain? | N4-D | deep splices vs last-hop check |
| `DECISION_COUPLING` | which observation can change the downstream action? | N4-E | high-entropy decoys |
| `REMINT_OBLIGATION` | reuse, remint or rederive after representation edit? | N4-F3 | REMINT_UNNECESSARY exact tie |

This taxonomy is a **post-study synthesis** and should be labeled theory-building rather than preregistered cross-family proof.

## 3. Terminology ledger

| Canonical term | Meaning | Boundary |
|---|---|---|
| epistemic binding | metadata relating a fact/evidence item to role, scope, uncertainty, lineage or decision | not generic memory embedding |
| matched information | arms receive the same visible factual payload within each frozen family | representation/use can differ |
| typed/scoped state | state with declared epistemic binding relevant to that family | no universal schema-minimality claim |
| donor first right of refusal | strongest relevant same-information comparator | donor can absorb policy novelty |
| no-value regime | prespecified world where typed coordinate should not help | required to avoid always-on benefit story |
| exact-synthetic | deterministic controlled world with exact truth under declared model | not real-agent validation |
| LLM_PROXY | deterministic heuristic baseline | never describe as LLM performance |

## 4. Close-analogue calibration

### Analogue A — Nature Machine Intelligence, “A benchmarking framework for embodied neuromorphic agents” (2026)

Observed transferable functions:

- framework/benchmark papers make tasks, metrics, platform and reproducibility explicit;
- the benchmark's value is tied to a real-world/scalable evaluation contract;
- a taxonomy of tasks is made operational rather than presented only as prose.

Q4 adoption:

- turn the six-study list into a benchmark taxonomy with one schema for `fact bundle -> binding -> decision -> hostile control -> metric -> donor`;
- make null/no-value regimes part of the benchmark definition.

### Analogue B — Nature Machine Intelligence 2026 discussion of synthetic-data simulation-to-reality gaps

Observed implication:

- strong synthetic evidence does not automatically transfer to real behavior;
- Q4's explicit real-domain preregistration is a strength, but the stretch venue remains evidence-blocked until transfer exists.

### Analogue C — npj Artificial Intelligence agentic framework papers (2026)

Observed evidence architecture:

- strong framework papers typically report multiple tasks, comparators and concrete performance differences;
- multi-task synthetic/controlled evidence can be publishable when the paper's claim is explicitly about the framework/mechanism rather than deployment.

Q4 implication:

- npj AI is plausible if the six families are unified as a controlled mechanism benchmark, the matched-information contract is made machine-checkable, and statistical/uncertainty reporting is upgraded where the simulations sample stochastic worlds.

## 5. Editorial triage — Nature Machine Intelligence

**Posture:** `TECHNICAL_CASE_NOT_REVIEW_READY` for a real scientific-agent claim.

**Blocking reason:** the headline empirical evidence is synthetic and the target's scientific-discovery/agentic papers increasingly demonstrate meaningful real or naturalistic task behavior. The registered real-domain study is the appropriate closure.

**Repair:** `ADD_DECISIVE_EVIDENCE` for NMI; prose cannot close this.

## 6. Editorial triage — npj Artificial Intelligence

**Posture:** `SEND_TO_REVIEW_POSITIONING_RISK` after a substantial integration pass.

The evidence volume (six families plus donor/null controls) is sufficient to justify a mechanism/benchmark paper if the manuscript becomes a coherent benchmark theory rather than six loosely connected studies.

## 7. Reviewer lens 1 — VALIDITY / STATISTICS

### Q4-R1-V1 — synthesis is post hoc

- Class: `CLAIM_RECALIBRATION`.
- Concern: the common “epistemic bindings” hypothesis is inferred after separately frozen studies. It must not be described as one preregistered six-family theorem.
- Resolution test: label the taxonomy as post-study synthesis/theory building and preserve family-specific preregistered claims.
- Repair: `NARROW_CLAIM` / `CLARIFY_OR_RESTRUCTURE`.

### Q4-R1-V2 — uncertainty reporting for stochastic synthetic episodes

- Class: `MAJOR_REPAIRABLE`.
- Concern: N4-A/B/C/E/F3 report means/rates over seeded episodes but the manuscript mainly gives point estimates. For a journal paper, paired differences and uncertainty should be reported where episode-level stochasticity exists.
- Resolution test: deterministic publication-analysis rerun from the frozen seeds that emits episode-level paired contrasts and bootstrap or exact/Monte-Carlo confidence intervals without changing the frozen primary outcomes.
- Repair: `REANALYSE_EXISTING_EVIDENCE`.

### Q4-R1-V3 — heterogeneous metrics cannot be pooled

- Class: `CLARITY_OR_REPORTING`.
- Resolution test: main table reports family-specific outcome, paired comparator, effect measure, hostile/no-value control and exact scope; no universal aggregate effect.

## 8. Reviewer lens 2 — POSITIONING / SIGNIFICANCE

### Q4-R1-P1 — generic typed-memory novelty is donor-owned

- Class: already closed by current manuscript; retain.
- Requirement: related-work matrix should show MemIR / stale-memory / VoI / provenance systems versus Q4's matched-information scientific-decision tests.

### Q4-R1-P2 — contribution needs a reusable benchmark object

- Class: `MAJOR_REPAIRABLE`.
- Concern: the current paper can read as six small experiments. The reusable contribution is the family contract and taxonomy of epistemic-decision failure modes.
- Resolution test: publish a machine-readable benchmark index with common fields: binding axis, fact payload, decision, donor, hostile control, no-value control, seed/generator, metric, authority boundary.
- Repair: `CLARIFY_OR_RESTRUCTURE` + code/data package.

## 9. Reviewer lens 3 — REPRODUCIBILITY / BOUNDARY / READABILITY

### Q4-R1-R1 — main figure/table architecture

- Class: `MAJOR_REPAIRABLE`.
- Resolution test:
  - Figure 1: scientific epistemic-binding taxonomy and matched-information design;
  - Figure 2: six-family effect/control matrix;
  - Figure 3: selected paired/uncertainty plots for stochastic families;
  - Table 1: donors, null regimes and forbidden extrapolations.

### Q4-R1-R2 — benchmark and code availability

- Class: `CLARITY_OR_REPORTING`.
- Resolution test: one-command deterministic rerun of all six families plus publication-analysis output; availability statement names exact paths and licenses.

### Q4-R1-R3 — decimal precision

- Class: `MINOR/CLARITY_OR_REPORTING`.
- Concern: values such as `11.809659685355605` communicate numerical accident rather than scientific precision.
- Resolution test: retain exact value in receipt; manuscript rounds appropriately (e.g. 11.810) and states exact equality in the frozen output.

## 10. Editor synthesis

### NMI stretch

`EVIDENCE_BLOCKED` on real transfer.

### npj AI fallback

Plausible after:

1. unified taxonomy/benchmark object;
2. uncertainty/effect reporting from frozen episode-level reruns;
3. related-work/donor matrix;
4. figure architecture;
5. explicit post-hoc synthesis label and real-transfer boundary.

No new synthetic family should be added merely to increase count.

## 11. Round-one engineering scores

| Dimension | Score /10 |
|---|---:|
| problem_and_question | 8.5 |
| contribution_clarity | 7.4 |
| claim_evidence_alignment | 8.4 |
| technical_rigor | 8.0 |
| novelty_positioning | 7.2 |
| significance_or_field_advance | 7.3 |
| generality_and_boundaries | 6.5 |
| reproducibility_and_availability | 8.8 |
| figure_data_statistics_quality | 6.1 |
| writing_and_evaluability | 7.5 |
| venue_fit | 6.8 |

**Mean:** 7.50/10.

### Round-one terminal

- Nature Machine Intelligence: `EVIDENCE_BLOCKED`
- npj Artificial Intelligence: `CONTINUE_REFINEMENT__MECHANISM_BENCHMARK`
