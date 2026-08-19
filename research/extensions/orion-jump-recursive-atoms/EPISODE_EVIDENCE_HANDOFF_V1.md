# Discovery / failure episode evidence handoff V1

**Status:** additive research-data substrate stacked on PR #513. No historical causal claim, Jump result, or failure-learning value is established.

## Why this exists

#506/#509 need real historical and practical episodes to derive candidate discovery/failure morphology. Those episodes cannot become pseudo-gold merely because a retrospective narrative sounds plausible.

The V1 substrate therefore represents four states explicitly:

```text
DOCUMENTED
STRUCTURAL_INTERPRETATION
CANNOT_INFER
POST_CUTOFF / EVALUATOR_ONLY
```

A source may be primary yet wrong; `PRIMARY_ORIGINAL` is provenance, not a truth terminal.

## Objects

### `EpisodeSource.v1`

Binds source kind, relation to historical cutoff, candidate visibility, supported fact/event IDs, and limitations. A post-cutoff source is mechanically forbidden from candidate visibility.

### `EpisodeAssertion.v1`

Binds a coordinate/value with role, source lineage, competing interpretations, descriptive confidence, and evaluator-only state.

- `DOCUMENTED` requires source support;
- `STRUCTURAL_INTERPRETATION` is explicitly an ORION/reviewer interpretation, not hidden historical cognition;
- `CANNOT_INFER` cannot carry a positive value.

### `DiscoveryEpisode.v1`

Binds domain/cutoff/incumbent regime, target contracts, source/assertion set, ordered documented event trace, transformation interpretations, later results and successor context. Historical use is limited to:

- mechanism extraction;
- pre-cutoff reconstruction development.

V1 rejects `PROTECTED_CONFIRMATORY_GOLD` for historical material.

### `PreCutoffDiscoveryCandidatePacket.v1`

Deterministic projection retains only:

- candidate-visible `PRE_OR_AT_CUTOFF` sources;
- documented assertions depending only on retained sources;
- the subsequence of documented events explicitly supported by retained pre-cutoff sources.

It strips evaluator-only structural interpretations, post-cutoff sources, successor IDs, later result IDs and unsupported later event chronology.

### `FailureEpisode.v1`

Separates failure-process evidence from `FailureKnowledge.v1`. It binds the ordered attempted trace, visible negative evidence, contemporaneous competing responsibility hypotheses, retries/patches/replications, visibility/publication state, and sparse observed chronology over:

```text
OCCURRED
BECAME_OBSERVABLE
DETECTED
RECOGNIZED_MATERIAL
RESPONSIBILITY_INVESTIGATED
NEGATIVE_KNOWLEDGE_FROZEN
SUCCESSOR_SEARCHED
SUCCESSOR_VALIDATED
```

A later observed stage does **not** cause missing earlier stages to be inferred. Visibility (`PUBLISHED_NULL`, `FILE_DRAWER`, `RETRACTED`, etc.) is separate from scientific validity/refutation.

`FailureEpisode.v1` never emits scoped exclusions. Only an independently evaluated `FailureKnowledge.v1` may later do so.

## Cross-programme use

- **#506 Discovery Atlas:** episodes can support morphology/atom hypotheses, with interpretation uncertainty preserved.
- **#509 Failure Atlas:** process chronology and visibility can be annotated without inventing recognition/onset dates.
- **#429 P10 historical reconstruction:** pre-cutoff packets can be generated without post-cutoff successor leakage. This does not solve broader corpus/citation leakage by itself.
- **P9:** may consume episode records only after train/evaluation exclusions and schema authority are frozen; structural interpretations must not be silently treated as labels.
- **#508:** failure episodes are events/process evidence; scientific negative knowledge remains separately scoped and authority-bound.
- **#500/#501:** historical episodes derive candidate move classes only. Contamination-safe invented worlds remain the confirmatory route for Jump claims.

## Key hostile properties

- post-cutoff sources cannot be candidate visible;
- source-set/assertion-set fields canonicalize, but event/attempt traces preserve order;
- `CANNOT_INFER` cannot be filled with a guessed historical thought;
- famous historical content cannot become protected confirmatory gold under V1;
- pre-cutoff packet physically strips later result/successor/interpretation bytes;
- later failure recognition never manufactures undocumented onset/observability stages;
- publication/retraction state cannot self-authorize scientific refutation.

## Scientific boundary

Implementation-only terminal if exact-head tests pass:

`DISCOVERY_FAILURE_EPISODE_EVIDENCE_SUBSTRATE_IMPLEMENTED`.

This allows the atlas work to begin with auditable records. It does not mean the atlas is populated, the episode interpretations are correct, or a common discovery/failure morphology has survived.