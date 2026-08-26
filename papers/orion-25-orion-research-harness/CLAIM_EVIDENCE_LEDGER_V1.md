# ORION-25 Scientific Execution Integrity — claim/evidence ledger V1

**Paper:** ORION-ORION-25  
**Programme:** #977  
**Paper issue:** #979  
**Current strongest terminal:** `P15_SEI_BOUNDED_FAULT_V1_GREEN`  
**Top-tier external terminal:** `CANNOT_CHECK`

## C15.1 — execution integrity is not scientific validity

**Statement.** Under the frozen SEI V1 interface, complete/attributable/replayable execution does not imply scientific validity.

**Authority:** `BOUNDED_EXECUTABLE_VERIFIED`.

**Evidence:** `top_tier/P15_SEI_RESULT_RECEIPT_V1.md`, H15.4 pair `SEI-CLEAN-AUTH` vs `SEI-COMPLETE-INVALID-SCIENCE`.

**Scope:** exact frozen 18-case fault model. General philosophical principle is not claimed as novel.

## C15.2 — lane agreement is neither correctness nor required scientific authority

**Statement.** In the frozen interface, two lanes may agree on invalid science, and lane disagreement may coexist with an independently verified/authorized scientific result.

**Authority:** `BOUNDED_EXECUTABLE_VERIFIED`.

**Evidence:** H15.5: `SEI-DUAL-AGREE-WRONG`, `SEI-DUAL-DISAGREE-VERIFIED`.

**Nonclaim:** dual-lane systems are not generally bad; agreement remains useful reproducibility/consistency evidence.

## C15.3 — fail-closed SEI contract separates execution/science/authority on V1

**Statement.** On the frozen V1 cases, the SEI reference contract obtains 18/18 exact dispositions with zero false authorized-science admissions and zero false rejection of clean authorized cases.

**Authority:** `BOUNDED_EMPIRICAL_EXACT`.

**Evidence:** run `32645458435`, artifact `9494739942`, receipt SHA-256 `436ae0ed39fc9c0c58bcb8d50249222d979340669265aacd4c7dea605fccde51`.

**Comparator result:** plain log success, structured execution receipt and replay/agreement products all admit at least one invalid/unauthorized scientific result under their intentionally narrower semantics.

**Boundary:** this is a semantics/fault benchmark, not a matched implementation-performance comparison with W3C PROV/RO-Crate or production workflow systems.

## C15.4 — host/execution failures must not enter scientific evidence

**Statement.** The SEI contract rejects host/execution-integrity failures before scientific promotion, including spawn/timeout, nonzero completion, truncation, pre-reap finalization, cleanup omission, invalid retry accounting, stale/duplicate occurrence, digest mismatch and coverage omission in the V1 corpus.

**Authority:** `BOUNDED_EXECUTABLE_VERIFIED`.

**Evidence:** H15.1–H15.3 and 11 `EXECUTION_INVALID` cases in the V1 receipt.

**Framework synchronization:** current ORION harness has related implementation tests, but this paper ledger does not infer unexecuted production guarantees from the reference model.

## C15.5 — real-harness superiority over provenance/replay systems

**Statement sought.** An implemented SEI layer materially reduces false scientific-success admission versus strong actual provenance/replay/attestation comparators at acceptable false-rejection and overhead cost.

**Authority:** `CANNOT_CHECK`.

**Required evidence:** real interoperable adapters, prospectively frozen broad fault injection, matched execution access, external validity oracle, overhead/resource accounting, independent reproduction.

**No manuscript may state this as a result yet.**

## C15.6 — interoperability with RO-Crate/PROV and claim-aware observability

**Statement sought.** ORION-25 semantics compose with standard research-object/provenance and claim-aware artifact-lineage representations without requiring a competing metadata layer.

**Authority:** `SUPPORTED_BOUNDED` for the composition claim; `CANNOT_CHECK` for
claim-aware observability. **Updated 2026-08-24:** the prospectively frozen
provenance-interoperability study has landed, so the row no longer reads
`PROPOSED`. It evaluates 22 cases -- the 18 existing hostile SEI cases plus four
real ORION workflow receipts -- and shows the SEI admission boundary survives
representation through W3C PROV and RO-Crate / Workflow-Run structures. Its
protocol was frozen before the adapter and the independent checker, with one
pre-outcome correction to the fact vector made while no outcome existed.

What that supports is the composition half of the statement sought: the
separation is not obtained only by forcing users into an ORION-specific receipt
representation. It does not support the claim-aware observability half, which
has no study, and it grants no production or superiority authority -- C15.5
remains `CANNOT_CHECK` on its own requirements, which this study discharges only
one of.

**Donor ownership:** RO-Crate 1.3, Workflow Run RO-Crate, execution-provenance work and artifact-centered claim-aware observability are explicitly donor-owned in `top_tier/P15_NEAREST_WORK_DELTA_2026-08-23.md`.

## C15.7 — top-tier scientific systems claim

**Maximum statement sought.** Scientific execution needs a fail-closed admission layer that treats attribution, replay, agreement and attestation as evidence about
execution rather than substitutes for independent scientific validity and
claim authority, and this separation improves real research-execution reliability under broad faults at acceptable cost.

**Authority:** `CANNOT_CHECK` pending C15.5/C15.6 and external independent validation.

**The six are separate and none implies the next.** Execution attribution says
which run produced an artifact. Replay says a run can be repeated. Agreement
says two runs concurred. Attestation says a key signed a statement about one of
those facts. None of the four says the result is scientifically valid, and
scientific validity does not confer claim authority, which is a governance
disposition about what may be asserted. Attestation is the one most easily read
as more than it is: a signature is evidence that a specific party vouched for a
specific byte sequence, and a correct signature over a wrong result is exactly
as verifiable as one over a right result.

## C15.8 — cryptographic attestation composition is not scientific admission

**Statement.** Under the frozen attestation-composition V2 protocol, three-link Ed25519 chains over execution/environment/publication facts verify and fail closed against truncation, substitution, splice-with-partial-re-signing, reorder, replay and stale/consumed re-presentation (22/22-case corpus, all arms 100% detected), yet (a) collapsing the chain into the scientific-admission decision false-promotes `12` cases while the properly scoped cryptographic-only reading returns `CANNOT_CHECK` everywhere, and (b) a full key-set compromise is detected `0/6` at the signature layer and also false-promotes through `CHAIN_PLUS_SEI` (`6/6`) — key custody is an inherited, now explicitly registered premise, not something the signature layer observes.

**Authority:** `BOUNDED_EXECUTABLE_VERIFIED` (for the composition-and-boundary statement; C15.5 superiority remains `CANNOT_CHECK`).

**Evidence:** run `32664075763`, artifact `9499830847` (ZIP SHA-256 `fccf3b28f3f33af8b07a87eab6764742c7882de88018d65be16e2dba1dee3bff`), receipt `top_tier/P15_ATTESTATION_COMPOSITION_RESULT_RECEIPT_V2.md` with second independent implementation GREEN and all 13 agreement-table entries matching.

**False-rejection endpoints:** `0/11` chain-layer and `0/5` disposition-level over the full valid workload (7 execution-valid fault cases + 4 real receipts); `0/4` real false promotion. The admission layer does not win by rejecting everything.

**Scope:** frozen 22-case corpus, simulated per-role keys, full-compromise simulated by re-signing with genuine key material. No hardware-backed custody, external timestamping/KMS, or production Sigstore/in-toto product comparison is claimed.

## Publication rule

The bounded V1 result may be submitted as a controlled systems/semantics contribution if venue strategy requires, but `P15_TOP_TIER_SUBMISSION_READY` cannot be emitted until the real comparator/interoperability/independent-authority gates close.
