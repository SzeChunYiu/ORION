# P14 Peer-Review Readiness Report

**Decision:** `READY_FOR_EXTERNAL_REVIEW_AS_CONTROLLED_GOVERNANCE-CONFORMANCE_RESULT`

## Five-lens hostile review

### Scientific-method lens

**Pass.** The paper evaluates claim-promotion decisions rather than research-text quality, separates generation from authority and has explicit fail-closed dispositions.

### Experimental-design lens

**Pass for the primary P14C result after corrections.** P14A's negative is preserved. P14B is now explicitly non-authoritative for two independent reasons: its full arm reused the gold adjudication function, and hostile review found that its realized generator did not implement all nuisance reminting promised by its protocol. P14C was frozen after the circularity finding, separates the adjudication case table from policy implementation and strips gold metadata before every policy call.

### Statistics / measurement lens

**Pass for controlled specification scope.** P14A reports mixture prevalence; P14B is diagnostic only; P14C tests conformance against an explicit case specification and is not presented as a natural-prevalence estimate. Useful-discovery recall prevents blanket abstention.

### Reproducibility / protocol authority

**Pass after explicit correction.** Hostile review found that the P14C V1 runner omitted the protocol's two-run byte-identity requirement from its terminal path. The V1 runner terminal is therefore non-authoritative alone. `verify_p14c_protocol_adjudication_v2.py` executes the exact V1 runner and frozen adjudication table twice in fresh subprocess directories, verifies all original gates, and makes the authoritative terminal contingent on byte identity. Both canonical payloads hash to `74032348de7e6508b6c1827aabcf1bf9d354d30b9c6f81c8259fdb3535f01a63`.

### Novelty / donor lens

**Pass after subtraction.** Autonomous research agents, goal evolution, reflection/debate, preregistration, truth maintenance, provenance and authorization are donor-owned. The residual is the composed scientific-promotion contract and its specification-separated conformance evaluation.

### Referee / reporting lens

**Pass for controlled conformance scope.** The evidence history now distinguishes four states cleanly: P14A negative; P14B diagnostic/non-authoritative; P14C scientific gates positive; P14C V2 replay adjudication authoritative. External scientific validity and real-agent superiority are explicitly held out.

## Checklist

- [x] generation vs scientific-authority separation
- [x] donor subtraction
- [x] protected discriminator/protocol freeze
- [x] explicit negative/subsumed history
- [x] interaction-only and CANNOT_CHECK dispositions
- [x] recursion stop/reopen semantics
- [x] strong raw/reflection/donor/multi-review baselines
- [x] useful-discovery productivity constraint
- [x] P14A negative retained
- [x] P14A root cause documented before successor
- [x] P14B circularity explicitly acknowledged
- [x] P14B nuisance-reminting protocol mismatch explicitly acknowledged
- [x] P14B removed from claim authority
- [x] P14C protocol/case table frozen before execution
- [x] P14C policy receives facts only; gold field stripped
- [x] P14C independent full-policy implementation
- [x] six component ablations
- [x] V1 P14C replay-gate omission disclosed
- [x] exact P14C runner/spec replayed in two fresh subprocesses
- [x] authoritative V2 replay adjudication
- [x] claim/evidence ledger updated
- [ ] blinded realistic multi-domain research packets
- [ ] matched frontier research-agent workflows
- [ ] independent human/model adjudication study
- [ ] longitudinal negative-history value under genuine regime change

## Referee-facing headline

> **Scientific governance is an evaluable decision contract.** Against a separately frozen specification, the full ORION-RSE implementation conforms to all registered promotion/retention/reopen cases and strictly outperforms partial review contracts without suppressing valid promotion; that conformance result survives the protocol's explicit replay gate. Whether those governance semantics improve real science remains an external blinded-adjudication question rather than a self-certified conclusion.
