# Issue #210 checkbox audit (preparatory vs blocked on #209)

**Date:** 2026-08-17
**Status:** `PREPARATORY_AWAITING_ACTIVATION`
**Authorization granted:** **NO**
**Issue #209:** OPEN — this issue may not authorize a self-sustaining programme.

Tick rule: tick a box only when a merged, tested artifact on `main` satisfies
the checkbox as a *schema/protocol existence* claim. Do not tick operational
enforcement, executed cycles, live detection, longitudinal data, or the
terminal. Over-ticking would convert missing evidence into PASS.

| # | Checkbox | Class | Tick? | Evidence |
|---|----------|-------|-------|----------|
| CB1 | Candidate/LLM processes cannot mutate protected evaluators, held-outs, authority policy, phase rules, or programme termination criteria | BLOCKED_ON_209 | no | Live enforcement requires an authorized programme. Scaffolding has no writers; that is not operational custody. |
| CB2 | Missing evidence remains OPEN/CANNOT_CHECK; programme pressure cannot force positive conclusions | BLOCKED_ON_209 | no | Vocabulary and fail-closed battery exist in `#276`; live programme pressure does not. |
| CB3 | Null, harmful and rejected research directions remain immutable negative history | BLOCKED_ON_209 | no | Reopen ledger shape exists; no programme history is being written. |
| CB4 | Every programme-level state change is content/lineage/version bound and replayable | BLOCKED_ON_209 | no | `seal`/`verify_seal` exist; no programme-level state changes have occurred. |
| K1 | Explicit object/referent/claim/evidence identities | PREP_VERIFIED after `#276` | yes after merge | `orion.programme.object_knowledge` |
| K2 | Provenance and source-version binding | PREP_VERIFIED after `#276` | yes after merge | `ProvenanceBinding` |
| K3 | Contradiction/plural-view representation | PREP_VERIFIED after `#276` | yes after merge | `view_group_id` / `contradicts_object_ids` |
| K4 | Uncertainty/authority state | PREP_VERIFIED after `#276` | yes after merge | `ObjectAuthority` includes OPEN/CANNOT_CHECK |
| K5 | Dependency graph to measurements, methods and search-universe assumptions | PREP_VERIFIED after `#276` | yes after merge | `depends_on_coordinates` |
| W1 | Explicit versioned W/search-universe state | PREP_VERIFIED after `#276` | yes after merge | `search_universe_knowledge` |
| W2 | Source-family/domain/route coverage obligations | PREP_VERIFIED after `#276` | yes after merge | coverage fields on the W record |
| W3 | Blind-spot and saturation tests | PREP_VERIFIED after `#276` | yes after merge | `BlindSpotTest` |
| W4 | Typed unavailable/censored route state | PREP_VERIFIED after `#276` | yes after merge | `RouteAvailability` |
| W5 | Reopen rules when new domains/routes/representations appear | PREP_VERIFIED after `#276` | yes after merge | `ReopenRule` |
| M1 | Versioned methods with exact implementation/protocol identity | PREP_VERIFIED after `#276` | yes after merge | `method_knowledge` |
| M2 | Applicability/assumption boundaries | PREP_VERIFIED after `#276` | yes after merge | applicability fields |
| M3 | Causal support linking failures to interventions | PREP_VERIFIED after `#276` | yes after merge | `CausalSupportLink` |
| M4 | Replay and fresh-transfer evidence | PREP_VERIFIED after `#276` | yes after merge | transfer fields on the method record |
| M5 | Negative history and known failure classes | PREP_VERIFIED after `#276` | yes after merge | negative-history binding |
| D1 | New object evidence can invalidate search-universe closure and method applicability | PREP_VERIFIED after `#276` | yes after merge | typed dependency edges |
| D2 | New search-universe discoveries can reopen object claims and method comparisons | PREP_VERIFIED after `#276` | yes after merge | `apply_reopen` |
| D3 | New method knowledge can trigger remeasurement/reinterpretation without silently rewriting old evidence | PREP_VERIFIED after `#276` | yes after merge | supersession, not edit |
| D4 | Dependency-directed reopening is typed and auditable | PREP_VERIFIED after `#276` | yes after merge | `ReopenEvent` / ledger |
| D5 | Historical states remain reproducible after reopening | PREP_VERIFIED after `#276` | yes after merge | prior certificate byte-identical |
| G1 | Programme objectives and research-question queue policy | PREP_VERIFIED after this PR | yes after merge | `GovernanceFreeze` |
| G2 | Exploration/exploitation policy | PREP_VERIFIED after this PR | yes after merge | same |
| G3 | Budget/resource ceilings and stop rules | PREP_VERIFIED after this PR | yes after merge | same |
| G4 | Protected benchmark/held-out families and refresh policy | PREP_VERIFIED after this PR | yes after merge | same |
| G5 | Evaluator custody and versioning policy | PREP_VERIFIED after this PR | yes after merge | same |
| G6 | Search/web contamination policy | PREP_VERIFIED after this PR | yes after merge | same |
| G7 | External escalation/halt/revert conditions | PREP_VERIFIED after this PR | yes after merge | same |
| C1–C9 | Repeated protected research cycles (all nine "for every cycle" items) | BLOCKED_ON_209 | no | Protocol shape exists; zero cycles executed. |
| H1–H8 | Anti-collapse / hostile *detection* (live) | BLOCKED_ON_209 | no | Battery specs exist in `#276`; no live monitoring. |
| L1–L8 | Longitudinal sustainability evidence | BLOCKED_ON_209 | no | Schema exists; `assess_longitudinal()` is `CANNOT_CHECK`. |
| R1 | Machine-readable Phase-4 programme protocol | PREP_VERIFIED after `#276` | yes after merge | `build_protocol_document` |
| R2 | Machine-readable per-cycle receipts | PREP_VERIFIED after this PR | yes after merge | receipt *schema*; no receipts of executed cycles |
| R3 | Immutable evaluation-epoch manifests | PREP_RUNNABLE schema only | no | Schema exists; no live epoch has been frozen |
| R4 | Scripts regenerate programme trajectories, failures, costs and protected metrics | BLOCKED_ON_209 | no | Regenerator returns `CANNOT_CHECK` / `FAIL`; no real script against real cycles |
| R5 | Clean replay of accepted and rejected research cycles | BLOCKED_ON_209 | no | No cycles to replay |
| R6 | Permanent archival strategy for releasable programme state | PREP_VERIFIED after this PR | yes after merge | strategy document; `live_archive_populated` is false |
| R7 | Exact-final-head CI and independent reproduction before terminal promotion | BLOCKED_ON_209 | no | Explicitly refused by `validate_programme_receipt` |

**Counts:** 63 boxes. Tickable as preparatory schema/protocol after both merges: 15 (K) + 5 (D) + 7 (G) + 1 (R1) + 1 (R2) + 1 (R6) = 30. Blocked on #209 (must stay unticked): 4 (CB) + 9 (cycles) + 8 (hostile live) + 8 (longitudinal) + 4 (R3/R4/R5/R7) = 33.

Constitutional boxes stay **unticked** even though protocol text exists: they claim live enforcement, not document authorship.

## What this work does not do

- Does not close #210 or #209.
- Does not emit `PHASE_4_SELF_SUSTAINING_RESEARCH_PROGRAM_CLOSED`.
- Does not activate live `p4-programme*` / `p4-epoch-manifest*` / `p4-anti-collapse*` workflows.
- Does not create `src/phase4/` runners.
- Does not fabricate cycle results, epoch snapshots, or longitudinal PASS.
