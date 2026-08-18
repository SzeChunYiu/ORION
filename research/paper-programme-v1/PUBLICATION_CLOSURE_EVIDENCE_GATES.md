# Publication closure evidence gates — issue #153

**Wave:** closure checklist + mechanical `PEER_REVIEW_READY` gate.  
**Programme owner:** #97 (`cursor/paper-97`).  
**Archive/submission package owner:** #160 (`cursor/paper-160`).  
**Classified against:** issue-#393 integration tree, content-bound by the paper/result checksum manifests (2026-08-18).
**Mechanical gate:** `make peer-review-ready-gate` (`python3 -m orion.publication.peer_review_ready`).

This file enumerates the shared Gates 0–9 from `JOURNAL_READINESS_STANDARD.md` / #97 against what is actually on `main`. It ticks only what the tree verifies. It does **not** convert `CANNOT_CHECK`, underpowered, or null results into a ready terminal.

## Mechanical rule

A paper may *claim* `PEER_REVIEW_READY` (asserted `**Terminal:**` / attestation file, not an “only when” done-definition) only if all of these exist:

- `JOURNAL_READINESS.md`
- `manuscript/main.tex`
- a claim ledger (`CLAIM_LEDGER*`)
- `protocol/PROTOCOL_V1.json`
- a `*PEER_REVIEW_READY*` attestation
- `REPRODUCE.md` or `reproducibility/`
- at least one file under `evidence/`

P1 H1 on the frozen 48-case TEST arm remains `NOT_SUPPORTED` / `UNDERPOWERED` (`TierRule.from_n(48)`). Promoting that arm still fails the gate. P1 readiness is instead authorized only when the separate v2.2.4 powered primary, disjoint replication, checksum manifests, exact independent verifiers, concordance record, bounded claim, and pre-outcome amendment all validate mechanically.

## Per-paper evidence-gate table

| Paper | Issue | Claimed terminal on `main` | G0 identity | G1 nearest-work | G2 manuscript | G3 freeze | G4 empirical | G5 mechanism | G6 figures/tables | G7 repro | G8 integrity | G9 submission | `PEER_REVIEW_READY` |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| P1 | #393 powered successor closure | **claimed** `PEER_REVIEW_READY` for bounded mechanical claim | PASS | PASS (rounds A--H plus closure pass) | PASS + 27-page PDF audit | PASS v2.2.4 primary + disjoint replication | PASS; V1 null retained, successor supported twice | PASS (5 direct ablations) | PASS (P1-1…P1-7, T1–T4) | PASS (80,696 rows independently rescored; DOI is filing-time) | PASS | PARTIAL (DOI/venue filing external) | **yes — bounded artifacts present** |
| P2 | #99 open / #157 | **not claimed** (`CANNOT_CHECK`) | PASS | PASS local | PASS | PARTIAL (offline freeze; live/Wide/Deep confirmatory unbound) | **BLOCKED** official Wide/Deep/SAGE/live | PARTIAL (offline ablations only) | PARTIAL (P2-2, P2-7, T2 intervals open) | PARTIAL | PARTIAL (contamination audit incomplete) | OPEN | **no** |
| P3 | #100 open | **not claimed** (`CANNOT_CHECK`) | PASS | PARTIAL (atlas exists; JOURNAL_READINESS absorb boxes still open; PR #270 owns ticks) | PARTIAL (manuscript present; results unpopulated) | PARTIAL | **BLOCKED** gold: 32 single-annotator, 0 `annotator-a`/`annotator-b` | OPEN | OPEN | OPEN | PARTIAL (`CANNOT_CHECK` retained) | OPEN | **no** |
| P4 | #101 closed | **claimed** `PEER_REVIEW_READY` | PASS | PASS (refresh if submit after 2026-08-31) | PASS | PASS protected V2 | PASS H1/H2; H3 **NOT_SUPPORTED** (honest null) | PASS (8 ablations) | PASS | PASS (release tag + independent headline replay) | PASS | PARTIAL (TMLR package yes; OpenReview ID external) | **yes — artifacts present** |
| P5 | #102 open / #159 | **not claimed** (`CANNOT_CHECK`) | PASS | PARTIAL (closure note on `main`; JOURNAL_READINESS still 0/87 ticked — owned by #102) | PARTIAL | **BLOCKED** campaign identities not frozen | **BLOCKED** live Copilot `MODEL_UNAVAILABLE`; #8/#76 not result-bearing | OPEN | OPEN | OPEN | PARTIAL (failed entitlement preserved, not a negative study) | OPEN | **no** |

## P1 — negative V1 history plus powered bounded successor

| Coordinate | On `main` | May this close `PEER_REVIEW_READY`? |
|---|---|---|
| Frozen TEST N | 48 cases (32 hidden-shift) | no |
| Prospective power | `PROSPECTIVE_POWER_V1.md`; H1 +0.05 needs far larger N; achieved `BELOW_TIER_D` | no |
| T2 `orion_full` × `P1.H1` | `NOT_SUPPORTED` (interval includes/below +0.05; n=48) | no — and must not be rewritten to `SUPPORTED` |
| Precision tier | `underpowered=True`; does not license H1 superiority | no |
| Live `orion_live_provider` | 48/48 scored, 0 `CANNOT_CHECK`, root success 0 | descriptive / underpowered, not a superiority close |
| Optional SciAgentArena cases | still open | no |
| Permanent DOI | still open (external) | no (Gate 7 leftover; not a fake scientific close) |

The separate `P1.epistemic-mutation-necessity.v2.2.4` successor contains 2,882 worlds per run, nine runnable arms, five direct ablations, a pre-bound primary and disjoint replication, and three assimilated strong parents. Both runs return `P1_MUTATION_NECESSITY_SUPPORTED`; each 40,348-row archive is independently reconstructed with zero score or analysis mismatches. This authorizes only the credential-free mechanical necessity claim and leaves every V1 row above unchanged.

Issue #278's negative V1 diagnosis remains archived. Issue #393 closes the separately versioned bounded successor without reinterpretation or pooling.

## Shared Gates 0–9 vs `origin/main` (detail)

Statuses: **PASS** = verified on `main`; **PARTIAL** = local substrate present, confirmatory evidence missing; **OPEN** = not started; **BLOCKED** = cannot close without external/credential/expert input; **HONEST-NULL** = executed and not supported.

### Gate 0 — claim coherence

| Paper | Status | Evidence on `main` |
|---|---|---|
| P1 | PASS | Stable ID, scoped residual, claim ledger `evidence/CLAIM_LEDGER_V1.md` |
| P2 | PASS | Discovery ≠ synthesis; claim ledger `evidence/CLAIM_LEDGER_V1.md` |
| P3 | PASS | Portrait residual scoped; `CLAIM_LEDGER_V1.md` at paper root |
| P4 | PASS | Non-compensatory authority residual; `evidence/CLAIM_LEDGER_V1.md` |
| P5 | PASS | No-self-promotion residual; manuscript present |

### Gate 1 — nearest-work

| Paper | Status | Notes |
|---|---|---|
| P1 | PASS | 36-row `NEAREST_WORK_MATRIX_V2.md`; SCION/MAST/failure-attribution gaps closed; rounds A--H assimilated into parents and ablations |
| P2 | PASS local | JOURNAL_READINESS §1 all ticked; SAGE struck rather than faked |
| P3 | PARTIAL | `NEAREST_WORK_DISPOSITIONS_V1.md` exists; JOURNAL_READINESS absorb boxes still `[ ]` (do not tick here — #270) |
| P4 | PASS | Saturated 2026-08-17; refresh if submit after 2026-08-31 |
| P5 | PARTIAL | `P5_NEAREST_WORK_CLOSURE_2026-08-16.md` + #102 comments; JOURNAL_READINESS still unticked (owned by #102/#159) |

### Gate 2 — manuscript

| Paper | Status | Notes |
|---|---|---|
| P1 | PASS | `manuscript/main.tex` compiles; results/limitations populated from archive |
| P2 | PASS | Canonical manuscript; Results bounded to offline + MetaSyn |
| P3 | PARTIAL | `manuscript/main.tex` exists; gold-study Results not executable |
| P4 | PASS | Anonymous TMLR manuscript, H3 null reported |
| P5 | PARTIAL | Canonical manuscript; external Results unpopulated |

### Gate 3 — prospective freeze

| Paper | Status | Notes |
|---|---|---|
| P1 | PASS | Historical V1 freeze retained; v2.2.4 primary and disjoint-replication world/execution receipts frozen before outcomes |
| P2 | PARTIAL | Offline manifest frozen; official Wide/Deep/live confirmatory freeze incomplete |
| P3 | PARTIAL | Protocol present; gold execution identities unbound |
| P4 | PASS | Protected V2 bindings + signed freeze |
| P5 | BLOCKED | #159: exact campaign subject/provider/model/evaluator/split/epoch still open |

### Gate 4 — empirical adequacy

| Paper | Status | Notes |
|---|---|---|
| P1 | PASS + HONEST-NULL | Historical V1 remains underpowered/`NOT_SUPPORTED`; bounded v2.2.4 primary and replication pass every registered gate |
| P2 | BLOCKED | Official Deep judge; admissible Wide ORION-vs-baseline; SAGE unavailable; live campaign |
| P3 | BLOCKED | Independent annotators absent; expert gold unresolved |
| P4 | PASS + HONEST-NULL | H1/H2 PASS; H3 `NOT_SUPPORTED` retained |
| P5 | BLOCKED | Copilot run `32003937947` is `CANNOT_CHECK` (`MODEL_UNAVAILABLE`), not a negative study |

### Gate 5 — mechanism identification

| Paper | Status | Notes |
|---|---|---|
| P1 | PASS | Five v2.2.4 ablations move the registered protected-sibling, dependency-binding, lower-level-exclusion, K/W/M-ordering, and budget mechanisms in both runs |
| P2 | PARTIAL | Offline ablations; external matched baselines incomplete |
| P3 | OPEN | Ablation campaign not run |
| P4 | PASS | Eight registered ablations |
| P5 | OPEN | Matched self-improvement baselines not executed |

### Gate 6 — figures/tables

| Paper | Status | Notes |
|---|---|---|
| P1 | PASS | Single-page vector protocol diagram, powered primary/replication figure, historical tables, powered contrast table, and 36-row nearest-work matrix all render in the audited PDF |
| P2 | PARTIAL | P2-2, P2-7, T2-with-intervals still need confirmatory campaigns |
| P3 | OPEN | P3-1…P3-7 / T1–T3 ungenerated from gold |
| P4 | PASS | Five figures + three tables from immutable V2 aggregates |
| P5 | OPEN | P5-1…P5-7 / T1–T3 ungenerated |

### Gate 7 — reproducible artifact

| Paper | Status | Notes |
|---|---|---|
| P1 | PASS | SHA-256 manifests; 80,696 rows independently rescored with zero mismatches; compiled PDF bound; DOI remains an external filing operation |
| P2 | PARTIAL | Offline `--check` path; no permanent archive/DOI; live archive missing |
| P3 | OPEN | Gold not independently annotatable from checkout |
| P4 | PASS | `orion-p4-v2-peer-review-ready` + saturated successor release |
| P5 | OPEN | No result-bearing archive |

Gate 7 leftovers that #160 owns once scientific terminals stabilize: permanent DOI/archive, journal template conversion, cover letters, independent PDF/claim audits.

### Gate 8 — integrity/authority

| Paper | Status | Notes |
|---|---|---|
| P1 | PASS | Protected candidate view; V1 null preserved; pre-outcome amendments additive; primary/replication hashes and terminals independently checked |
| P2 | PARTIAL | Contamination audit incomplete; SAGE not substituted |
| P3 | PASS local | Single-annotator corpus kept `CANNOT_CHECK` for agreement |
| P4 | PASS | Protected custody telemetry; H3 null preserved |
| P5 | PARTIAL | Failed Copilot entitlement preserved via #198/#199; not counted as a study result |

### Gate 9 — submission package

| Paper | Status | Notes |
|---|---|---|
| P1 | PARTIAL | Scientific/peer-review package complete; DOI, venue metadata, and cover letter require an external filing target |
| P2–P3, P5 | OPEN | Blocked on scientific terminals |
| P4 | PARTIAL | TMLR checklist/PDF/archive ready; OpenReview ID is an external filing step, not a scientific blocker |

## JOURNAL_READINESS checkbox census vs `main`

| Paper | Ticked | Open | This wave ticked | Left honestly open |
|---|---:|---:|---|---|
| P1 | scientific/content checklist complete | DOI/venue filing | powered primary + replication, independent verification, concordance, Figure P1-7, Table P1-T4, bounded attestation, compiled PDF audit | permanent DOI and venue metadata; V1 H1 stays `NOT_SUPPORTED`/`UNDERPOWERED` |
| P2 | 70 | 22 | none (owned by #99/#157) | official Wide/Deep, SAGE struck, live campaign, submission |
| P3 | 25 | 69 | none (PR #270 owns ticks) | independent annotators, gold study, baselines/ablations/results |
| P4 | 44 | 1 | none | OpenReview submission ID |
| P5 | 0 | 87 | none (owned by #102/#159) | freeze, hidden-cause execution, #8/#76, plots, submission |

## Remaining blockers to `PEER_REVIEW_READY`

1. **P1** — no scientific/content blocker for the bounded claim. DOI/archive, venue metadata, and a cover letter require a selected external target; do not relabel the n=48 V1 non-finding.
2. **P2** — admissible official Wide ORION-vs-baseline; official Deep only with a valid judge; SAGE remains unavailable; live cost-bearing campaign; then #160.
3. **P3** — two independent annotators + domain-expert gold; then matched study, plots, #160. PR #270 may tick stale local boxes; it cannot invent the second annotator.
4. **P4** — scientific terminal met. Remaining: OpenReview ID (external); literature refresh if submit after 2026-08-31; #160 grayscale/DOI-if-any polish if not already in the saturated release.
5. **P5** — freeze identities; hidden-cause splits; live/protected #8/#76 execution that is not `MODEL_UNAVAILABLE`; matched baselines; then #160.

#153 stays open until #98–#102 scientific terminals are actually `PEER_REVIEW_READY` **and** #160’s submission/repro packages exist. #98/#101 being closed is not sufficient: #98 closed a local freeze tranche, not the journal terminal.

## Coordination

- Do not edit `JOURNAL_READINESS.md` on P3 (PR #270) or P5 (#102/#159) from this wave.
- P1 may be marked ready only through the v2.2.4 successor validator; the V1 H1 row remains permanently negative.
- Archives, journal conversion, cover letters, independent PDF audits: #160 (`make journal-packages`).
- Machine-readable status JSON that also refuses invented readiness: `research/publication/scoreboard.py` (landed on `main` while this wave was in flight). This gate remains the fail-closed CI check for false `PEER_REVIEW_READY` claims and for promoting underpowered P1 H1.
- Programme master issue text: #97.
