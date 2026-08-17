# Phase-4 programme protocol `phase4-programme-protocol.v1`

Machine-readable form: `orion.programme.protocol.build_protocol_document()`,
schema id `orion.programme.protocol.v1`. The document is sealed with its own
content digest, so this prose and the emitted document can be checked against
each other.

**This protocol is pre-registered, not in force.** The document carries
`programme_status: PRE_REGISTRATION_SCAFFOLDING`, `authority_granted: false`,
`cycles_executed: 0`, `evidence_status: NO_PROTECTED_EVIDENCE`, and
`blocking_dependencies: ["#209", "#76"]`.

## Constitutional invariants

These correspond one-to-one with the Step-0 bullets of issue #210. Each names the
module that makes it fail closed rather than merely assert it.

| Id | Invariant | Enforced by |
|---|---|---|
| `P4-INV-1-PROTECTED-SURFACE-IMMUTABLE` | Candidate/LLM processes cannot mutate protected evaluators, held-outs, authority policy, phase rules or termination criteria | no writer exists in the package; `HC-EVALUATOR-GAMING` |
| `P4-INV-2-ABSENCE-IS-NOT-PASS` | Missing evidence stays `OPEN`/`CANNOT_CHECK`; programme pressure cannot force a positive | `records.Outcome`, `hostile.HostileCheckReport.blocked`, `HC-INSUFFICIENT-PROTECTED-EVIDENCE` |
| `P4-INV-3-NEGATIVE-HISTORY-IMMUTABLE` | Null, harmful and rejected directions are permanent | `dependency.validate_reopen_event`, `HC-HIDDEN-DELETION`, the P5 negative-history chain |
| `P4-INV-4-STATE-CHANGES-ARE-REPLAYABLE` | Every programme state change is content/lineage/version bound and replayable | `identity.seal`, `dependency.build_reopen_ledger` / `verify_reopen_ledger` |
| `P4-INV-5-NO-SELF-GRANTED-AUTHORITY` | Nothing here grants closure or self-sustaining authority | `grants_phase4_closure`, `ProgrammeReadinessReport` |

Invariant 5 is implemented the way `orion.self_orion.phase2_terminal` implements
its own: as a property that returns the constant `False`. A report that could
compute its own authority under some condition is a report that can be argued
into granting it.

## Layer 1 — object knowledge `orion.programme.object-knowledge.v1`

Extends `orion.core.claims.ClaimRecord` and `orion.core.evidence.EvidenceRecord`.
What those already carry — claim text, evidence ids, authority, contradictions —
is reused. What they do not carry is added:

- **Identity**: `object_id`, `referent_id`, `claim_id`, `evidence_ids`,
  `record_version` (monotone from 1).
- **Provenance and source-version binding**: every `ProvenanceBinding` carries
  `source_id`, `source_uri`, `source_family`, `source_version` and a SHA-256 of
  the content read. `source_version` is mandatory because silent substitution
  under a stable URI is otherwise invisible.
- **Contradiction and plural views**: `view_group_id` groups competing readings;
  `contradicts_object_ids` must be mutual, so a one-sided contradiction cannot
  hide the losing view. A `VERIFIED` claim that contradicts another requires a
  `resolution_certificate_id`.
- **Uncertainty and authority**: `ObjectAuthority` extends `ClaimAuthority` with
  `OPEN` and `CANNOT_CHECK`. An `OPEN` claim may carry no evidence — that is what
  open means — and can never be read as settled.
- **Dependency graph**: `depends_on_coordinates` (rooted `K`/`W`/`M` coordinates),
  `measurement_ids`, `method_record_ids`, `search_universe_record_id`. A
  `VERIFIED` claim must name the universe it was verified under, or its closure
  can never be reopened.

## Layer 2 — search universe `orion.programme.search-universe-knowledge.v1`

Extends `orion.core.search_universe.SearchUniverseState` with the distinction
that state cannot express: walked versus never attempted.

- **Versioned `W`**: `universe_id` + `universe_version`, active/candidate domains,
  routes, representations.
- **Coverage obligations**: per source family and domain, with the route kinds
  required to discharge them and the evidence that did.
- **Typed availability**: `RouteAvailability` separates `AVAILABLE`,
  `NOT_ATTEMPTED`, `UNAVAILABLE_TRANSIENT`, `UNAVAILABLE_STRUCTURAL`,
  `CENSORED_LEGAL`, `CENSORED_PAYWALL`. A non-available route must carry a reason.
- **Blind-spot and saturation tests**: `BlindSpotTest` results are three-valued.
  A saturation claim is refused unless every obligation is discharged, no route
  is `NOT_ATTEMPTED`, every blind-spot test actually ran, none found a blind spot,
  and no coverage residual is open.
- **Reopen rules**: a universe with no reopen rule is rejected — its closure would
  be permanent by construction.

## Layer 3 — method knowledge `orion.programme.method-knowledge.v1`

Extends `orion.core.method.MethodState`.

- **Implementation identity**: module path, source SHA-256, protocol id and
  protocol-document digest. A method version denotes exact bytes.
- **Applicability boundaries**: assumption plus the observation that violates it,
  each with a three-valued `checked` state. A method with no declared boundary
  claims to apply everywhere, which is not a claim that can fail, and is rejected.
- **Causal support**: failure class → single attributed stage → intervention →
  evidence. Multi-stage attribution is rejected; diffuse attribution is diffuse
  effort with an explanation's costume on.
- **Replay and fresh transfer**: `TransferEvidence` distinguishes the two. Fresh
  transfer must be independently verified *and* graded outside candidate custody.
- **Negative history**: cited entries must be bound to a chain digest, so
  uncommitted negative history cannot be edited after the fact.

`method_promotion_blockers` is deliberately separate from record validation: a
record can be well-formed and still have no business being selected.

## Steps 3, 4, 6 and 7 of issue #210

Not addressed here, and deliberately so. Programme governance (Step 3), executed
research cycles (Step 4), longitudinal evidence (Step 6) and per-cycle receipts
(Step 7) all require protected evidence that does not exist while #209 and #76
are open. Pre-registering the record shapes is legitimate; pre-registering the
results would be fabrication.
