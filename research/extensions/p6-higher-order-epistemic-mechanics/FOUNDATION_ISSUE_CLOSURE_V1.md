# Higher-order foundations — bounded issue closure synthesis V1

Date: 2026-08-19  
Closure PR: #522

This synthesis does not create new formal objects. It records the issue-level consequence of the parent-formalism map and the finite closure checker already frozen in this PR.

## Expert-panel synthesis

Four lenses were applied to each foundation issue:

1. **Formal diagnosis / belief revision** — whether the proposed object is already supplied by model-based diagnosis, AGM-style revision, minimal repair, sufficiency, metareasoning or epistemic/game-theoretic parents.
2. **Scientific-interface design** — what ORION still needs as a typed, fail-closed interface even when the mathematical primitive is donor-owned.
3. **Hostile countermodels** — whether ambiguity, missing authority, correlated evidence, nonpositive compute value, or containment can be incorrectly promoted into a scientific rewrite.
4. **Claim ownership** — whether a useful ORION composition is being mistaken for standalone mathematical novelty.

The common result is subtraction, not rollback: retain the typed interfaces; strike broad ownership claims.

## #452 — revision responsibility

Candidate terminal after exact-head merge: `FOUNDATION_NARROWED_TO_EXISTING_THEORY`.

The surviving ORION object is a typed, non-authorizing responsibility-to-revision interface. Competing/minimal diagnoses, discriminating observations and minimal/iterated belief change are mature parents. ORION's useful boundary is that identifying a responsibility is not the same transition as authorizing a protected scientific write, and unresolved/incomparable responsibilities remain unresolved rather than being tie-broken by confidence.

This does not establish a universal revision ontology. New domain-specific responsibility classes may still be registered by later studies without reopening the broad novelty claim.

## #458 — epistemic computation allocation

Candidate terminal after exact-head merge: `NO_INCREMENTAL_VALUE` for a standalone ORION metareasoning novelty claim.

Rational metareasoning/value-of-computation owns generic decisions about whether more computation is worth its cost. ORION retains an engineering/scientific composition rule: hard verification or authority obligations cannot be compensated away by scalar expected value, and a local decision not to compute is not global scientific closure.

The RLC-2026 harvest strengthens rather than weakens this disposition: compute-aware agents, selective planning and explicit waiting are direct parents, so a future empirical scheduler should be treated as an application/composition study rather than ownership of metareasoning.

## #459 — interface adequacy

Candidate terminal after exact-head merge: `EXISTING_DIAGNOSTICS_SUFFICIENT`.

Blackwell-style informativeness, state abstraction/sufficiency, active sensing and representation-alignment parents already supply the central scientific distinction: an observation/state/interface can be inadequate for a task without implying the model class itself is wrong. ORION keeps a registered fail-closed check and routing interface so required failures or unresolved checks block broader escalation.

This is intentionally narrower than a new universal theory of interface adequacy. Active perception, common-state compatibility, reward/interface co-construction and grounding remain domain-specific diagnostics or later empirical studies.

## #462 — social epistemology

Candidate terminal after exact-head merge: `EXISTING_SOCIAL_THEORY_SUFFICIENT`.

Common-knowledge/dependent-information, strategic-learning and causal-credit parents own the broad theory. ORION keeps the concrete provenance-dependence rule that multiple reports with one source are not independent evidence, and keeps hidden contribution/strategic reporting as reasons to remain unresolved.

The result does not claim a new social epistemology. It only places social evidence inside the same protected authority flow as other evidence.

## #463 — higher-order calculus

Candidate terminal after exact-head merge: `FORMAL_COMPONENTS_ONLY_NO_UNIFIED_CALCULUS`.

The finite checker shows that the implemented T1–T7 contracts can remain useful while the unified-calculus claim is struck. No new cross-component mathematical primitive is required at the current registered resolution. T8 remains a separate prospective empirical discriminator and does not gain efficacy from this formal closure.

## Consequence for papers

- P6 successor text should describe the retained typed/non-authorizing composition and the negative unification result.
- P1/P5 may reference responsibility/interface/computation contracts only as shared substrate, not as new standalone results.
- P4/P8 remain the authority owners.
- Any later empirical positive for a domain-specific interface, metareasoning or social mechanism must be versioned as a new study rather than reopening these broad ownership claims by default.

## Merge gate

None of the five issue terminals is authorized by this document alone. Close #452/#458/#459/#462/#463 only after the exact final #522 head has required repository `ci` and `p6-p8-candidate-ci` green and the PR is merged.
