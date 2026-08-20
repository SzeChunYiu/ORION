# P2-U GPT-R1 academic-paper-skills and framework audit

Date: 2026-08-20
Parent: #650
Base: `main@83abfc5c3a98606d9339b88024f83d1d4ab313e7`

## Academic-paper-skills scope

This pass applies the relevant contracts from `SzeChunYiu/academic-paper-skills`:

- `nature-academic-search`: current, venue-agnostic donor search with contradictory/limiting literature;
- `nature-ref-verifier`: verify load-bearing bibliographic metadata rather than copying discovery snippets;
- `nature-reviewer`: three independent lenses, here executed as separately frozen validity, prior-work, and reproducibility reports before synthesis;
- `nature-statistics`: task is the independent unit; repeated samples/remints are technical repeats; effect sizes and intervals precede significance language;
- `nature-polishing`: claim/evidence/boundary consistency pass after the scientific target is fixed.

No target journal is assumed. This is a generic high-rigor research-manuscript pass.

## Current donor frontier added after the first P2-U freeze

The 2026 deep-research frontier moved materially after the initial P2-U TeX:

1. **HALT** (`arXiv:2608.02009`, Roh & Han, 2026) treats stopping as claim-evidence coverage and shows that verification-aware stopping can reduce redundant search while largely preserving answer accuracy. This is direct donor structure for coverage-aware stopping.
2. **RAAC** (`arXiv:2608.15191`, Soudani et al., 2026) diagnoses reasoning stagnation and controls deep-research trajectories using retrieval novelty and information coverage. This is direct donor structure for adaptive retrieval/stopping control.
3. **LiveDRBench / Characterizing Deep Research** (ICLR 2026, Java et al.) formalizes deep research around high-fan-out concept exploration and reports large query-coverage gaps across current systems. This raises the route-generation and exploration baseline.
4. **ConfRAG** (ACL 2026) supplies real-world conflicting-reference evaluation. Contradiction-aware synthesis is therefore donor-owned rather than an ORION novelty phrase.
5. **MTRAG-UN** (ACL Findings 2026) stresses unanswerable, underspecified, non-standalone and unclear multi-turn retrieval regimes. Calibrated unresolved behavior must be compared against systems trained/evaluated for such conditions.
6. Existing EDR (`Don't Stop Early`, ACL Industry 2026), SAGE, DeepResearch Bench, capture-recapture/coverage estimation, query-conditioned state compilation, caching and systematic-review search remain donor-owned.

## Reviewer 1 — validity/methods, frozen

**Major P2-R1-01 — Stage-local success can masquerade as global discovery. Blocking: Yes for the largest claim.**
The manuscript correctly separates route generation, retrieval, processing and closure, but a final study must independently score each stage and make task-global closure non-compensatory. A gain in report quality cannot compensate for missed decision-relevant evidence or false closure.

**Major P2-R1-02 — Optionality needs future-query custody. Blocking: Yes for H3.**
Future queries/routes must be frozen before state construction and hidden from candidate systems. Otherwise an apparent optionality advantage can be produced by post-hoc selection.

**Major P2-R1-03 — Provider failures are authority failures, not comparator losses. Blocking: Yes.**
The current `CannotCheck` treatment is correct and must remain immutable.

## Reviewer 2 — prior work/contribution, frozen

**Major P2-R2-01 — Coverage/stopping novelty is already donor-saturated. Blocking: Yes for novelty wording, not for the higher-order claim.**
HALT, EDR and RAAC collectively own claim/evidence coverage, evidence-aware termination, novelty/coverage trajectory control and adaptive stopping. P2-U must absorb them into the donor-complete comparator.

**Major P2-R2-02 — The residual must move upward to joint discovery-control. Blocking: Yes.**
The surviving scientific question is whether ORION coordinates route invention, evidence acquisition, processing/state optionality and global closure across changing regimes better than a donor-complete controller, and whether a negative family yields a new transferable route/state/closure mechanic.

## Reviewer 3 — reproducibility/generalization, frozen

**Major P2-R3-01 — Independent unit must be the research task or predeclared task cluster. Blocking: Yes.**
Repeated model samples, search traces or reminted variants cannot inflate `n`.

**Major P2-R3-02 — Naturalistic transfer is mandatory. Blocking: Yes for GENERAL_OPEN_WORLD_DISCOVERY_SUPERIORITY.**
Authored hidden-route exact cases can establish mechanism non-vacuity only. The broad terminal needs held-out domains/source ecosystems and at least one systematic-review-like evidence set with independently curated relevance.

**Major P2-R3-03 — Baseline budget matching must include state-construction cost. Blocking: Yes.**
Compilation, caching, indexing, evaluator calls, retrieval and reasoning all consume the same total resource envelope.

## Editor synthesis

The largest P2-U claim remains scientifically coherent if donor ownership is broadened rather than the claim narrowed. The decisive residual is not a stopping rule. It is a **joint open-world discovery controller** that allocates effort across route generation, retrieval, processing/state preservation and closure, with calibrated `Unresolved/CannotCheck`, and that can learn or invent a new exploration/closure mechanic from a failure without losing clean-case utility.

## Framework consistency

Canonical `registry.py` and `FRAMEWORK_SNAPSHOT.json` agree on `0.3.9-shadow`, K/W/M and the registered mechanics. Relevant implemented/candidate substrate includes:

- `SEARCH.v1` and `SATURATE_BOUNDED.v3` for bounded search control;
- `RetrievalBenchmark.rakl-v1` and `BackwardMultiseedBenchmark.rakl-v1` for retrieval/search evaluation;
- `RouteFamilyHealth.rakl-v1` for longitudinal search-control telemetry;
- `EpistemicContextCompiler.rakl-v1` for candidate state compilation;
- `ExternalEvidenceManifest.v1` for external evidence authority.

`RouteFamilyHealth` explicitly declares itself search-control telemetry only. It cannot emit truth, abandonment or scientific-authority verdicts. That is consistent with P2-U's separation of route progress from task-global closure.

### Deliberately prospective, not current framework capability

- naturalistic hidden-route enumeration/coverage gold;
- a learned cross-domain controller jointly choosing route-generation, retrieval, processing/state and stop/continue actions;
- optionality-optimal compile/cache/recover policy;
- automatic invention of new exploration/closure mechanics;
- general open-world discovery superiority.

Verdict: `CONSISTENT_AS_PROSPECTIVE_EXTENSION`.

## Negative-to-positive research directive

Historical false-closure, missed-route, retrieved-but-unprocessed and provider-invalid outcomes remain immutable. The recovery target is positive, but no outcome deletion, margin relaxation, baseline weakening or post-hoc route exclusion is allowed.

The first successor mechanism family is **Obligation-Directed Adaptive Exploration (ODAE)**: maintain an explicit set of candidate scientific obligations, estimate which admissible action most reduces decision-relevant obligation uncertainty per charged cost, preserve unresolved route cues across state compression, and issue task closure only when every load-bearing obligation is independently discharged or explicitly `Unresolved/CannotCheck`.

Generic coverage estimation, value-of-information and adaptive stopping are donor-owned. The proposed residual is their responsibility-aware composition across route generation, evidence processing/state optionality and global scientific closure.

## Completion gate for the paper

The TeX may state this as a prospective programme. `GENERAL_OPEN_WORLD_DISCOVERY_SUPERIORITY` is earned only after protected naturalistic tasks show:

1. higher decision-relevant discovery/scientific utility versus the strongest runnable donor-complete comparator;
2. non-inferior or lower false closure with clean-closure utility retained;
3. held-out domain/source/route/query-shift transfer;
4. charged optionality/state costs;
5. at least one failure-derived exploration/state/closure mechanic with fresh transfer;
6. independent route accounting and evaluator custody.
