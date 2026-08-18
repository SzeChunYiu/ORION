# P6 additive bridge — claim-relative structural signatures and method fibres

**Status:** additive successor text for #417/#419. The current P6 V2.1 manuscript, formal core, PDF, content manifest and peer-review terminal remain historical authority and are not rewritten by this extension.

## Concrete realizations and structural reduction

P6 treats a concrete method as an upstream reconstruction rather than redefining P1. Its adapter retains preconditions, actions, dependency graph, invariants, effects, termination, reconstruction, failure semantics and lineage, including explicit unknown coordinates. A structural reduction is always **claim-relative**: `π_C` names the declared claim/purpose `C`, the coordinates preserved, erased or unresolved, the load-bearing coordinates, preservation obligations and an explicit justification for every erasure. There is no universal context-free object called “the structure of the method.”

`StructuralSignature.v1` is content-bound to the concrete realization and reduction. If a preserved coordinate is unknown, the signature is `UNRESOLVED`. If a load-bearing erased coordinate lacks preservation evidence, the signature remains `UNRESOLVED`; evidence that the erasure is unsound yields `OBSTRUCTION`. A signature grants neither transfer nor novelty authority.

## Claim-relative method fibres

`MethodFibre.v1` denotes realizations admitted under one supported signature and declared claim. Membership requires evidence for compatible assumptions, invariants, effects, reconstruction and provenance. Coinciding effects on one finite panel are explicitly insufficient and remain `UNRESOLVED`. The fibre retains realization/evidence lineage; collapsing members into an anonymous learned cluster is outside P6 authority.

A useful cross-domain interpretation is therefore conditional: two superficially different procedures may share a fibre when their declared preconditions, protected invariants, effect and reconstruction obligations agree for the claim even if their internal action names differ. Conversely, two procedures with the same action graph or vocabulary may be a false fibre if one requires an assumption the other does not satisfy.

## Faithful substitution and composition

Substitution is justified only between supported members of the same claim-relative signature. Composition closure is conditional, not automatic. The executable contract checks sequential/conditional precondition preservation, parallel read/write collisions, hidden dependencies, authority escalation and recursive well-foundedness. A composition that creates a new dependency or authority footprint is not licensed merely because each component was individually admissible.

Generalization and specialization are directional relations, not aliases for equivalence. A representation lift cannot close the original problem without a valid reconstruction map.

## Bounded countermodel discriminator

`MethodFibreBench.v1` freezes twelve synthetic cases spanning false fibres, one-panel coincidence, missing reconstruction evidence, faithful membership, composition collisions/precondition loss/authority escalation/recursion, clean composition, specialization and invalid representation lift. The typed calculus matches all twelve frozen outcomes, including all false-fibre and clean no-alarm cases. The terminal is deliberately `P6_METHOD_FIBRE_FORMALISM_NARROWED`: this finite suite supports the semantics and their non-vacuity, but it does not establish general cross-domain equivalence, expert projection reliability, or superiority to the strongest external formal alternative.

## Ownership boundary for P9/P10

P9 may learn over P6 signatures/fibres and may predict likely membership or useful neighborhoods, but learned similarity is not formal membership and cannot rewrite P6 evidence. P10 may propose new/generalized/composed methods, but those proposals must obtain a fresh P6 signature/reduction and then flow to P4/P8 for scientific authority. P6 does not claim that P9 recovers its fibres or that P10 invents new ones.
