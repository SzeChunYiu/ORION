# Typed knowledge assimilation v1 — frozen design discriminator

**Status:** SOURCE_PROJECTION + FROZEN_DESIGN_DISCRIMINATOR. External disciplines inform the candidate mechanics; they do not automatically become ORION authority.

## Review lanes

- **Provenance / data integration:** preserve source entities, derivations, context and mapping lineage rather than overwriting them into one decontextualized fact.
- **Scientific information extraction:** retain qualifications and relational context around scientific claims; a sentence-level paraphrase is not a sufficient global representation.
- **Knowledge representation / entity resolution:** keep referent resolution explicit and allow unresolved/ambiguous bindings rather than silently equating mentions.
- **Verification / ORION governance:** assimilation class controls state transitions, never scientific authority. Authority still comes only from the independent verification path.

## Absorbed constraints

W3C PROV separates entities, activities and derivations and explicitly supports provenance generated under different contexts. ORION therefore stores a source projection as its own object instead of treating the integrated claim as a replacement for the source view.

Fine-grained scientific-claim extraction work such as SciClaim represents qualifications, relation types and evidence around experimental claims. ORION therefore treats context/referent information as part of the projection boundary, not disposable metadata.

Entity-resolution work distinguishes the question "do these mentions refer to the same thing?" from downstream knowledge fusion. ORION therefore uses typed `RESOLVED`, `AMBIGUOUS`, and `UNRESOLVED` referent bindings and opens a context residual when a binding is not resolved.

## Frozen v1 state-effect table

Every contribution is retained as a `SourceProjection`. The assimilation outcome then controls additional effects:

| Outcome | Integrated claim | May widen W | Required residual |
|---|---:|---:|---|
| `ALREADY_KNOWN` | no | no | none |
| `EQUIVALENT_VIEW` | no | no | none |
| `COMPLEMENTARY_FACET` | yes | yes | none |
| `REFINES_EXISTING_FACET` | yes | yes | none |
| `NEW_CONTEXT_COORDINATE` | yes | yes | none |
| `NEW_REPRESENTATION` | yes | yes | representation residual only when the mapping is incompatible/unresolved |
| `NEW_MECHANISM` | yes | yes | none |
| `CONTRADICTS_EXISTING` | yes | no | `CONTRADICTION` |
| `EXPOSES_ASSUMPTION` | yes | no | `CONTEXT_GAP` |
| `EXPOSES_SEARCH_UNIVERSE_GAP` | yes | yes | `SEARCH_COVERAGE_FAILURE` |
| `EXPOSES_METHOD_FAILURE` | yes | yes | `METHOD_GAP` |
| `UNRESOLVED` | no | no | `CONTEXT_GAP` |

This table is deliberately conservative. `ALREADY_KNOWN`, `EQUIVALENT_VIEW`, and `UNRESOLVED` cannot create another integrated claim merely because an LLM emitted a new contribution id.

## Representation / GLUE boundary

Mappings are explicit objects with source representation, target representation, relation, evidence and a recoverability flag. Relations are `EQUIVALENT`, `REFINES`, `COMPLEMENTS`, `CONTEXTUAL`, or `INCOMPATIBLE`.

A compatibility reducer returns:

- `UNMAPPED` for no mapping;
- `COMPATIBLE` when all mappings are equivalent/refinement relations;
- `PARTIAL` when at least one mapping is complementary/contextual and none is incompatible;
- `INCOMPATIBLE` when any mapping is explicitly incompatible.

Any mapping into an `orion:` representation must be recoverable to its source projection. The mapping is an alignment claim, not scientific authority.

## Global portrait discriminator

`RECONSTRUCT` must retain:

- every integrated claim id;
- verified claim ids separately;
- unresolved residual ids;
- source-projection ids;
- representation-mapping ids.

A generated summary is therefore only one view over an inspectable portrait graph; it cannot erase source projections or unresolved contradictions.

## Hostile tests frozen before implementation

1. `ALREADY_KNOWN` and `EQUIVALENT_VIEW` retain projections without duplicating integrated claims.
2. `UNRESOLVED` retains the projection, creates `CONTEXT_GAP`, and creates no integrated claim.
3. `CONTRADICTS_EXISTING` creates a source-projection claim plus a contradiction residual, without independent verification silently disappearing.
4. search-universe-gap outcomes may add candidate domains; already-known/equivalent outcomes may not.
5. ambiguous/unresolved referents open a context residual even when the high-level assimilation label is otherwise benign.
6. incompatible representation mappings open `REPRESENTATION_FAILURE`.
7. an ORION-native representation mapping that is not recoverable is rejected at construction time.
8. reconstructing the global portrait includes projection/mapping ids and preserves verified-vs-source-projection authority separation.
9. no assimilation outcome can set claim authority to VERIFIED without a verification certificate from the existing verifier.
