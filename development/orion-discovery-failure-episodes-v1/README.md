# ORION discovery/failure episode evidence substrate V1

**Stack base:** `84fa7670fb7672a556e1cd3ac046292f6fc73c27` (PR #513 head).  
**Parents:** #506 Discovery Atlas, #509 Failure Atlas, #429 historical breakthrough reconstruction, #508 failure epistemology, #500 Jump.  
**Authority:** historical/research-data representation only. These records do not establish causal histories, benchmark gold, scientific novelty, or Jump capability.

## 1. Problem

ORION wants to learn candidate discovery/failure mechanics from mathematical, scientific, engineering, and everyday episodes. Historical narratives are dangerous supervision because later knowledge makes earlier choices look inevitable and retrospective stories routinely infer private cognition that is not documented.

The framework therefore needs to distinguish:

```text
DOCUMENTED AT/BEFORE CUTOFF
!= STRUCTURAL INTERPRETATION BY ORION
!= CANNOT_INFER PRIVATE/HISTORICAL STEP
!= POST-CUTOFF SUCCESSOR KNOWLEDGE
```

The first implementation goal is a source/provenance substrate that mechanically preserves those distinctions.

## 2. Source object

Candidate `EpisodeSource.v1` fields:

- source ID;
- source kind (`PRIMARY_ORIGINAL`, `CONTEMPORANEOUS_RECORD`, `ARCHIVAL_SECONDARY`, `RETROSPECTIVE_SECONDARY`, `META_ANALYSIS`, `UNKNOWN`);
- temporal relation to episode cutoff (`PRE_OR_AT_CUTOFF`, `POST_CUTOFF`);
- candidate-visible flag;
- supported fact IDs;
- optional disputed/limitation note IDs.

Load-bearing rule:

> In a pre-cutoff reconstruction packet, a `POST_CUTOFF` source can never be candidate-visible.

A source kind is not a truth score; primary sources can still be mistaken.

## 3. Fact / interpretation object

Candidate `EpisodeAssertion.v1` fields:

- assertion ID;
- field/coordinate ID;
- value/reference ID;
- epistemic role:
  - `DOCUMENTED`;
  - `STRUCTURAL_INTERPRETATION`;
  - `CANNOT_INFER`;
- supporting source IDs;
- alternative/competing interpretation IDs;
- confidence label (`HIGH`, `MEDIUM`, `LOW`, `UNRESOLVED`) as descriptive annotation only.

Rules:

- `DOCUMENTED` requires at least one supporting source;
- `STRUCTURAL_INTERPRETATION` requires source lineage when it interprets a documented event;
- `CANNOT_INFER` must not carry a claimed value as if known;
- descriptive confidence never upgrades an assertion role.

## 4. Discovery episode

Candidate `DiscoveryEpisode.v1` binds:

- episode/domain/cutoff;
- incumbent regime and target/question/function IDs;
- candidate-visible pre-cutoff source IDs;
- all source/assertion records;
- ordered documented event trace where chronology is source-grounded;
- candidate transformation hypotheses as **interpretations**, not hidden cognitive truth;
- result/new-function/proof/consequence IDs as post-event description;
- successor/correspondence/adoption IDs as post-cutoff evaluator context;
- historical-use mode:
  - `MECHANISM_EXTRACTION_ONLY`;
  - `PRE_CUTOFF_RECONSTRUCTION_DEVELOPMENT`;
- `PROTECTED_CONFIRMATORY_GOLD` is explicitly forbidden for famous/history-derived content by this V1 schema.

The record may say a transformation interpretation is plausible; it cannot claim `this is how the discoverer actually thought` unless independently documented at the appropriate granularity.

## 5. Failure episode

Candidate `FailureEpisode.v1` adds the process chronology required by #508:

```text
OCCURRED
-> BECAME_OBSERVABLE
-> DETECTED
-> RECOGNIZED_MATERIAL
-> RESPONSIBILITY_INVESTIGATED
-> NEGATIVE_KNOWLEDGE_FROZEN
-> SUCCESSOR_SEARCHED (optional)
-> SUCCESSOR_VALIDATED (optional)
```

Each observed stage is an event identity with source lineage; missing stages remain `NOT_DOCUMENTED` rather than being inferred from later history.

Also bind:

- failed target/claim/method/prototype;
- visible negative evidence;
- contemporaneous competing responsibility hypotheses;
- patches/replications/retries;
- failure visibility/publication/retraction state;
- successor/no-successor state;
- pointer to any later `FailureKnowledge.v1` only after scoped negative knowledge is separately evaluated.

A final `FAIL` terminal is not enough to synthesize the chronology.

## 6. Pre-cutoff candidate packet

Provide a deterministic projection that strips:

- post-cutoff sources;
- post-cutoff assertions;
- successor/result identities that reveal later outcome;
- ORION structural interpretations marked evaluator-only;
- private/non-documented cognition placeholders.

The candidate packet must retain the cutoff, public/incumbent state, and allowed source evidence.

## 7. RED-first requirements

Tests must require:

1. post-cutoff source cannot be candidate-visible;
2. documented assertion requires a supporting source;
3. assertion cannot cite unknown source IDs;
4. `CANNOT_INFER` cannot carry a positive historical value;
5. source/assertion digests are canonical under set-like ordering;
6. event traces preserve chronology;
7. discovery episode cannot use historical material as `PROTECTED_CONFIRMATORY_GOLD`;
8. candidate packet contains no post-cutoff source/assertion/successor identity;
9. structural interpretations can be evaluator-side while documented source events remain candidate-visible;
10. failure chronology cannot reorder fixed stages;
11. later failure stage does not imply missing earlier stage identities;
12. failure visibility (`PUBLISHED_NULL`, `FILE_DRAWER`, `RETRACTED`, etc.) remains distinct from whether failure is scientifically valid;
13. a failure episode cannot manufacture `FailureKnowledge` exclusions by itself;
14. all objects remain non-authorizing.

## 8. Scientific boundary

This tranche does not populate the 50+/100+ atlases and does not infer historical cognition. It provides the versioned bytes needed so future atlas work can be audited and later used by P9/P10 without pseudo-gold.

Implementation-only terminal:

`DISCOVERY_FAILURE_EPISODE_EVIDENCE_SUBSTRATE_IMPLEMENTED`.
