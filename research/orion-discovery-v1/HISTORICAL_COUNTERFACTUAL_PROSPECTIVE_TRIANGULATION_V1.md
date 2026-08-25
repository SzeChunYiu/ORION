# Historical–Counterfactual–Prospective Discovery Triangulation V1

**Status:** prospective protocol and formal eligibility theory.
**Parent:** #632 historical reconstruction.
**Related:** #980 discovery layer, #283 verification, #287 novelty, #669 research-machine evaluation.
**Authority:** no claim that ORION has rediscovered historical science or made a prospective discovery.

## 1. Why one discovery benchmark is insufficient

Three major evaluation modes fail in different ways.

### Historical reconstruction

Freeze evidence at a date before a known discovery and ask whether a system can produce a valid result, theory, representation, or decisive experiment.

Strengths:

- real scientific context;
- real incumbent theories and anomalies;
- genuine historical consequences;
- natural cross-domain diversity.

Main confounds:

- model weights may contain the later discovery;
- famous names, terminology, metadata, or problem signatures may leak it;
- historical evidence may be incomplete or mythologized;
- the later theory may not have been uniquely identifiable at the cutoff.

### Counterfactual/reminted discovery

Create a structurally related but materially changed world whose solution is not the famous historical answer.

Strengths:

- breaks direct memorization;
- tests mechanism and representation transfer;
- permits exact hidden truth and full negative controls;
- enables systematic changes of laws, constants, causal mechanisms, or method closures.

Main confounds:

- generated worlds may be toy-like;
- the generator may encode the intended operator;
- performance may be benchmark-specific;
- ecological realism may be weak.

### Prospective frontier escrow

Freeze the problem, methods, sources, predictions, and evaluator before a real result is known to the candidate or programme.

Strengths:

- directly tests present-day discovery;
- can support contemporary novelty;
- eliminates hindsight by chronology rather than instruction.

Main confounds:

- results are sparse and slow;
- many problems remain unresolved;
- independent custody is required;
- external experiments or proof review may be expensive or inaccessible.

No lane alone establishes a general discovery capability.

## 2. Triangulation principle

A strong discovery mechanism should survive all three tests at the exact claimed level:

\[
DiscoveryEvidence
=
Historical
\land Counterfactual
\land Prospective.
\]

This is a non-compensatory conjunction for the strongest claim, not a scalar score.

Allowed weaker terminals include:

```text
HISTORICAL_RECONSTRUCTION_ONLY
COUNTERFACTUAL_MECHANISM_TRANSFER_ONLY
PROSPECTIVE_SINGLE_DISCOVERY_ONLY
HISTORICAL_PLUS_COUNTERFACTUAL
PROSPECTIVE_WITHOUT_GENERALIZATION
TRIANGULATED_DISCOVERY_MECHANISM_SUPPORTED
MODEL_CHRONOLOGY_CANNOT_CHECK
EXTERNAL_CUSTODY_CANNOT_CHECK
```

## 3. ModelChronologyContract.v1

A source cutoff does not imply a model cutoff. Every historical candidate run must bind:

```text
contract_id
model_provider
model_name
model_revision_or_digest
pretraining_cutoff_claim
pretraining_corpus_disclosure_state
posttraining_or_finetuning_sources
retrieval_corpus_cutoff
retrieval_index_digest
system_prompt_digest
conversation_memory_state
external_tool_versions
package_and_database_snapshots
web_access_state
benchmark_exposure_audit
famous-name_and-term masking
contamination_probe_results
cache_and_embedding_state
candidate_visible_metadata
CANNOT_CHECK_fields
```

The contract has one of four states:

```text
CHRONOLOGY_COMPATIBLE
CONTAMINATION_DETECTED
CONTAMINATION_NOT_RULED_OUT
CANNOT_CHECK
```

`CONTAMINATION_NOT_RULED_OUT` is expected for many general-purpose pretrained models. Such runs remain useful for mechanism analysis but cannot by themselves establish independent historical rediscovery.

## 4. Source chronology is event-relative

A source is not simply pre- or post-publication. For each episode define a sequence of material events:

```text
problem recognised
key observation available
incumbent method failure visible
candidate representation introduced
decisive experiment designed
result privately obtained
result publicly disclosed
independent confirmation
```

A source may be legal for one reconstruction target and leakage for another. The cutoff must bind the exact event being tested.

## 5. Historical eligibility theorem

Let an episode `E` have:

- reconstructible pre-cutoff evidence `S_E`;
- model chronology contract `M_E`;
- contemporaneous action/tool set `A_E`;
- hidden consequence set `H_E`;
- equivalence relation `≈_E` over candidate frameworks;
- independent verifier `V_E`.

Define

\[
Eligible(E)
=C_S\land C_M\land C_A\land C_H\land C_{\approx}\land C_V.
\]

Where each condition asserts that the corresponding object is sufficiently specified for the claimed responsibility.

If any condition fails, the episode cannot authorize a full historical rediscovery claim. It may still authorize:

```text
MECHANISM_EXTRACTION
PARTIAL_RECONSTRUCTION
HISTORICAL_CASE_STUDY
CORRECT_UNRESOLVED
CANNOT_CHECK
```

## 6. HCP-T1 — source projection is necessary but insufficient

A pre-cutoff packet that strips every post-cutoff source prevents direct retrieval leakage from those sources. It does not rule out later knowledge encoded in model parameters, prompts, caches, tools, or benchmark construction.

Therefore:

\[
SourceChronologySafe
\not\Rightarrow
ModelChronologySafe.
\]

Both are required for the strongest historical claim.

## 7. HCP-T2 — counterfactual twin criterion

A counterfactual twin `E'` of historical episode `E` should preserve the targeted discovery structure while changing superficial and solution-bearing content.

Declare preserved coordinates `P` and reminted coordinates `R`, with `P∩R=∅`.

A valid twin must satisfy:

1. the old regime in `E'` has the same registered obstruction type;
2. the historical answer to `E` is invalid or insufficient in `E'`;
3. the desired transformation class remains capable of success;
4. a different transformation class is required in a controlled subset;
5. routine/no-jump controls remain solvable in the old closure;
6. the generator does not expose the transformation label.

A method that succeeds historically and fails on twins may be memorizing content rather than transferring discovery structure.

## 8. HCP-T3 — historical answer non-uniqueness

Let `F_E` be the set of candidate frameworks consistent with all evidence available at the cutoff. If

\[
|F_E/{\approx_E}|>1,
\]

then the historically later framework is not identified by the cutoff evidence alone.

A scientifically calibrated system should preserve plural candidates and propose a discriminator. Exact reproduction of the historical answer is not automatically superior to another member of `F_E`.

The correct terminal may be:

```text
MULTIPLE_VALID_FRAMEWORKS
CORRECT_UNRESOLVED
DECISIVE_EXPERIMENT_PROPOSED
```

## 9. Framework equivalence witness

A `DiscoveryEquivalenceWitness.v1` must bind two candidates through the responsibility being evaluated:

```text
candidate_a_id
candidate_b_id
responsibility_id
shared_prediction_ids
shared_derivation_ids
shared_intervention_ids
correspondence_map
known_divergence_ids
hidden_test_agreement
resource_relationship
equivalence_state
```

Possible states:

```text
SYNTACTIC_RENAMING
RESPONSIBILITY_EQUIVALENT
STRICTLY_STRONGER_A
STRICTLY_STRONGER_B
INCOMPARABLE
CANNOT_CHECK
```

Terminology similarity is neither necessary nor sufficient for scientific equivalence.

## 10. HCP-T4 — prospective escrow requirement

A prospective discovery result requires at least:

- problem and source identity frozen before outcome;
- candidate-visible information frozen;
- prediction/proposal timestamped before protected reveal;
- outcome controlled by a custodian not able to rewrite candidate outputs;
- evaluator and success criteria frozen;
- failed and null proposals retained;
- donor search and validity review after the output is sealed;
- no candidate access to the escrowed result.

A local hash proves what bytes existed at a time; it does not establish that the hasher lacked access to the hidden outcome.

## 11. HCP-T5 — triangulation interpretation

Let:

- `H=1` mean the mechanism succeeds on eligible historical episodes;
- `C=1` mean it succeeds on counterfactual twins and no-jump controls;
- `P=1` mean it earns at least one prospective escrowed result.

Then:

| H | C | P | Maximum interpretation |
|---:|---:|---:|---|
| 0 | 0 | 0 | no discovery evidence |
| 1 | 0 | 0 | possible reconstruction/memorization |
| 0 | 1 | 0 | benchmark mechanism value |
| 0 | 0 | 1 | prospective result without general mechanism evidence |
| 1 | 1 | 0 | transferable reconstruction; present novelty open |
| 1 | 0 | 1 | real result but historical mechanism may be content-specific |
| 0 | 1 | 1 | prospective transferable mechanism without historical coverage |
| 1 | 1 | 1 | triangulated discovery-mechanism evidence |

Even the final row does not self-authorize novelty or universal science coverage.

## 12. Historical atlas design

Do not begin with hundreds of weak episodes. The first atlas should prioritize adjudicability:

```text
12 breakthrough episodes
12 matched routine / failed / no-jump controls
4 domain strata
1 counterfactual twin per eligible breakthrough
```

Suggested strata:

1. mathematics and proof;
2. physics and symbolic law/framework formation;
3. chemistry/materials mechanism or design;
4. biology/engineering/instrument or intervention.

Every episode needs:

- primary-source lineage;
- exact event cutoff;
- documented incumbent state;
- documented failures or opportunities;
- legal contemporaneous tools;
- hidden consequences;
- alternative-framework policy;
- leakage attacks;
- domain-specific verifier;
- matched routine control.

## 13. Domain-specific limits

### Mathematics

Strongest eligibility because proofs and counterexamples can often be verified exactly. Remaining hazards include statement memorization, modern notation leakage, and enormous unconstrained search.

### Physics

Requires uncertainty, measurement interfaces, competing theories, hidden predictions, and instrument availability. A symbolic law benchmark is weaker than reconstructing a theory tied to real measurements.

### Chemistry/materials

Requires conditions, synthesis routes, measurement semantics, negative experiments, and chemical validity. Literature-only reconstruction omits tacit laboratory constraints.

### Biology/medicine

Requires cohort identity, batch effects, intervention semantics, ethics, and held-out validation. Multiple causal mechanisms may remain observationally equivalent.

### Instrument discovery

Requires a constructive interface capable of proposing and validating a measurement device or protocol. A text proposal without physical or simulated performance is not an instrument discovery.

## 14. Historical backtest scoring

Do not use exact wording overlap as the primary score. Report a vector:

\[
S=(validity,predictive\ reach,derivational\ reach,
intervention\ value,compression,discriminator\ quality,
calibration,cost,leakage).
\]

Hard failures include:

- post-cutoff leakage;
- protected-answer reconstruction from metadata;
- invalid proof or physical theory;
- unlimited hypotheses followed by retrospective selection;
- historical-name matching without hidden consequences;
- false certainty under non-identification.

## 15. Prospective frontier order

The first prospective ORION discovery campaign should use domains with exact evaluators:

1. open finite combinatorics or constructive mathematics;
2. proof-system method or representation expansion;
3. program synthesis/algorithm construction;
4. state abstraction or compiler-regime theorem;
5. symbolic physical-law world;
6. natural-science simulation;
7. external laboratory.

The progression is based on verifier quality, not on prestige. Exact domains are the place to debug proposal origin, theorem-identifying harnesses, donor subtraction, and false-invention controls before expensive natural science.

## 16. Comparison systems

At matched visible information and resource vector compare:

- raw research LLM;
- chronology-safe retrieval agent;
- reflection/self-critique;
- multi-agent debate;
- search/evolution inside the old operator grammar;
- structural ORION without generative edits;
- ORION with edit generation but without novelty/adoption governance;
- full ORION discovery cycle;
- domain-native exact systems.

A donor-complete tie is not a failed experiment. It identifies which ORION layer adds no residual.

## 17. Required artifacts

```text
HistoricalReconstructionEpisode.v2
ModelChronologyContract.v1
CounterfactualTwinContract.v1
DiscoveryEquivalenceWitness.v1
ProspectiveFrontierEscrow.v1
TriangulationResultReceipt.v1
HistoricalEligibilityLedger.v1
```

Each result receipt must keep source safety, model safety, validity, mechanism transfer, prospective authority, and novelty as separate coordinates.

## 18. Novelty boundary

Historical backtesting, time-sliced evaluation, counterfactual benchmarks, scientific forecasting, formal proof reconstruction, and prospective preregistration all have substantial prior work.

The candidate ORION contribution is the coupled authority architecture:

- source and model chronology kept separate;
- historical, counterfactual, and prospective evidence kept separate;
- alternative-framework equivalence explicitly evaluated;
- proposal origin and old-closure obstruction bound;
- theorem-identifying harness receipt required;
- validity, novelty, and adoption remain externally governed.

This is a candidate residual, not an earned novelty statement.