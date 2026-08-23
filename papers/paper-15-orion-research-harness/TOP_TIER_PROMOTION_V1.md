# P15 top-tier promotion V1 — Scientific Execution Integrity

**Programme:** #977  
**Existing state:** bounded SEI fault result + real provenance interoperability + claim/evidence ledger + manuscript exist; no universal production-system superiority authority.  
**Top-tier state:** `SEI_PLUS_REAL_PROVENANCE_INTEROP_EARNED__PRODUCTION_PROMOTION_PENDING`

## Maximum claim to earn

> **Scientific Execution Integrity (SEI):** execution provenance can establish attribution and replay properties without thereby establishing scientific validity. A fail-closed research harness should make this separation explicit: host/capability failures must never be laundered into scientific evidence, receipts must bind what actually executed, publication must be race-safe and non-coercing, and multi-lane agreement must remain distinct from correctness/validity.

P15 must not compete by claiming provenance, workflow packaging, reproducibility or proof-of-execution in general. Those are donor layers to absorb/interoperate with.

## Post-outcome status — 2026-08-23

### Bounded hostile SEI result

The publication-specific protocol, 18 hostile cases and independent gold dispositions were frozen before the reference checker. The protected run returns `P15_SEI_BOUNDED_FAULT_V1_GREEN` with byte-identical replay. Exact evidence is bound in `top_tier/P15_SEI_RESULT_RECEIPT_V1.md` and `CLAIM_EVIDENCE_LEDGER_V1.md`.

Protected disposition performance:

| system | exact disposition accuracy | false authorized science | execution-invalid admitted as science | invalid science admitted as success |
|---|---:|---:|---:|---:|
| plain logs + exit/output | 0.2778 | 13 | 8 | 2 |
| structured receipt/provenance | 0.7222 | 5 | 0 | 2 |
| replay + lane-agreement product | 0.7222 | 4 | 0 | 2 |
| SEI reference contract | 1.0000 | 0 | 0 | 0 |

Executable witnesses cover H15.1–H15.5: host/science separation, exact binding, publication atomicity, coverage/receipt non-implication, and agreement/validity non-implication.

### Real provenance interoperability result

The donor-first interoperability protocol was frozen before adapter/scorer implementation. One pre-outcome correction expanded the execution-only round-trip vector because the first draft could not represent already-frozen cleanup/stale/pre-reap/coverage distinctions; that correction is recorded explicitly in the protocol chronology.

The executed study now returns `P15_PROVENANCE_INTEROP_V1_SUPPORTED` over `22` cases: all 18 hostile SEI cases plus four real ORION workflow receipts. The study uses the production `prov==3.1.0` W3C PROV implementation for PROV-JSON serialization/deserialization and a current RO-Crate 1.3 / Workflow-Run `CreateAction` projection.

Exact outcomes:

- W3C PROV-JSON normalized execution-fact round-trip: `1.0`;
- RO-Crate 1.3 / Workflow-Run projection round-trip: `1.0`;
- scientific-field leakage into provenance-only records: `0`;
- native-vs-imported SEI disagreements: `0`;
- provenance-only false scientific successes: `0`;
- real-receipt false rejection: `0`;
- real-receipt false promotion: `0`;
- mean serialized size: PROV-JSON `1619.636...` bytes/case, RO-Crate JSON-LD `2014.636...` bytes/case;
- independent second implementation: GREEN;
- deterministic replay: GREEN.

The real receipt set includes a bounded positive, an authoritative negative, a two-checker formal result, and a native-Lean execution whose stronger scientific claim is `CANNOT_CHECK`. Source papers, per receipt (auditable under `papers/SYNC_CONTRACT.md`): the bounded positive is P6's bounded ETS positive; the authoritative negative is P9's authoritative Qwen negative; the two-checker formal result and the native-Lean `CANNOT_CHECK` execution are P10 artifacts (bounded OCME positive and native-Lean record). The fixtures carry no new scientific authority here; they reuse dispositions already bound by their source receipts. That last case remains `CANNOT_CHECK` after both provenance round trips, demonstrating on a real execution record that provenance completeness is not scientific admission.

Bound receipt: `top_tier/P15_PROVENANCE_INTEROP_RESULT_RECEIPT_V1.md`. Current donor refresh: `top_tier/P15_INTEROP_LITERATURE_DELTA_2026-08-23.md`.

**Earned claim:** the execution-integrity/scientific-validity separation is executable and remains representation-independent when execution evidence is imported from real provenance standards. P15 can sit above, rather than compete with, W3C PROV and RO-Crate: provenance supplies execution evidence; an independent scientific/authority record supplies scientific admission. **Not earned:** universal superiority over cryptographic attestation/proof-of-execution products, large production workflows, or all host/runtime fault distributions.

## Core separation ladder

`ATTRIBUTABLE_EXECUTION`
`!= REPLAYABLE_EXECUTION`
`!= AGREEMENT_BETWEEN_EXECUTIONS`
`!= SCIENTIFICALLY_VALID_RESULT`
`!= AUTHORIZED_SCIENTIFIC_CLAIM`

The top two rungs are not semantics P15 defines: they are externally supplied frozen disposition types, donor-owned by the P6/P8 authorization layer (typing) and the P14 admission layer (decision), with P13-class responsibility-scoped sufficiency likewise entering only as a frozen disposition type. Every scientific disposition in P15's receipts is an imported frozen judgment from its source paper or a deterministic contract — never an output of the provenance layer, which records dispositions and does not decide them.

The protected fault corpus supplies explicit witnesses for each required bounded non-implication, and the provenance-interoperability study demonstrates that the ladder is not an artifact of a proprietary execution representation.

## Formal harness invariants

### H15.1 — Host/science separation
A host, capability, transport, timeout, cleanup, resource-limit or protocol failure cannot produce a success/scientific-result receipt unless scientific execution success conditions were independently satisfied.

### H15.2 — Exact invocation/result binding
Every scientific result receipt binds exact invocation identity, relevant input/content digests, execution occurrence, output completeness/sentinel semantics, exit/reap state and declared environment/capability envelope.

### H15.3 — Publication atomicity
No partial/stale/duplicate/replayed invocation may race into a final authoritative receipt. Finalization occurs only after required execution/reap/cleanup phases, with fail-closed interruption/retry behavior.

### H15.4 — Coverage is not validity
The protected corpus contains complete-receipt/invalid-science counterexamples; the provenance round-trip preserves them exactly.

### H15.5 — Dual-lane agreement semantics
The protected corpus contains agreement-on-wrong-science and disagreement-with-independent-validity witnesses; both survive provenance import unchanged.

## Donor/interoperability matrix

P15 explicitly donor-owns rather than reclaims:

- generic structured logs/event sourcing;
- W3C PROV entity/activity/agent provenance and exchange;
- RO-Crate research-object packaging;
- Workflow/Process Run Crate execution provenance;
- workflow engines and reproducible pipeline systems;
- content-addressed build/execution systems;
- sandbox/container execution receipts;
- cryptographic/signed proof-of-execution systems;
- deterministic replay systems;
- multi-run/ensemble agreement systems.

Actual interoperability is now executed for W3C PROV-JSON and an RO-Crate 1.3/Workflow-Run projection. The residual is the scientific-evidence admission boundary, not provenance interchange.

## Protected fault-injection benchmark

The bounded 18-case corpus is executed and content-bound. It covers process/execution validity failure, stale replay, duplicate occurrence, digest forgery, output truncation, pre-reap publication, cleanup omission, retry-accounting corruption, invalid scientific content with complete receipts, agreement on invalid science, disagreement with independent scientific verification, valid-but-not-authorized and `CANNOT_CHECK` dispositions.

The broad production target remains larger: real timing/signal/nonblocking/cap-sentinel faults, cryptographically attested systems, and non-toy workflow scale.

## Comparator systems

Current executed layers now include:

1. plain logs + exit/output;
2. structured receipt/provenance proxy;
3. replay + lane agreement;
4. SEI reference admission semantics;
5. production W3C PROV-JSON import/export;
6. current RO-Crate 1.3/Workflow-Run structural import/export.

A top-tier production-systems superiority headline would still require an accessible signed/attested execution comparator and broader host/runtime fault campaign. The higher **scientific-admission-above-provenance** claim no longer depends on proprietary provenance.

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

The fault corpus has independent frozen gold committed before its checker. The provenance-interoperability study has a second implementation that uses a different PROV extraction path and a separate execution-failure formulation; it agrees across all 22 cases. External human scientific adjudication remains necessary only for payload validity that cannot be supplied by deterministic scientific contracts.

## Strongest hostile attacks

- ordinary provenance plus strict schemas matches every P15 property;
- signed receipts provide the same boundary at lower complexity;
- harness rejects too many valid executions and wins by fail-closed conservatism;
- receipt completeness is confused with evidence quality;
- dual-lane agreement is sold as correctness;
- cleanup/resource failures are hidden after nominal success;
- retry/finalization semantics allow stale success replay;
- publication protocol differs from tested protocol;
- benchmark is tailored only to known ORION implementation bugs.

The real PROV/RO-Crate result directly addresses the first attack at representation/interoperability level: donor provenance is accepted and round-tripped, yet it does not itself supply scientific validity/authority.

## Top-tier promotion gate

`P15_TOP_TIER_SUBMISSION_READY` requires:

- [x] formal separation ladder and bounded non-implication witnesses;
- [x] H15.1–H15.5 executable semantics on the protected corpus;
- [x] independent publication-specific fault-injection protocol/cases/gold freeze before checker execution;
- [x] real W3C PROV interoperability with exact execution-fact round-trip;
- [x] current RO-Crate 1.3 / Workflow-Run structural interoperability;
- [x] donor/nearest-work matrix explicitly ceding provenance/replay/claim-lineage ownership;
- [x] zero false scientific-success admission under the 18 protected hostile cases;
- [x] zero false rejection/promotion on the four protected real workflow receipts;
- [x] explicit counterexamples showing receipt/coverage/agreement `!=` validity;
- [x] independent frozen gold for the fault corpus and independent second implementation for provenance interoperability;
- [x] claim/evidence ledger + submission-facing manuscript object + P15 issue (#979);
- [ ] broader production host/runtime fault campaign beyond the bounded corpus;
- [ ] cryptographic/signed proof-of-execution or attestation comparator if feasible under a frozen contract;
- [ ] production-scale false-rejection/runtime/storage characterization beyond the current small-corpus serialization measurements;
- [ ] immediate pre-submission systems/provenance literature refresh;
- [ ] exact final reproduction/artifact/manuscript binding.

P15 is therefore much closer to a top-tier systems review package: the provenance-interoperability objection is no longer hypothetical. The remaining scientific work is production-scale hostile breadth/attestation/cost characterization, not proving that the admission layer can coexist with real provenance standards.

If a signed/attested donor product already implements the same independent scientific-admission semantics, P15 should report the equivalence and interoperability result rather than manufacture a proprietary execution-model novelty claim.
