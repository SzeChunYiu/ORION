# P15 top-tier promotion V1 — Scientific Execution Integrity

**Programme:** #977  
**Existing state:** `DIRECTORY_OPENED / NO_PROTECTED_RESULT`; no scientific superiority authority.  
**Top-tier state:** `SCIENTIFIC_OBJECT_NOT_YET_EARNED`

## Maximum claim to earn

> **Scientific Execution Integrity (SEI):** execution provenance can establish attribution and replay properties without thereby establishing scientific validity. A fail-closed research harness should make this separation explicit: host/capability failures must never be laundered into scientific evidence, receipts must bind what actually executed, publication must be race-safe and non-coercing, and multi-lane agreement must remain distinct from correctness/validity.

P15 must not compete by claiming provenance, workflow packaging, reproducibility or proof-of-execution in general. Those are donor layers to absorb/interoperate with.

## Core separation ladder

Formalize and test the strict non-implications:

`ATTRIBUTABLE_EXECUTION`
`!= REPLAYABLE_EXECUTION`
`!= AGREEMENT_BETWEEN_EXECUTIONS`
`!= SCIENTIFICALLY_VALID_RESULT`
`!= AUTHORIZED_SCIENTIFIC_CLAIM`

Some implications may hold under additional premises; P15 must state those premises explicitly rather than collapse the levels.

## Formal harness invariants

### H15.1 — Host/science separation

A host, capability, transport, timeout, cleanup, resource-limit or protocol failure cannot produce a success/scientific-result receipt unless the scientific execution success conditions were independently satisfied.

### H15.2 — Exact invocation/result binding

Every scientific result receipt binds the exact invocation identity, relevant input/content digests, execution occurrence, output completeness/sentinel semantics, exit/reap state and declared environment/capability envelope.

### H15.3 — Publication atomicity

No partial/stale/duplicate/replayed invocation may race into a final authoritative receipt. Finalization must occur only after required execution/reap/cleanup phases, with fail-closed behavior under interruption and retry.

### H15.4 — Coverage is not validity

Complete execution coverage proves only that the declared execution obligations were attempted/recorded. Construct an explicit counterexample where coverage and receipts are complete but the scientific result is invalid because the scientific representation/evaluator contract is wrong.

### H15.5 — Dual-lane agreement semantics

For the ORION-Q dual harness, define what agreement establishes and does not establish. Two lanes agreeing on the same wrong result must remain distinguishable from independently validated correctness.

## Donor/interoperability matrix

P15 must explicitly compare/interoperate with applicable classes such as:

- generic structured logs/event sourcing;
- W3C PROV / RO-Crate-style workflow provenance;
- workflow engines and reproducible pipeline systems;
- content-addressed build/execution systems;
- sandbox/container execution receipts;
- cryptographic or signed proof-of-execution systems where applicable;
- deterministic replay systems;
- multi-run/ensemble agreement systems.

The strongest donor product should be allowed to export/import provenance into the P15 evaluation. P15's residual is the scientific-evidence admission boundary, not ownership of interchange provenance.

## Protected fault-injection benchmark

Freeze a large adversarial matrix before outcomes covering at least:

- process spawn/setup failure;
- timeout/signal/termination races;
- EAGAIN/EWOULDBLOCK/nonblocking readiness races;
- exact output cap and cap+1 sentinel behavior;
- truncated/partial output;
- nonzero exit with misleading output;
- helper/tool failure reported as success;
- cleanup/unregister omission;
- finalization before reap;
- retry exhaustion and retry-accounting corruption;
- stale invocation/result replay;
- duplicate occurrence/identity collision;
- missing prefix/coverage recurrence;
- directory/file boundary attacks;
- forged work/result deltas;
- invalid scientific content with perfectly valid execution receipts.

This benchmark should reuse existing hostile harness findings as design evidence but freeze a publication protocol independently.

## Comparator systems

At minimum:

1. plain logs + exit status;
2. structured provenance/manifest logging;
3. deterministic replay/content-addressed execution baseline;
4. strongest available signed/attested execution baseline feasible locally;
5. ORION single research harness;
6. ORION-Q dual-lane harness where the test applies.

All comparators receive identical fault injections and scientific payloads.

## Primary endpoints

- false scientific-success admission rate;
- false host-failure-as-science rate;
- missing/forged execution detection;
- stale/replay/duplicate receipt detection;
- output truncation/overflow detection;
- publication-race failures;
- correct `CANNOT_CHECK` / invalid-content disposition;
- replay fidelity;
- provenance interchange completeness;
- runtime/storage overhead;
- dual-lane agreement false reassurance rate;
- ability to separate attributable-but-invalid science from valid science.

## Independent authority

The fault injector and gold execution/scientific disposition must be independent from the candidate harness. Scientific validity of payloads must be supplied by a frozen external checker/contract; the harness may not infer validity from receipt completeness.

## Strongest hostile attacks

- ordinary provenance plus strict schemas matches every P15 property;
- signed receipts provide the same boundary at lower complexity;
- harness rejects too many valid executions and wins by fail-closed conservatism;
- receipt completeness is confused with evidence quality;
- dual-lane agreement is sold as correctness;
- cleanup/resource failures are hidden after a nominal success;
- retry/finalization semantics allow stale success replay;
- publication protocol differs from tested protocol;
- benchmark is tailored only to known ORION implementation bugs.

## Top-tier promotion gate

`P15_TOP_TIER_SUBMISSION_READY` requires:

- [ ] formal separation ladder and non-implication witnesses;
- [ ] H15.1–H15.5 executable or machine-checkable semantics;
- [ ] independent publication-specific fault-injection protocol freeze;
- [ ] broad adversarial benchmark executed against all comparators;
- [ ] donor/interoperability matrix including provenance/replay systems;
- [ ] near-zero false scientific-success admission under protected hostile cases;
- [ ] acceptable false rejection and overhead;
- [ ] explicit counterexamples showing receipt/coverage/agreement != validity;
- [ ] independent harness/result adjudicator;
- [ ] paper issue + claim/evidence ledger + submission manuscript;
- [ ] immediate pre-submission systems/provenance literature refresh;
- [ ] exact reproduction and artifact binding.

If generic provenance/replay systems already implement the same fail-closed scientific-admission semantics, P15 should become an interoperability/formal-equivalence systems paper rather than overclaim a new execution model.
