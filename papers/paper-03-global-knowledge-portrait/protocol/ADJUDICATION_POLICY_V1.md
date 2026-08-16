# ORION-P3 adjudication policy V1

## Frozen sequence

1. Two annotators label the shared adjudication subset independently using `ANNOTATION_SCHEMA_V1.json` and the frozen handbook.
2. Agreement is computed per coordinate before adjudication. The independent labels remain immutable.
3. Disagreements are discussed using only the frozen source packet and handbook. The adjudicator records the disputed coordinate, both original labels, final label and rationale.
4. Cases requiring specialist scientific knowledge are escalated to a domain expert under the same schema. Escalation status is recorded; it is not silently treated as ordinary annotator agreement.
5. If the evidence remains insufficient, the correct gold is `UNRESOLVED`; adjudication is not required to manufacture certainty.

## Prohibited actions

- Do not inspect evaluated-system outputs before freezing the final gold for the headline test.
- Do not delete hard/disputed cases because systems perform poorly on them.
- Do not revise the handbook to fit a preferred model output after final outcome access; create a new annotation/protocol version.
- Do not collapse measurement disagreement into construct disagreement or vice versa to increase agreement.

## Domain-expert escalation triggers

Escalate when the disputed coordinate depends on specialist operationalization, instrument behavior, domain-specific ontology, nontrivial coordinate transformation, or a scientific boundary condition not recoverable from the provided source packet by a trained general annotator.

## Reporting

The publication artifact reports:

- number of independently double-annotated cases;
- per-coordinate raw agreement and a chance-corrected statistic where appropriate;
- number of adjudicated and expert-escalated cases;
- unresolved rate;
- examples of consequential disagreements;
- exact handbook/schema version and gold artifact hash.
