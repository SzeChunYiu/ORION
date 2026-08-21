# P12 Claim–Evidence Ledger

**Stable ID:** ORION-P12  
**Issue:** #665  
**Accounting owner:** #664

| Claim | Status | Evidence | Maximum authorized wording |
|---|---|---|---|
| state construction and reasoning can have different marginal value across tasks | SUPPORTED / EXISTENCE + CONTROLLED | formal construction + P12A | controlled heterogeneous resource worlds |
| joint allocation beats fixed `(1,1)` under identical two-unit budget | SUPPORTED | P12A + V2 adjudication | +0.342651 mean success gain |
| joint allocation beats both one-axis adaptive policies | **SUPPORTED / PRIMARY** | P12A + `P12A_PROTOCOL_ADJUDICATION_V2.json` | mean +0.334717 vs best one-axis; CI [0.286008,0.382693] |
| gain is positive in every held-out family | SUPPORTED | P12A | worst-family +0.158203 |
| joint policy gets more compute | FALSE | budget audit | every action satisfies `c+r<=2` |
| protected signals use outcomes | FALSE | construction/protocol | pre-outcome noisy requirements only |
| V1 runner alone satisfied every protocol gate | **FALSE / CORRECTED** | PR hostile review | replay was omitted from the V1 terminal path |
| exact frozen runner is byte-identical across two fresh executions | **SUPPORTED / REPLAY-ADJUDICATED** | V2 adjudicator | both SHA-256 = `0194bc094f5696583533af5baae41e7c339902603d3706c8a1d2a78493f98947` |
| adaptive test-time compute is novel to P12 | FALSE / DONOR-OWNED | current literature | do not claim |
| dynamic state/context selection is novel to P12 | FALSE / DONOR-OWNED | retrieval/memory/state literature | do not claim |
| two-axis state–reasoning allocation has controlled superiority under matched total compute | **SUPPORTED SYNTHESIS** | P12A + V2 protocol adjudication | strongest current paper claim |
| real LLM/prover superiority | OPEN | no real-system result | not authorized |

## Evidence correction

The original P12A executable evaluated seven frozen scientific gates but did not put the protocol's byte-identical replay requirement into its own terminal decision. That is an evidence-adjudication defect, not a change in the scientific comparison. The V1 runner terminal is therefore **non-authoritative alone**.

`verify_p12a_protocol_adjudication_v2.py` executes the unchanged V1 runner twice in fresh subprocess directories, hashes the complete canonical JSON, checks every original scientific gate, and only then emits the authoritative terminal. Both executions reproduce the committed scientific payload exactly with SHA-256 `0194bc094f5696583533af5baae41e7c339902603d3706c8a1d2a78493f98947`. No policy, seed, threshold, budget, metric, comparator, family, or outcome was changed.

## Donor subtraction

- Strategic/bandit test-time compute allocation owns adaptive reasoning-budget allocation across inputs.
- Constrained-policy test-time allocation owns accuracy-under-average-compute optimization and learned allocation policies.
- Adaptive in-context demonstration/generation and current “when to think” work own difficulty-conditioned reasoning allocation and adaptive inference effort.
- Retrieval, compression and query-conditioned state systems own adaptive state/context construction as a primitive.

## Residual novelty

P12's residual is not “adaptive inference.” It is the **resource-locus problem**: state construction and downstream reasoning are made symmetric actions inside one matched envelope, and the method must strictly improve over policies allowed to adapt either axis alone.

## Strongest authorized headline

> Under an identical two-unit resource budget across 16 held-out heterogeneous families, a frozen joint state–reasoning allocator reaches 0.8582 verified success and improves by +0.3347 over the better one-axis adaptive policy, with a family-block 95% CI [0.2860,0.3827] and +0.1582 worst-family gain. The exact frozen result is independently replay-adjudicated with two byte-identical payloads.
