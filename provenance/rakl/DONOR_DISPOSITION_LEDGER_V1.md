# RAKL donor disposition ledger — V1

**Purpose:** issue #75 gate B / issue #7. Every RAKL `src/rakl/` module and every
`docs/` formalism receives a terminal, evidence-backed disposition against ORION
`main`. A disposition is a claim about *mechanism*, never about vocabulary: a
name in ORION with no consumer that branches on it is **ABSENT**.

**Audit basis:** RAKL at pinned commit `70f5f7c4`, verified byte-identical to
local HEAD for every file cited. ORION `main` on 2026-08-16. Three independent
audit passes partitioned by filename (a–f, g–p, q–z + docs), each grepping for
mechanism rather than name.

**Scoring rule that governs every row:** hits inside
`src/orion/self_orion/rakl_transfer.py` and the `src/orion/mechanics/*` default
plans are declarations (tuples of English strings). They never count as
ABSORBED. Benchmark-only callers are not runtime consumers.

## Coverage

| slice | modules | audited | NOT_APPLICABLE (harness/paper/provider) |
|---|---|---|---|
| a–f | 72 | 72 | ~20 |
| g–p | 94 | 56 | 38 |
| q–z | 43 | 40 | 3 |
| docs/formalisms | 13 read | 13 | — |

**Undispositioned donor families after this pass: 0.** Four `docs/` files were
ranked by formalism density but not read (`EPISTEMIC_NONINTERFERENCE.md`,
`CONTEXTUAL_METHOD_CAPABILITY_FRONTIER.md`, `MULTI_HOP_BRIDGE_COMPOSITION.md`,
`LATTICE_METROLOGY_AND_CAPACITY.md`, `TOKEN_BUDGET_AUTHORITY.md`) — CANNOT_CHECK,
listed as open below rather than rounded to dispositioned.

## Dispositions — ABSORBED (do not port)

| RAKL | ORION mechanism, with consumer |
|---|---|
| `epistemic_saturation.py`, `saturation.py` | `kernel/saturation.py` — basis fingerprint voids stale streaks; lineage-disjoint independence; `certifies_recall` fixed False. **Strictly stronger.** |
| `saturation_vector.py` | `self_orion/saturation_vector.py:103` + `resource_bound → cannot_check`; consumed at `invention_gate.py:62`. Stronger. |
| `hard_gates.py` | `kernel/hard_gates.py` — ported 2026-08-16, chronology pinned to round+fingerprint instead of author-declared boolean. |
| `experience_learning.py` | `experience/learning.py:101-380` — same ladder, real Ed25519 receipts; consumed `kernel/driver.py:180`. Stronger. |
| `v3_authority.py` | `experience/authority.py:133,193,250` — signature + exact bytes + chronology. |
| `child_operators.py` | `mechanics/decomposition.py:141-154` + `audit_recursive`. |
| `AUTHORITY_POSET.md` §2,§5 (5-axis non-escalation) | `knowledge/space.py:11-25,223`. **Caveat: every call site uses default GROUNDING axis.** |
| `SELF_EVOLUTION_EVIDENCE.md` §3 (Δ_D>0 ∧ Δ_A>0) | `self_orion/change_control.py:161-172`. |
| `method_specs.py` | `self_orion/rakl_transfer.py` (24/24 surfaces reconstructed). |

## Dispositions — PARTIAL (half present, half missing)

| RAKL | present | missing |
|---|---|---|
| `authority_ledger.py` | linear supersession over answers (`mechanics/answers.py:155`) | **revoke**; non-monotone active set; per-axis certificate ledger |
| `pre_action_receipt.py` | declared `frozen_at_round` (`kernel/gate.py:63`) | **derived** chronology; self-hashed receipt with discriminator inside the hash |
| `discovery_coverage.py` | 14 route kinds; earned independence (`knowledge/routes.py`) | route ensemble as **precondition on stopping** — `saturate.py` has 0 refs to it |
| `execution.py` | hash-chained ledger (`kernel/store.py:51`) | `invocation_id = SHA256(canonical spec)`; retry-identity |
| `evolution.py` | verdict ladder | **`AssuranceReserve` exposure counter** — `fresh_split` is a caller boolean |
| `evaluator.py` | `evaluator_artifact_hash` as unverified string | derived evaluator integrity |
| `claim_evidence.py` | file-granularity binding (`kernel/evidence.py`) | **sub-document span** binding |
| `evidence_lineage.py` | identifier-alias merge | **derivational ancestry** — two papers from one experiment count as two |
| `promotion.py` | fail-closed change control (`change_control.py:135`) | ref transaction; class-C refusal; `CANNOT_CHECK` distinct from reject |
| `evolution_archive.py`, `experience_policy.py` (ranking) | faithfully ported | **zero runtime consumers** — wiring, not porting |
| `problem_novelty.py` | near-verbatim `self_orion/novelty.py` | no consumer; `RAKL_TRIVIAL` absent |
| `typed_lattice.py` | typed relations + traversal (`knowledge/space.py`) | pairwise compatibility witness required for multi-atom construction |
| `research_trace.py`, `search_controller.py`, `subject_identity.py`, `tree.py`, `v3_metrology.py`, `v3_runtime.py`, `matched_microtrial.py`, `open_world_discovery.py`, `problem_fibre.py`, `formal_contracts.py`, `framework_freshness.py`, `core.py`, `memory.py`, `cycle_metrics_harvest.py`, `missing_operator.py`, `invention.py`, `invention_runtime.py`, `driver_learning.py`, `experience_substrate.py`, `self_bootstrap.py`, `research_cycle.py`, `release_manifest.py`, `shadow_artifact_hash.py`, `training_ladder/`, `round044_runtime_guards.py` | see per-slice audit | each has a named missing half in the audit record |

## Dispositions — ABSENT, ranked by what ORION could then REFUSE

Top of each slice, merged and deduplicated. Value = the refusal gained.

1. **`identity_saturation.py` + `identity.py`** — refuse to credit a flat round with empty/unresolved lineage as independent. **The audit found ORION fail-OPEN here; fixed 2026-08-16 (`PARTIALLY_IDENTIFIED_LINEAGE`).**
2. **`degeneracy_probe.py`** — refuse a benchmark score when a responder reading only ids beats the majority baseline. ORION hand-rolled this twice (`knowledge/parent_domains.py:115`, `benchmarks/parent_domain_replay.py:247`).
3. **`epistemic_noninterference.py`** — refuse a run where authority rose outside a registered promotion; no endpoint check catches it.
4. **`method_telemetry.py`** — refuse to credit a search as thorough when it cannot name what it retrieved-and-rejected, considered-and-passed, or which policy chose. `TaskEpisode` cannot express any of these.
5. **`similarity.py::validate_similarity_witness`** — refuse an analogy whose mapping family widened after the fit. Zero hits for `declared_before|posthoc|null_calibration` in ORION. *(Being ported in parallel by `research/rakl-donor-saturation-v2`.)*
6. **`claim_evidence.py` + `evidence_binding_certificate.py`** — refuse a claim whose cited span is not in the hashed source.
7. **`search_policy_learning.py::certify_search_root_cause`** — refuse a policy change on an uncertified diagnosis. `COUNTERFACTUAL` exists in ORION as an unconsumed enum.
8. **`failure_lattice.py` + `FAILURE_EXPERIENCE_LATTICE.md`** — refuse a retry without a `DifferenceWitness`. Spec written; ORION currently refuses no retry ever.
9. **`research_tool_inventory.py` + `research_memory.py`** — refuse reuse without a known-failure review. `related_failure_episodes` computed, never consulted.
10. **`token_budget.py`** — refuse a prompt whose size was estimated not measured. Only budget branch in ORION is an HTTP rate limiter.
11. **`authority_transport.py`** (non-amplification half) — refuse a derived claim minting an axis no source held.
12. **`root_coordinate_preservation.py`** — refuse search spend on a surrogate with no root-preservation receipt.
13. **`meta.py`** — change-class A/B/C ladder; class-C never auto-promotes; portfolio reallocation on a saturation wall.
14. **`multires_memory.py`** — refuse a lossy view as evidence.
15. **`math_context.py`**, **`measurement.py`** tri-state leakage, **`context_compiler.py`** (`CANNOT_COMPILE`), **`quantifier_compatibility.py`** (gluing scope), **`FORMAL_SYSTEM_SPEC` §3** uncertainty transport with independence witness, **`RAKL_QUANTITATIVE_EVALUATION_MODEL`** ALR/EUR/NHR (ORION hardcodes `0.0`) — all ABSENT.

Remaining ABSENT items (`amortization`, `application_feedback`, `artifact_*`,
`assimilation`, `assumption_sensitivity`, `atlas_gluing`, `availability_oracle`,
`backward_multiseed`, `breakthrough_learning`, `bridge_composition`,
`capability`, `challenge_learning`, `constructive_lattice`,
`content_addressed_archive`, `context_efficiency`, `current_work_coverage`,
`epistemic_evolution`, `epistemic_search`, `epistemic_sufficiency`,
`episode_admission`, `failure_learning`, `formal_oracles`, `formalism`,
`formal_signatures`, `framework_candidate_freeze`, `generator_transport`,
`gluing_learning`, `lattice_metrology`, `manuscript_saturation`,
`math_oracles`, `math_research_*`, `mechanism_compiler`, `meta_registry`,
`metacognition`, `metrology`, `model_criticism`, `promotion_attestation`,
`proof_dag`, `problem_solving_algebra`, `publication_gate`,
`rakl_cycle_metrics`, `reference_profile`, `repository_boundary`,
`research_identity`, `schema_reference_constraints`, `semantic_shortcut`,
`strategy_motifs`, `structural_*`, `summation_compatibility`,
`symbolic_discovery`, `unified_substrate`, `workspace`) carry M/L port value
and are dispositioned ABSENT with rationale in the per-slice audit.

## Dispositions — NOT_APPLICABLE

All `paper2_*`, `paper3_*`, `paper5_*` (34); `*_benchmark*` (7); provider
clients (`hosted_anthropic_client.py`); closeout stubs and 9-line aliases
(`ai_operator_demoted_closeout`, `associative_experience`,
`closest_parent_ablation`, `conceptual_basis_independence`, `epistemic_gps`,
`experience_to_method_promotion`, `learning_governance_factorial`,
`meta_history*`); proposal-only with no RAKL caller (`identity_reservation`,
`memory_coverage`, `memory_reference_resolution`, `project_runtime`,
`obstruction_transformation_corpus`, `pre_scratch_fibre_freeze`); repo-shaped
(`meta_history_v2/3/4`, `parent_evaluator`, `cli`); facades (`invention_api`,
`math_research_api`, `prepolymarket`, `v3`); `training_projection` (no weight
plane in ORION); `compatibility_complex` (naming alias); `EVALUATOR_DEPENDENCY_PINNING.md`
(one-time migration record; value is negative history only).

## RAKL negative history ORION must not repeat

1. Saturation was declared without a search-coverage gate
   (`OBSIDIAN_EXOGENOUS_DISCOVERY_FAILURE_044.json`). ORION's `saturate.py`
   still gates on route-kind *strings*, not route escape — open.
2. Assurance capacity is consumable (`SELF_EVOLUTION_EVIDENCE.md` §5). ORION's
   `fresh_split` is a boolean; the same holdout can be reused forever — open.
3. Development gain with assurance regression has a name in RAKL
   (`development_gain_with_assurance_regression`) and none in ORION, which
   collapses it into two independent reasons — open.
4. Equal bytes under different labels is `ALIAS_CANDIDATE`, deliberately not
   `DEDUPLICATED` (`research_identity.py:49`). ORION's `merge_identities` should
   be checked against this before trusted for anything semantic.
5. A protected-input rejection was preserved as evidence rather than engineered
   around (`EVALUATOR_DEPENDENCY_PINNING.md`). ORION's `kernel/registry.py:60`
   chronology pin is the analogous trust root; it must not be relaxed for a
   "clearly safe" check.
6. Byte-stable ≠ reproducible: pin resolved implementation identity, not tags.

## Open

- Four `docs/` formalisms unread (listed above) — CANNOT_CHECK.
- `route_family_health.py` — deferred; presupposes live route-execution history
  ORION does not yet generate.
- The donor-before-invention gate is asserted by this ledger's existence, not
  yet enforced in code.
