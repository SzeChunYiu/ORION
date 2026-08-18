# P6 additive bridge — claim-relative structural signatures and method fibres

**Status:** additive successor text for #417/#419. The current P6 V2.1 manuscript, formal core, PDF, content manifest and peer-review terminal remain historical authority and are not rewritten by this extension. This document is the insertion-ready successor manuscript surface. The frozen submission directory is intentionally byte-unchanged.

## Concrete realizations and structural reduction

P6 does not redefine P1's concrete method object. It consumes the `MethodRealization.v1` field vocabulary owned by #404 through the version-gated `P6.P1MethodRealizationAdapter.v1`. If P1 changes that upstream schema, the adapter must version-bump before P9 may consume it.

The reconciliation is explicit:

| P1-owned coordinate | P6 formal input | status in P6 |
|---|---|---|
| `method_id`, exact source/version identity | realization id + source digest | mandatory identity |
| target/problem-role signature | reduction context | claim-relative |
| preconditions | `preconditions` | claim-relative |
| assumptions/resources | reduction context | claim-relative; resources optional when immaterial |
| representation-in/out | reduction context | optional but must be classified if present |
| transformation/mechanic graph | `actions` + `dependencies` | claim-relative |
| invariants/protected properties | `invariants` | claim-relative |
| progress measure | reduction context | optional but must be classified if present |
| effect contract | `effects` | claim-relative |
| terminal condition | `termination` | claim-relative |
| reconstruction map | `reconstruction` | claim-relative |
| failure/dead-end semantics | `failures` | claim-relative |
| lineage/provenance | `lineage` + adapter receipt | mandatory lineage |
| authority boundary | adapter receipt | mandatory and non-escalating |
| unknown coordinates | explicit unresolved fields | never fabricated |

The compact P6 view retains the coordinates needed by the existing formal calculus, while `P6.P1MethodRealizationAdapter.v1` content-binds the P1-owned context that is not collapsed into those nine formal fields. Thus P6 consumes P1 rather than creating a competing method schema.

A structural reduction is always **claim-relative**:

`π_C : R → S_C`.

`StructuralReduction.v1` binds the claim, preserved/erased/unresolved coordinates, load-bearing coordinates, preservation obligations and exact erasure justifications. `P6.StructuralReductionProcedure.v1` additionally binds the transformations and normalizations applied while forming the reduction and requires every P1 context coordinate present in the adapter to be classified as preserved, erased or unresolved. There is no universal context-free object called “the structure of the method,” and no present coordinate may disappear silently.

Typical procedure operations include domain-object renaming to structural roles and canonical normalization of an ordered state representation. These operations are descriptive/formal only; they carry no transfer, novelty, utility or adoption authority.

`StructuralSignature.v1` is content-bound to its reduction and primary realization. `P6.StructuralSignatureContract.v1` binds the contributing realization provenance, load-bearing coordinates, effect-equivalence obligations and reconstruction-equivalence obligations. If a preserved coordinate is unknown, the signature is `UNRESOLVED`. If a load-bearing erased coordinate lacks preservation evidence, it remains `UNRESOLVED`; evidence that the erasure is unsound yields `OBSTRUCTION`. A signature grants neither transfer nor novelty authority.

## Claim-relative method fibres

`MethodFibre.v1` denotes realizations admitted under one supported signature and declared claim:

`F_s = π_C^{-1}(s)`.

Membership is evidence-bound. Compatible assumptions, invariants, effects, reconstruction and provenance must be established, and agreement on one finite panel is explicitly insufficient: that case remains `UNRESOLVED`. A `P6.FibreLineageIndex.v1` binds each admitted member digest back to its upstream P1 adapter receipt, so a fibre cannot erase donor/source lineage.

Membership therefore means **equivalent under this declared reduction for this declared purpose**, not globally identical algorithms or proofs.

### Worked cross-domain illustration: bisection and threshold calibration

This is an explanatory structural example, not empirical evidence that arbitrary domains share fibres.

A numerical bisection procedure and a monotone experimental threshold-calibration procedure can have very different surface objects:

- bisection manipulates a numeric interval and evaluates a function sign;
- threshold calibration manipulates a dose/control interval and runs a binary assay/classifier.

For the narrow claim **bounded monotone threshold localization**, both can instantiate the same retained contract if evidence supports:

1. an ordered interval with the target initially bracketed;
2. a midpoint probe;
3. an invariant that the retained half still brackets the target;
4. an abstract effect `shrink_interval`;
5. a progress measure based on interval width;
6. a termination rule `width <= ε`;
7. a reconstruction returning a representative point/interval in the original domain.

The reduction may erase domain nouns and native probe names only because those coordinates are not load-bearing for this declared claim. The member-specific implementations and provenance remain recoverable.

### False fibre: same surface loop, erased monotonicity

Now keep the same visible sequence—“probe midpoint, discard half, repeat”—but apply it to a non-monotone response where the target may leave the retained interval. If the reduction erases the monotonicity/bracketing assumption or protected invariant, the apparently identical action graph is a **false fibre**. Membership must be `BLOCKED` when incompatibility is evidenced, or `UNRESOLVED` when the required assumption/invariant evidence is missing. Surface similarity is therefore insufficient.

## Faithful substitution and composition

Compatible-realization substitution is first-class in `P6.CompatibleRealizationSubstitution.v1`. Both realizations must already have supported membership in the same signature, and interface, invariant, effect, reconstruction and relevant authority-boundary preservation must each be supported. Any false obligation blocks substitution; missing evidence remains `UNRESOLVED`. A compatible substitution receipt still carries `can_authorize_transfer=false`: P4/P8 own scientific transfer authority.

Composition closure is conditional, not automatic. `CompositionContract` covers:

- sequential composition;
- conditional composition;
- parallel/independent composition;
- recursive composition with explicit well-foundedness.

The executable checks reject or leave unresolved read/write collisions, right-precondition loss, hidden dependencies, authority escalation and recursive nontermination/unknown well-foundedness. `classify_fibre_composition` then makes the missing distinction explicit:

- `STAYS_IN_FIBRE` only when the composition is compatible, the retained contract is preserved and no footprint changes;
- `NEW_SIGNATURE_REQUIRED` when the composition is individually admissible but changes the retained contract/footprint;
- `BLOCKED` for incompatible composition;
- `UNRESOLVED` when the relevant compatibility evidence is incomplete.

Thus two valid methods do not automatically compose into another member of the original fibre.

## Generalization, specialization and representation change

Generalization and specialization are directional, not aliases for equivalence. `P6.StructuralPreorderWitness.v1` records the claim-relative relation under explicit obligations. On the supported finite formal examples the relation is reflexive and transitive under the declared set-inclusion semantics, which is enough to provide an explicit preorder for these structural signatures. The witness explicitly carries `can_grant_fibre_membership=false`: order alone never establishes equivalence.

A specialization may strengthen preconditions while preserving the required effect. A generalization must demonstrate that its weaker preconditions do not admit counterexamples and that its effect/reconstruction obligations still hold. When those obligations are missing the relation is unresolved rather than promoted.

Representation lift **and** project require a valid reconstruction/transport map. `representation_lift` and `representation_project` return `SUPPORTED`, `OBSTRUCTION` or `UNRESOLVED`; a representation change cannot close the original target merely because the transformed problem was solved.

## Core propositions and executable countermodels

The P6 extension freezes the following bounded propositions:

1. **Surface equivalence is insufficient.** Identical-looking action structure can have incompatible preconditions/invariants.
2. **Finite-panel effect coincidence is insufficient.** One-panel agreement remains `UNRESOLVED`.
3. **Erasure can be unsound.** Erasing a load-bearing coordinate without preservation evidence cannot support the signature; counterevidence yields `OBSTRUCTION`.
4. **Faithful substitution is conditional.** Same-signature supported membership plus interface/invariant/effect/reconstruction/authority preservation is required.
5. **Composition closure is conditional.** Individually admissible parts can collide, invalidate preconditions, add dependencies/authority footprint or recurse without a decreasing rank.
6. **Generalization/specialization is not equivalence.** Direction and obligations are explicit and the preorder carries no membership authority.
7. **UNKNOWN remains first-class.** Missing preserved coordinates, membership evidence, recursive well-foundedness, substitution evidence or reconstruction evidence remains `UNRESOLVED`; downstream P4/P8 may map unresolved scientific authority to `CANNOT_CHECK`.

`MethodFibreBench.v1` freezes twelve synthetic countermodels/no-alarm cases spanning false fibres, one-panel coincidence, missing reconstruction evidence, faithful membership, composition collisions/precondition loss/authority escalation/recursion, clean composition, specialization and invalid representation lift. The typed calculus matches all twelve frozen outcomes. The terminal remains deliberately `P6_METHOD_FIBRE_FORMALISM_NARROWED`: this finite suite supports the semantics and their non-vacuity, not general cross-domain equivalence or empirical superiority.

## Ownership boundary and explicit nonclaims

P6 owns claim-relative formal structural reduction, signature/fibre membership semantics, substitution/composition obligations and the bounded structural preorder.

P6 explicitly does **not** claim:

- that P3 can extract these coordinates accurately from arbitrary papers;
- that P2 can retrieve useful distant donors;
- that P9's learned latent space recovers formal fibres;
- that P10 can invent new fibres or methods;
- that generic category, graph, action-model, simulation/bisimulation or refinement machinery is novel merely because ORION uses it.

P9 may learn distributions over P6 objects and predict likely neighborhoods, but model confidence cannot declare fibre membership or rewrite evidence. P10 may propose new/generalized/composed methods, but each proposal must obtain a fresh P6 reduction/signature and then flow to P4/P8 for scientific authority. Donor mechanisms remain subject to #318 assimilation and #287 novelty authority before any novelty claim.

## Frozen-package boundary

The peer-review P6 V2.1 candidate under `papers/candidates/paper-06-formal-epistemic-structures-and-mechanics/` is content-bound historical authority. PR #436 demonstrated that inserting successor files into that directory correctly trips the candidate-content binding guard. Therefore this extension is maintained under `research/extensions/p6-method-fibres/` and is the successor manuscript surface; the frozen V2.1 bytes are not silently rewritten.
