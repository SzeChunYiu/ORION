# P7 real regime source record — 2026-08-23

This file freezes public-source facts used by the non-synthetic regime-transport study. It is evidence-source documentation, not novelty authority.

## RO-Crate 1.2 -> 1.3

Sources:

- RO-Crate 1.3 Recommendation: https://www.researchobject.org/ro-crate/specification/1.3/index.html
- 1.3 announcement / upgrade guidance: https://www.researchobject.org/ro-crate/blog/2026-06-23/announcing-ro-crate-1-3
- 1.3 changelog: https://www.researchobject.org/ro-crate/specification/1.3/appendix/changelog

Published 2026-06-22 / announced 2026-06-23. The release states that a conforming 1.2 crate can normally upgrade by updating `conformsTo` and `@context`; however, four Bioschemas terms changed canonical URI bindings in the JSON-LD context:

| term | RO-Crate 1.2 binding | RO-Crate 1.3 binding |
|---|---|---|
| `ComputationalWorkflow` | `https://bioschemas.org/ComputationalWorkflow` | `https://bioschemas.org/terms/ComputationalWorkflow` |
| `FormalParameter` | `https://bioschemas.org/FormalParameter` | `https://bioschemas.org/terms/FormalParameter` |
| `input` | `https://bioschemas.org/properties/input` | `https://bioschemas.org/terms/input` |
| `output` | `https://bioschemas.org/properties/output` | `https://bioschemas.org/terms/output` |

The announcement explicitly warns RDF consumers to handle previous URIs when reading older crates. This makes the transition useful for P7: JSON keys/value payloads can appear unchanged while canonical RDF identity changes, so value preservation alone is weaker than semantics-aware support transport.

## W3C PROV donor boundary

Sources:

- PROV-DM: https://www.w3.org/TR/prov-dm/
- PROV Constraints: https://www.w3.org/TR/prov-constraints/

PROV already owns version/aspect relations such as `specializationOf` and `alternateOf`, and provenance constraints for evolving entities. P7 does not claim generic version linking. The residual tested here is whether a declared scientific/evidence closure witness survives a representation/ontology regime change, including when a complete alias map is or is not available.

## Wine data ontology domain

Source implementation: `sklearn.datasets.load_wine()` (UCI Wine recognition dataset bundled with scikit-learn).

The original responsibility uses the three observed class identities `{0,1,2}`. The frozen coarse responsibility is `class0_vs_other`. This is a real observed dataset; P7 uses labels as evidence atoms and does not claim a new wine classifier.

The fine->coarse map is deterministic:

- `0 -> 1`;
- `1 -> 0`;
- `2 -> 0`.

The reverse map is non-injective: coarse value `0` merges fine classes `1` and `2`. Therefore a coarse evidence record alone cannot transport exact fine-class closure without an additional refinement/support witness.
