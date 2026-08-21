# P13 Claim–Evidence Ledger

**Stable ID:** ORION-P13  
**Issues:** #666, #668

| Claim | Status | Evidence | Maximum authorized wording |
|---|---|---|---|
| sufficiency is relative to a named downstream responsibility in the registered world | SUPPORTED / EXACT | equivalence-class support matrix | exact constructed-world result |
| historical P14A combined gate passed | **NEGATIVE / FALSE** | `0.0556640625 > 0.05` | never relabel positive |
| historical exact ladder itself matches intended Z1/Z2/Z3 responsibilities | SUPPORTED / EXACT | full enumeration | mathematical/control construction only |
| RCS has zero unsafe reuse in P13A | **SUPPORTED / PRIMARY** | P13A + `P13A_PROTOCOL_ADJUDICATION_V2.json` | 12,288 controlled held-out episodes |
| confidence-only has zero unsafe reuse | FALSE | 0.215576 unsafe rate | cannot claim confidence is equivalent |
| provenance-only has zero unsafe reuse | FALSE | 0.396159 unsafe rate | cannot claim provenance is equivalent |
| RCS verified correctness is 0.980713 | SUPPORTED | P13A | registered benchmark |
| RCS cost is materially below always raw | SUPPORTED | 2.8747 vs 5.7319 | controlled cost units; ~49.8% lower |
| RCS degenerates to always reopen | FALSE | zero unnecessary reopen | registered benchmark |
| RCS correctly emits CANNOT_CHECK on unsupported/nonrecoverable cases | SUPPORTED | 237/237 exact | registered benchmark |
| V1 runner alone satisfied every protocol gate | **FALSE / CORRECTED** | hostile PR review | replay gate was omitted from terminal path |
| exact frozen P13A runner is byte-identical across two fresh executions | **SUPPORTED / REPLAY-ADJUDICATED** | V2 adjudicator | both SHA-256 = `ea4006981e0c5027a56789014dd723059420f603e071e81990a903986f6e8d1f` |
| responsibility-carrying state eliminates unsafe reuse while avoiding always-reopen cost in the controlled benchmark | **SUPPORTED SYNTHESIS** | P13A + V2 protocol adjudication | strongest current paper claim |
| real-agent / safety-critical superiority | OPEN | no external domain result | not authorized |

## Evidence correction

The original P13A runner evaluated the frozen scientific efficacy/safety/cost gates but did not include the protocol's byte-identical replay requirement in its terminal decision. The V1 runner terminal is therefore **non-authoritative alone**. This does not alter the benchmark or any result.

`verify_p13a_protocol_adjudication_v2.py` runs the exact unchanged V1 executable twice in fresh subprocess directories, hashes the entire canonical payload, verifies all frozen scientific gates, and then adjudicates the protocol terminal. Both runs reproduce SHA-256 `ea4006981e0c5027a56789014dd723059420f603e071e81990a903986f6e8d1f`. No task, seed, threshold, comparator, recovery rule, resource cost or outcome was changed.

## Donor subtraction

- Statistical sufficiency/state abstraction own task-relative information preservation.
- Selective prediction owns confidence/abstention gating.
- Provenance/evidence-tracing systems own lineage and execution provenance.
- STALE-style work owns memory invalidation after later observations.
- Proof-carrying agent/action systems own certificate-bearing runtime governance.

## Residual novelty

The scientific residual is **responsibility-scoped state authority**: a compact state's certificate names what downstream responsibility it supports, what it omits, when a semantic/context/resource change forces reopening, whether raw state is actually recoverable, and who independently witnesses the claim. The efficacy test requires a safety–cost advantage over confidence, provenance and always-reopen controls.

## Strongest authorized headline

> Across 12,288 held-out controlled responsibility-shift episodes, RCS produces zero structurally unsafe reuse and zero unnecessary reopen with 0.9807 verified correctness, while confidence-only and provenance-only make 21.56% and 39.62% unsafe reuses; RCS costs about half as much as always reopening raw state. The exact result is replay-adjudicated from two byte-identical executions of the frozen runner.
