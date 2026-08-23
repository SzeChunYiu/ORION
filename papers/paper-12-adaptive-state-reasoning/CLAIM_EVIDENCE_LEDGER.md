# P12 Claim–Evidence Ledger

**Stable ID:** ORION-P12  
**Issue:** #665  
**Accounting owner:** #664

| Claim | Status | Evidence | Maximum authorized wording |
|---|---|---|---|
| state construction and reasoning can have different marginal value across tasks | SUPPORTED / EXISTENCE + CONTROLLED | formal construction + P12A | controlled heterogeneous resource worlds |
| joint allocation beats fixed `(1,1)` under identical two-unit budget | SUPPORTED | P12A + V2 adjudication | +0.342651 mean success gain |
| joint allocation beats both one-axis adaptive policies because it reads both signals | **AUTHORITY WITHHELD / CANNOT_CHECK** | `P12A_COMPARISON_VALIDITY_ADJUDICATION_V1.json` | baselines' action-set ceilings are below the winner; no causal superiority wording |
| historical gain is positive in every held-out family | DESCRIPTIVE HISTORY ONLY | P12A | does not repair the capability confound |
| joint policy gets more compute | FALSE | budget audit | every action satisfies `c+r<=2` |
| protected signals use outcomes | FALSE | construction/protocol | pre-outcome noisy requirements only |
| V1 runner alone satisfied every protocol gate | **FALSE / CORRECTED** | PR hostile review | replay was omitted from the V1 terminal path |
| exact frozen runner is byte-identical across two fresh executions | **SUPPORTED / REPLAY-ADJUDICATED** | V2 adjudicator | both SHA-256 = `0194bc094f5696583533af5baae41e7c339902603d3706c8a1d2a78493f98947` |
| adaptive test-time compute is novel to P12 | FALSE / DONOR-OWNED | current literature | do not claim |
| dynamic state/context selection is novel to P12 | FALSE / DONOR-OWNED | retrieval/memory/state literature | do not claim |
| two-axis state–reasoning allocation has controlled superiority under matched total compute | **NOT AUTHORIZED** | `P12A_COMPARISON_VALIDITY_ADJUDICATION_V1.json` | identical budget did not mean identical action capability |
| real LLM/prover superiority | OPEN | no real-system result | not authorized |

## Evidence correction

Active terminal: `P12A_SUPERIORITY_AUTHORITY_WITHHELD`. The authority record is
`P12_ACTIVE_CLAIM_AUTHORITY_V1.json`, content-bound to
`P12A_COMPARISON_VALIDITY_ADJUDICATION_V1.json`.

The original P12A executable evaluated seven frozen scientific gates but did not put the protocol's byte-identical replay requirement into its own terminal decision. That is an evidence-adjudication defect, not a change in the scientific comparison. The V1 runner terminal is therefore **non-authoritative alone**.

`verify_p12a_protocol_adjudication_v2.py` executes the unchanged V1 runner twice in fresh subprocess directories, hashes the complete canonical JSON, checks every original scientific gate, and only then emits the authoritative terminal. Both executions reproduce the committed scientific payload exactly with SHA-256 `0194bc094f5696583533af5baae41e7c339902603d3706c8a1d2a78493f98947`. No policy, seed, threshold, budget, metric, comparator, family, or outcome was changed.

## Donor subtraction

- Strategic/bandit test-time compute allocation owns adaptive reasoning-budget allocation across inputs.
- Constrained-policy test-time allocation owns accuracy-under-average-compute optimization and learned allocation policies.
- Adaptive in-context demonstration/generation and current “when to think” work own difficulty-conditioned reasoning allocation and adaptive inference effort.
- Retrieval, compression and query-conditioned state systems own adaptive state/context construction as a primitive.

## Residual novelty

P12's residual is not “adaptive inference.” It is the **resource-locus problem**.
P12A motivates that problem but does not resolve it because signal count and
allocation capability varied together. P12B must make the actions symmetric
before measuring the value of an additional signal.

## Strongest authorized headline

> The exact P12A payload is reproducible, but 96.9% of its state-only contrast is
> beyond the shipped baseline's ceiling. Under the capability-matched reading,
> the gain is +0.0408 and the frozen superiority gate is not met. No active
> superiority claim is authorized before P12B.
