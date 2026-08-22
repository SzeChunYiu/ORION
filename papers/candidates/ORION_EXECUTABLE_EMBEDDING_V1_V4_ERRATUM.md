# P6–P8 executable embedding V1 — V4 covariance erratum

Date: 2026-08-22
Applies to: `ORION_EXECUTABLE_EMBEDDING_V1.md`
Framework: `0.3.10-shadow`
Paper sync epoch: `2026-08-22-paper-framework-harness-covariance-v4`

## Reason for reopening

The original embedding audit was frozen against `0.3.9-shadow`. The V4 paper ↔ framework ↔ harness covariance work adds two canonical substrate objects without changing the `K/W/M` coordinates or core operator set:

- `ResearchResolutionObligation.v1`
- `ResearchNegativeResult.v1`

Because the candidate checker intentionally treats a framework-version change as a reopening event, this erratum records the semantic review rather than merely changing the pinned version string.

## Effect on P6

P6's prior `PARTIAL` mapping for a universal residual-obligation registry is strengthened. ORION now has a canonical **research resolution obligation** for unresolved judgments. It carries subject identity, unresolved class, reason codes, required objects, next actions, prior attempts/blockers, bounded stop condition, and explicit non-authority ceilings.

This does **not** make P6's full mechanic calculus redundant. The new object concerns unresolved-research lifecycle; P6 composition, write/read footprints, certificate-aware reopening, chronology, and general admissibility remain distinct.

Hard obligations still may live in domain-specific objects. `ResearchResolutionObligation.v1` should not be misrepresented as a universal proof obligation calculus.

## Effect on P7

The prior audit correctly identified `CANNOT_CHECK` and resource-is-not-closure behavior. V4 makes the lifecycle explicit:

- route/task uncertainty that remains undecided is `UNRESOLVED` plus `ResearchResolutionObligation.v1`;
- a verified extension-ambiguity/non-identifiability result can be represented as `NEGATIVE` rather than being confused with missing evidence;
- an unresolved obligation cannot include task-stop authority.

This strengthens P7's fail-closed navigation embedding but does not fill the previously identified general chart/objective support-transport gap.

## Effect on P8

The new outcome objects do not widen P8 authority. Both resolution obligations and negative-result assimilation are structurally non-authorizing. In particular:

- missing authority/coercion evidence remains unresolved and routes to authority checking;
- a denied/negative authorization judgment is not softened into missing evidence;
- neither repeated resolution attempts nor a negative result can mint scientific, novelty, promotion, or global-stop authority.

## Negative-result semantics

`ResearchNegativeResult.v1` records verified negative evidence and an assimilation disposition. Examples include donor subsumption, verified obstruction, formal non-identifiability, failed frozen transfer, or an impossibility boundary.

The important covariance rule is:

```text
missing decision object  -> UNRESOLVED / resolution obligation
verified negative object -> NEGATIVE / assimilation
verified positive object -> POSITIVE under its bounded contract
```

No class may be silently coerced into another.

## Checker update

`check_orion_schema_embedding_v1.py` is updated to:

- pin `0.3.10-shadow`;
- require both V4 substrate identities;
- check their canonical dataclass fields and outcome polarity;
- confirm resolution obligations cannot self-authorize task stop and negative objects remain non-authorizing.

This remains a schema-correspondence check. It does not prove P6–P8 novelty or full semantic equivalence.
