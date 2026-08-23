# P15 top-tier promotion V1 — Scientific Execution Integrity

**Programme:** #977  
**Existing state:** protected bounded SEI fault result + claim/evidence ledger + manuscript now exist; no broad real-system superiority authority.  
**Top-tier state:** `BOUNDED_SEI_OBJECT_EARNED__REAL_SYSTEM_PROMOTION_PENDING`

## Maximum claim to earn

> **Scientific Execution Integrity (SEI):** execution provenance can establish attribution and replay properties without thereby establishing scientific validity. A fail-closed research harness should make this separation explicit: host/capability failures must never be laundered into scientific evidence, receipts must bind what actually executed, publication must be race-safe and non-coercing, and multi-lane agreement must remain distinct from correctness/validity.

P15 must not compete by claiming provenance, workflow packaging, reproducibility or proof-of-execution in general. Those are donor layers to absorb/interoperate with.

## Post-outcome status — 2026-08-23

The publication-specific protocol, 18 hostile cases and independent gold dispositions were frozen before the reference checker. The protected run now returns `P15_SEI_BOUNDED_FAULT_V1_GREEN` with byte-identical replay. Exact evidence is bound in `top_tier/P15_SEI_RESULT_RECEIPT_V1.md` and `CLAIM_EVIDENCE_LEDGER_V1.md`.

Protected disposition performance:

| system | exact disposition accuracy | false authorized science | execution-invalid admitted as science | invalid science admitted as success |
|---|---:|---:|---:|---:|
| plain logs + exit/output | 0.2778 | 13 | 8 | 2 |
| structured receipt/provenance | 0.7222 | 5 | 0 | 2 |
| replay + lane-agreement product | 0.7222 | 4 | 0 | 2 |
| SEI reference contract | 1.0000 | 0 | 0 | 0 |

The replay/agreement product also false-rejects one independently verified valid case because the two lanes disagree; the SEI contract keeps independent scientific verification distinct from agreement.

Executable witnesses now cover all five bounded invariants:

- **H15.1:** every frozen execution-invalid gold case fails the execution-integrity prerequisite;
- **H15.2:** stale replay, duplicate occurrence, digest forgery and truncation block authoritative execution success;
- **H15.3:** pre-reap finalization, cleanup omission and retry-accounting corruption block authoritative execution success;
- **H15.4:** complete attributable/replayable execution can still carry invalid science;
- **H15.5:** two lanes can agree on invalid science, while lane disagreement can coexist with independently verified valid science.

**Earned claim:** the strict non-implication between execution integrity/replay/agreement and scientific validity/authorization is executable and non-vacuous over the frozen fault model, and the bounded SEI admission semantics exactly recover the independent gold dispositions. **Not earned:** superiority over real W3C PROV, RO-Crate, workflow engines, attested execution, or production research systems.

The exact result identities are also summarized in `papers/candidates/TOP_TIER_EXECUTION_LEDGER_2026-08-23.md`.

## Core separation ladder

Formalize and test the strict non-implications:

`ATTRIBUTABLE_EXECUTION`
`!= REPLAYABLE_EXECUTION`
`!= AGREEMENT_BETWEEN_EXECUTIONS`
`!= SCIENTIFICALLY_VALID_RESULT`
`!= AUTHORIZED_SCIENTIFIC_CLAIM`

Some implications may hold under additional premises; P15 must state those premises explicitly rather than collapse the levels.

The current protected fault corpus provides explicit witnesses for each non-implication needed by the bounded result. Wider real-system premises remain open.

## Formal harness invariants

### H15.1 — Host/science separation

A host, capability, transport, timeout, cleanup, resource-limit or protocol failure cannot produce a success/scientific-result receipt unless the scientific execution success conditions were independently satisfied.

### H15.2 — Exact invocation/result binding

Every scientific result receipt binds the exact invocation identity, relevant input/content digests, execution occurrence, output completeness/sentinel semantics, exit/reap state and declared environment/capability envelope.

### H15.3 — Publication atomicity

No partial/stale/duplicate/replayed invocation may race into a final authoritative receipt. Finalization must occur only after required execution/reap/cleanup phases, with fail-closed behavior under interruption and retry.

### H15.4 — Coverage is not validity

Complete execution coverage proves only that the declared execution obligations were attempted/recorded. The protected corpus now contains explicit complete-receipt/invalid-science counterexamples.

### H15.5 — Dual-lane agreement semantics

For the ORION-Q dual harness, define what agreement establishes and does not establish. The protected corpus now includes both agreement-on-wrong-science and disagreement-with-independent-validity witnesses.

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

The nearest-work refresh now explicitly donor-owns claim-aware artifact lineage, RO-Crate/Workflow Run RO-Crate and execution-provenance layers. P15's residual is the scientific-evidence admission boundary. Actual import/export interoperability with real donor systems remains unexecuted.

## Protected fault-injection benchmark

The bounded 18-case corpus is now executed and content-bound. It covers representative instances of:

- process/setup/execution validity failure;
- stale replay and duplicate occurrence;
- digest forgery;
- output truncation/incompleteness;
- pre-reap publication;
- cleanup omission;
- retry-accounting corruption;
- invalid scientific content with complete execution receipts;
- lane agreement on invalid science;
- lane disagreement with independent scientific verification;
- valid-but-not-authorized and `CANNOT_CHECK` dispositions.

The **broad** benchmark target remains larger: real host timing/signal/nonblocking/cap-sentinel faults, real workflow/provenance systems and non-toy scientific workloads.

## Comparator systems

The bounded benchmark contains semantic proxies for:

1. plain logs + exit/output;
2. structured receipt/provenance;
3. replay + lane agreement;
4. SEI reference admission semantics.

Top-tier broad authority still requires actual real-system comparator integrations where feasible, including signed/attested execution if an accessible donor exists.

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

The current 18-case benchmark has independent frozen gold dispositions committed before the checker. That is enough for the bounded corpus result. It is **not** a substitute for an independently implemented production harness/adjudicator over real donor systems and workloads.

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

- [x] formal separation ladder and bounded non-implication witnesses;
- [x] H15.1–H15.5 executable semantics on the protected corpus;
- [x] independent publication-specific fault-injection protocol/cases/gold freeze before checker execution;
- [ ] broad adversarial benchmark executed against real donor comparator systems and non-toy workloads;
- [x] donor/nearest-work matrix that explicitly cedes provenance/replay/claim-lineage ownership;
- [x] zero false scientific-success admission under the 18 protected hostile cases;
- [ ] acceptable false rejection and measured runtime/storage overhead on real workloads;
- [x] explicit counterexamples showing receipt/coverage/agreement `!=` validity;
- [x] independent frozen gold adjudication for the bounded corpus;
- [ ] independent implementation/adjudicator for the intended real-system claim;
- [x] claim/evidence ledger + submission-facing manuscript object;
- [ ] paper-identity/issue administrative closure if required by the programme registry;
- [ ] immediate pre-submission systems/provenance literature refresh;
- [ ] exact reproduction and artifact binding for the final real-system submission package.

If generic provenance/replay systems already implement the same fail-closed scientific-admission semantics, P15 should become an interoperability/formal-equivalence systems paper rather than overclaim a new execution model.
