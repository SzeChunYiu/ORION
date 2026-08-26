# P15 Scientific Execution Integrity fault protocol V1

**Programme:** #977 / P15 issue #979  
**State:** `FROZEN_BEFORE_EXECUTION`  
**Purpose:** establish bounded executable non-implications between attribution/replay/agreement and scientific validity before any broad systems-superiority claim.

## Separation object

The benchmark distinguishes five levels:

1. `ATTRIBUTABLE` — an execution can be bound to an invocation/content occurrence;
2. `REPLAYABLE` — the bound execution can be deterministically/reliably replayed under the declared envelope;
3. `AGREED` — two independently executing lanes emit matching result payloads;
4. `SCIENTIFICALLY_VALID` — an independent frozen scientific contract accepts the result;
5. `AUTHORIZED_CLAIM` — separate scientific authority permits promotion/commitment.

No lower level is treated as sufficient for a higher level without the additional registered premises.

## Frozen case facts

`sei_fault_cases_v1.jsonl` contains exactly 18 cases. Every candidate comparator receives the same facts. Facts include:

- invocation/input/result identity binding;
- spawn/host/capability failure;
- exit state;
- output completeness/cap sentinel;
- reap/finalization order;
- cleanup/unregister completion;
- retry accounting;
- occurrence uniqueness/replay freshness;
- coverage completeness;
- lane agreement when applicable;
- independent scientific-contract availability/result;
- separate claim-authority result.

The independent gold disposition is frozen separately in `sei_fault_gold_v1.json` before any scoring checker exists.

## Gold dispositions

- `AUTHORIZED_SCIENCE` — execution integrity, independent scientific validity and claim authority all pass;
- `VALID_BUT_NOT_AUTHORIZED` — scientifically valid execution exists but promotion authority is absent/denied;
- `INVALID_SCIENCE` — execution may be perfectly attributable/replayable/agreed but independent scientific contract rejects it;
- `EXECUTION_INVALID` — host/execution/publication integrity failed, so no scientific-success receipt is admissible;
- `CANNOT_CHECK` — required execution/scientific facts are unavailable or ambiguous.

## Frozen fault families

The 18 cases include at least:

- clean authorized success;
- clean valid-but-not-authorized result;
- process/spawn failure;
- timeout/termination failure;
- nonzero exit with misleading complete-looking output;
- exact-cap+1/truncation sentinel failure;
- finalization before reap;
- cleanup/unregister omission;
- retry-accounting corruption;
- stale/replayed invocation receipt;
- duplicate occurrence collision;
- input/result digest mismatch/forgery;
- coverage omission;
- complete valid receipt + invalid scientific content;
- dual-lane agreement on the same invalid scientific result;
- dual-lane disagreement with independent validity unavailable;
- valid science with lane disagreement but an independent verifier selecting the valid result;
- clean attributable/replayable valid science lacking claim authority.

## Comparators

### C0 — plain logs + exit status

Uses only nominal spawn/exit/output-presence facts. It represents a strong version of the common but scientifically insufficient pattern “process exited 0 and produced output.”

### C1 — structured provenance/receipt

Adds invocation/digest binding, output completeness, occurrence uniqueness, reap/finalization, cleanup, retry and coverage checks. It establishes execution integrity but does not infer scientific validity from those checks.

### C2 — replay/agreement product

Adds deterministic replay and, when present, dual-lane agreement. Agreement is evidence about reproducibility/consistency only.

### SEI — Scientific Execution Integrity reference contract

Requires C1 execution integrity, then an **independent scientific contract**, then independent claim authority for `AUTHORIZED_SCIENCE`. It never uses receipt completeness or lane agreement as a substitute for scientific validity.

The benchmark is not allowed to give SEI a hidden scientific label unavailable to other systems: every comparator receives the `scientific_contract_available` and `scientific_contract_valid` facts. The comparison tests whether their declared semantics use that evidence correctly rather than laundering execution evidence upward.

## Primary endpoints

- false `AUTHORIZED_SCIENCE` rate;
- false scientific-success admission among execution-invalid cases;
- invalid-science-as-success admission;
- false rejection of clean authorized science;
- valid-but-not-authorized laundering;
- correct `CANNOT_CHECK`;
- dual-lane wrong-agreement false reassurance;
- exact disposition accuracy.

A positive cannot be earned by blanket rejection: the frozen clean/valid cases must remain accepted at their correct level.

## Formal executable invariants

### H15.1 host/science separation

Any failed host/execution-integrity prerequisite prevents `AUTHORIZED_SCIENCE` regardless of output text.

### H15.2 exact binding

Invocation/input/result mismatch, duplicate/stale occurrence or incomplete output prevents authoritative success.

### H15.3 publication atomicity

Final authoritative receipt requires reap + required cleanup + valid retry accounting before finalization.

### H15.4 coverage is not validity

At least one frozen pair must have identical complete execution/coverage/replay properties but different scientific validity.

### H15.5 agreement is not validity

At least one frozen case must have lane agreement plus invalid science.

## Positive terminal

`P15_SEI_BOUNDED_FAULT_V1_GREEN` requires:

1. SEI zero false authorized-science admissions;
2. SEI zero false rejection on clean authorized cases;
3. SEI correctly separates valid-but-not-authorized and invalid-science cases;
4. H15.1–H15.5 executable witnesses pass;
5. structured/replay comparators are explicitly shown not to imply scientific validity on the frozen counterexamples;
6. two executions are byte-identical.

## Authority boundary

A GREEN result earns bounded executable SEI separation, not general systems superiority. Still pending are interoperability with real PROV/RO-Crate/workflow systems, broad fault injection against actual comparators, overhead/false-rejection measurements, external harness adjudication and final submission-day systems literature saturation.
