# P14 Peer-Review Readiness Report

**Decision:** `READY_FOR_EXTERNAL_REVIEW_AS_CONTROLLED_GOVERNANCE-CONFORMANCE_RESULT`

**Active authority:** `P14_ACTIVE_CLAIM_AUTHORITY_V1.json` — active claim
`P14.CURRENT.CONTROLLED_CONFORMANCE`, scientific terminal
`P14C_SPECIFICATION_SEPARATED_GOVERNANCE_CONFORMANCE_SUPPORTED`, scoped to the
frozen 28-case seven-implementation register. **`external_validity: OPEN`.**

This report named no authority, while `MANUSCRIPT.md` and
`CLAIM_EVIDENCE_LEDGER.md` both cite V1. A readiness decision bound to nothing
cannot be flagged when the authority moves, because it is not reading from one.

The decision above is scoped by that terminal and by what the authority holds
open. Readiness is for the controlled conformance result on the frozen register;
external validity is `OPEN`, P14A remains a measurement that could not be taken
rather than a comparative negative, and P14B remains diagnostic because it
reuses its adjudication function. None of those becomes a real-science claim by
being declared ready for review.

## Five-lens hostile review

### Scientific-method lens

**Pass.** The paper evaluates claim-promotion decisions rather than research-text quality, separates generation from authority and has explicit fail-closed dispositions.

### Experimental-design lens

**Pass for the primary P14C result after corrections.** P14A's negative is preserved. P14B is now explicitly non-authoritative for two independent reasons: its full arm reused the gold adjudication function, and hostile review found that its realized generator did not implement all nuisance reminting promised by its protocol. P14C was frozen after the circularity finding, separates the adjudication case table from policy implementation and strips gold metadata before every policy call.

### Statistics / measurement lens

**Pass for controlled specification scope.** P14A reports mixture prevalence; P14B is diagnostic only; P14C tests conformance against an explicit case specification and is not presented as a natural-prevalence estimate. Useful-discovery recall prevents blanket abstention.

### Gate-attainability lens

**Pass after explicit reclassification.** Hostile audit asked whether each preregistered gate had a value the frozen protocol could produce, in both directions.

P14A's two failing gates read one quantity whose supremum over its own declared sampling support is `0.042326`, against bars of `0.05` and `0.08`. No admissible draw satisfies either; the best of five registered admissible worlds is `0.040250`, with attainment margins of `−0.009750` and `−0.039750`; the seven-gate conjunction had one reachable value. P14A's terminal, seed, thresholds and receipt are retained verbatim and its evidential disposition is recorded as `CANNOT_CHECK` — an unmeasurable gate, not a comparative negative. The emitter is separately shown responsive (3 of 3 capability worlds move the terminal), and the graded `ORION_RSE_FULL` arm is disclosed as the gold function that scores it (0 divergent points of 256), which is why three of its five passing gates read constants.

P14C's terminal is asked the same question over the coordinate it leaves free — which of the seven registered implementations occupies the graded slot. Exactly one clears all eight gates and six fail at least one, so the conjunction prints two terminals. P14A's `0.05` and `0.08` bars, registered unchanged, are both reachable here and both met at `0.142857`. One residual is disclosed rather than absorbed: `full_discovery_recall_one` is satisfied by every registered subject and therefore carries no refutation capacity over this register.

P14B is asked the same question and answers in two halves. Its terminal is reachable in both directions — the four component ablations its protocol registers, placed in the graded slot, make the conjunction print both its words, and no threshold is outside its statistic's reach. But only four of its eight gates could have gone either way: `full_discovery_recall_one` is satisfied by all nine arms in every admissible run and `matched_budget` reads a module literal, both hypothesis gates, and the two remaining unconditional gates are preconditions for which that is intended. Disposition `TERMINAL_REACHABLE__GATE_COUNT_INFLATED`; P14B's non-authoritative status is unchanged.

Adjudication: `P14_GATE_ATTAINABILITY_ADJUDICATION_V1.md` / `.json`, `verify_p14_gate_attainability_v1.py`.

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
- [x] P14A gate attainability measured; both failing bars shown unreachable under the frozen support
- [x] P14A terminal retained verbatim and reclassified `CANNOT_CHECK` rather than relabelled positive
- [x] P14A graded-arm/gold identity disclosed (0 of 256 divergent points)
- [x] P14C terminal shown reachable in both directions over the registered subject implementations
- [x] P14A's unchanged 0.05/0.08 bars shown reachable and met on the P14C benchmark
- [x] P14C `full_discovery_recall_one` disclosed as carrying no refutation capacity
- [x] P14B circularity explicitly acknowledged
- [x] P14B nuisance-reminting protocol mismatch explicitly acknowledged
- [x] P14B removed from claim authority
- [x] P14B terminal shown reachable in both directions over the registered component ablations
- [x] P14B disclosed as carrying four discriminating gates of the eight it publishes; `full_discovery_recall_one` and `matched_budget` satisfied by every admissible world
- [x] P14C protocol/case table frozen before execution
- [x] P14C policy receives facts only; gold field stripped
- [x] P14C independent full-policy implementation
- [x] six component ablations
- [x] V1 P14C replay-gate omission disclosed
- [x] exact P14C runner/spec replayed in two fresh subprocesses
- [x] authoritative V2 replay adjudication
- [x] claim/evidence ledger updated
- [x] P14D blinded external-validation acquisition contract frozen
- [x] P14D preflight rejects local self-certification of external custody
- [ ] blinded realistic multi-domain research packets
- [ ] matched frontier research-agent workflows
- [ ] independent human/model adjudication study
- [ ] longitudinal negative-history value under genuine regime change

## Referee-facing headline

> **Scientific governance is an evaluable decision contract.** Against a separately frozen specification, the full ORION-RSE implementation conforms to all registered promotion/retention/reopen cases and strictly outperforms partial review contracts without suppressing valid promotion; that conformance result survives the protocol's explicit replay gate. Whether those governance semantics improve real science remains an external blinded-adjudication question rather than a self-certified conclusion.
