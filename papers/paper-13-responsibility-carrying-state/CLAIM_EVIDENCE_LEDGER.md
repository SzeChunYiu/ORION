# P13 Claim–Evidence Ledger

**Stable ID:** ORION-P13  
**Issues:** #666, #668

| Claim | Status | Evidence | Maximum authorized wording |
|---|---|---|---|
| sufficiency is relative to a named downstream responsibility in the registered world | SUPPORTED / EXACT | equivalence-class support matrix | exact constructed-world result |
| historical P14A combined gate passed | **NEGATIVE / FALSE** | `0.0556640625 > 0.05` | never relabel positive |
| historical exact ladder itself matches intended Z1/Z2/Z3 responsibilities | SUPPORTED / EXACT | full enumeration | mathematical/control construction only |
| RCS has zero unsafe reuse in P13A | **AUTHORITY WITHHELD / CANNOT_CHECK** | `P13A_OUTCOME_ENTAILMENT_ADJUDICATION_V1.json` | self-scored zero over zero reachable harm opportunities |
| confidence-only has zero unsafe reuse | FALSE | 0.215576 unsafe rate | cannot claim confidence is equivalent |
| provenance-only has zero unsafe reuse | FALSE | 0.396159 unsafe rate | cannot claim provenance is equivalent |
| RCS verified correctness is 0.980713 | SUPPORTED | P13A | registered benchmark |
| RCS cost is materially below always raw | SUPPORTED | 2.8747 vs 5.7319 | controlled cost units; ~49.8% lower |
| RCS degenerates to always reopen | DESCRIPTIVE FALSE | frozen action table | not an independently graded safety endpoint |
| RCS emits CANNOT_CHECK on certificate-declared unsupported/nonrecoverable cases | CONDITIONAL INTERFACE INVARIANT | frozen rule; 237 historical cases | conditional on certificate correctness |
| V1 runner alone satisfied every protocol gate | **FALSE / CORRECTED** | hostile PR review | replay gate was omitted from terminal path |
| exact frozen P13A runner is byte-identical across two fresh executions | **SUPPORTED / REPLAY-ADJUDICATED** | V2 adjudicator | both SHA-256 = `ea4006981e0c5027a56789014dd723059420f603e071e81990a903986f6e8d1f` |
| responsibility-carrying state eliminates unsafe reuse while avoiding always-reopen cost in the controlled benchmark | **NOT AUTHORIZED** | `P13A_OUTCOME_ENTAILMENT_ADJUDICATION_V1.json` | P13B requires independently graded support and matched frontier |
| real-agent / safety-critical superiority | OPEN | no external domain result | not authorized |

## Evidence correction

Active authority is split. `P13_ACTIVE_CLAIM_AUTHORITY_V1.json` keeps
`P13.EXACT.RESPONSIBILITY_RELATIVE_SUPPORT` as `SUPPORTED_EXACT` and sets
`P13A.EMPIRICAL.SAFETY_COST_SUPERIORITY` to `CANNOT_CHECK`. Active terminal:
`P13A_EMPIRICAL_SAFETY_COST_AUTHORITY_WITHHELD`.

The original P13A runner evaluated the frozen scientific efficacy/safety/cost gates but did not include the protocol's byte-identical replay requirement in its terminal decision. The V1 runner terminal is therefore **non-authoritative alone**. This does not alter the benchmark or any result.

`verify_p13a_protocol_adjudication_v2.py` runs the exact unchanged V1 executable twice in fresh subprocess directories, hashes the entire canonical payload, verifies all frozen scientific gates, and then adjudicates the protocol terminal. Both runs reproduce SHA-256 `ea4006981e0c5027a56789014dd723059420f603e071e81990a903986f6e8d1f`. No task, seed, threshold, comparator, recovery rule, resource cost or outcome was changed.

## Donor subtraction

- Statistical sufficiency/state abstraction own task-relative information preservation.
- Selective prediction owns confidence/abstention gating.
- Provenance/evidence-tracing systems own lineage and execution provenance.
- STALE-style work owns memory invalidation after later observations.
- Proof-carrying agent/action systems own certificate-bearing runtime governance.

## Residual novelty

The supported residual is the exact, conditional **responsibility-scoped state
authority** interface. The efficacy claim is prospective: it requires a P13B
certificate whose declared support can disagree with independently graded gold,
plus a matched cost/correctness frontier. `PROVENANCE_ONLY` and `UNQUALIFIED` are
identical policies in P13A and cannot count as two comparisons.

## Strongest authorized headline

> The registered finite construction proves that sufficiency is
> responsibility-relative and the RCS interface conditionally refuses reuse
> outside declared support. P13A's empirical zero-harm claim is withheld because
> its harm predicate is entailed by the action rule; P13B must grade against
> independently defined gold support.
