# Failure atlas schema pilot V1 — development packet

Date: 2026-08-19

Issues: #509 feeding #508.  
Schema dependency: #514 (`FailureEpisode.v1`, source/assertion roles, pre-cutoff projection).  
Scoped-knowledge dependency: #513 (`FailureKnowledge.v1`).  
Authority boundary: this packet can establish a stable **annotation/corpus schema** from a 30-episode source-grounded pilot. It cannot self-issue independent domain-expert agreement, protected transfer efficacy, or a `FAILURE_MORPHOLOGY_CORPUS_READY` terminal.

## 1. Frozen atomic question

Can one revision-aware failure-atlas schema represent materially different failure histories across science/measurement, clinical/biomedical research, mathematics, engineering/safety, and AI/autonomous-science evaluation while preserving:

- the difference between an observed negative result and a scientifically licensed exclusion;
- plural/uncertain responsibility;
- response/patch/replication chronology;
- preserved successes;
- successor/reopening state;
- visibility/publication status;
- pre-cutoff versus post-cutoff information;
- same-symptom/different-cause matched cases;
- explicit historical-hindsight boundaries;
- a direct hook into #514 `FailureEpisode.v1` without pretending the atlas owns refutation authority?

The pre-implementation candidate terminal is:

`FAILURE_ATLAS_SCHEMA_STABLE`

`FAILURE_MORPHOLOGY_CORPUS_READY` is deliberately **not** available to this session because #509 requires inter-reviewer/domain-expert agreement on a subset and no independent domain-expert review has yet been obtained. A validator may confirm the schema-stable terminal or fall back to `FAILURE_ATLAS_NOT_STABLE / CANNOT_CHECK`; it may not upgrade the corpus to ready by self-attestation.

## 2. Expert-panel roles

The pilot is challenged through five lenses.

1. **Scientific failure / measurement expert** — separate instrument/protocol anomalies, replication failures, model inadequacy, contamination, and later reinterpretation.
2. **Clinical-trial / evidence expert** — separate surrogate failure, harm, efficacy nulls, population/context restriction, and theory-versus-intervention ambiguity.
3. **Formal-mathematical expert** — treat a valid counterexample as decisive only for the exact quantified conjecture/claim it falsifies; preserve restricted results and proof fragments where applicable.
4. **Safety / systems engineering expert** — represent multi-factor causal chains, latent precursor signals, organizational/interface contributions, and corrective redesign without collapsing them into one universal root-cause field.
5. **AI/autonomous-science evaluation expert** — distinguish process failure, scientific inconsistency, verifier failure, trajectory hallucination, and task/benchmark limitations; study-level failure taxonomies are not treated as individual-agent biographies.

No expert role in this packet substitutes for an **independent reviewer**. The implementation must expose that missing gate.

## 3. Frozen 30-episode pilot

### A. Science / measurement (8)

- `F001` Michelson–Morley (1887): small/null relative-motion signal in the registered interferometric experiment; do not rewrite the paper as a universal one-step disproof of every ether conception.
- `F002` OPERA superluminal-neutrino anomaly (2011–2012): anomalous time-of-flight result followed by identified timing-system/instrumental effects and dedicated remeasurement consistent with light speed.
- `F003` BICEP2 primordial B-mode interpretation (2014–2015): initial B-mode detection/primordial interpretation pressure followed by joint BICEP/Keck/Planck evidence showing strong dust contribution and no statistically significant tensor detection.
- `F004` Fleischmann–Pons cold fusion (1989): claimed excess heat/nuclear interpretation followed by broad replication/assessment difficulty; the atlas must distinguish failure to reproduce the claimed nuclear evidence from a global prohibition on all low-energy nuclear hypotheses.
- `F005` STAP cells (2014): published pluripotency claims, subsequent errors/retractions and evidence that alleged STAP cell lines were derived from ES cells.
- `F006` GFAJ-1 arsenic-life claim (2010–2012 cutoff): arsenic-incorporation interpretation followed by independent chemical/biological studies that did not support replacement of phosphate in DNA; the 2025 retraction is explicitly `POST_CUTOFF` for the frozen 2012 replay.
- `F007` high-dilution / “memory of water” basophil-degranulation result (1988–1993): dramatic claimed effect, Nature investigation and later independent replication failure; preserve the distinction between subjective/experimental-protocol responsibility and the exact biological claim.
- `F008` N-rays (1903–1904): reported subtle optical/radiation observations followed by R. W. Wood’s adversarial apparatus investigation showing observations persisted when a load-bearing prism was removed.

### B. Clinical / biomedical evidence (6)

- `F009` CAST (1989–1991): encainide/flecainide suppressed ventricular ectopy yet increased arrhythmic death/total mortality — a canonical same-successful-surrogate/different-clinical-outcome case.
- `F010` WHI estrogen+progestin primary-prevention trial (2002): combined therapy’s trial-wide risk/benefit profile was unfavorable in the studied population; do not promote this to an all-populations/all-regimens prohibition.
- `F011` torcetrapib ILLUMINATE (2007): HDL-raising strategy/intervention produced adverse blood-pressure/electrolyte signals and excess mortality/events despite favorable lipid changes.
- `F012` semagacestat Alzheimer trial (2013 report): gamma-secretase inhibition failed to improve cognition/function and worsened some outcomes/adverse events; intervention failure does not by itself settle every amyloid mechanism.
- `F013` solanezumab EXPEDITION3 (2018): no significant benefit on the prespecified primary cognitive outcome in mild Alzheimer disease; keep drug/target/exposure/population/theory responsibility hypotheses distinct.
- `F014` RECOVERY hydroxychloroquine (2020): no reduction in 28-day mortality in hospitalized COVID-19 patients and worse/longer hospitalization-related outcomes; the negative lesson is hospitalized-patient/regimen/context scoped.

### C. Mathematics / formal reasoning (6)

- `F015` Lander–Parkin (1966): explicit counterexample to Euler’s conjecture on sums of like powers.
- `F016` Haselgrove (1958): disproof of Pólya’s conjecture.
- `F017` Odlyzko–te Riele (1985): disproof of the Mertens conjecture without relying on finding a small explicit counterexample.
- `F018` Kahn–Kalai (1993): counterexample to Borsuk’s conjecture in sufficiently high dimensions.
- `F019` Shitov (2019): counterexamples to Hedetniemi’s conjecture.
- `F020` Heawood (1890): defect in Kempe’s accepted four-colour proof while preserving enough of the method to establish a five-colour result — a required `failed proof != no preserved success` case.

### D. Engineering / safety (6)

- `F021` Tacoma Narrows Bridge (1940/1941 report): observed oscillation precursors, attempted mitigations, catastrophic failure and post-failure aerodynamic/dynamic redesign pressure.
- `F022` de Havilland Comet fatigue failures (1954/1955 inquiry): initial operational failures, grounding/investigation and fatigue/pressurization-related redesign; causal understanding required destructive/repeated structural testing rather than one surface symptom.
- `F023` Space Shuttle Challenger / Rogers Commission (1986): O-ring/joint failure under cold conditions plus documented decision/organizational contributors; prior erosion evidence did not translate into adequate launch blocking.
- `F024` Ariane 5 Flight 501 (1996): reused inertial-reference software encountered an out-of-range conversion under a new trajectory; software that had been adequate under Ariane 4 context did not transport safely to Ariane 5.
- `F025` Mars Climate Orbiter (1999): ground-software units/interface mismatch propagated into trajectory estimation and mission loss; same broad symptom `navigation failure` has different responsibility than Ariane 501.
- `F026` Therac-25 (1985–1987 accidents; 1993 analysis): repeated radiation overdoses involving software race/state errors, weak independent interlocks, misleading messages and delayed causal recognition; later redesign added hardware/software safeguards.

### E. AI / autonomous-science evaluation (4)

- `F027` AutoResearch failure taxonomy (2026): process-level evaluation over 100 frontier research tasks; use only documented trajectory/failure categories, not invented task-agent mental states.
- `F028` DeepHallu / full-research-trajectory hallucination evaluation (2026): final outputs can look plausible while intermediate/source/reasoning trajectory failures remain hidden.
- `F029` ResearchClawBench (2026): end-to-end autonomous scientific research benchmark exposes protocol/evidence/scientific-core mismatch failure modes under expert rubrics.
- `F030` verifiable/self-correcting AI physicist / PhysVEC-style evaluation (2026): programming and scientific/domain verifiers catch different failure families; one successful program check is not scientific correctness.

Frozen domain counts: `8 / 6 / 6 / 6 / 4 = 30`.

## 4. Source floor and leakage rule

Every episode must have at least one source that directly documents the first negative evidence or formal counterexample and at least one source documenting either the initial claim/regime or the later response/successor when available. Primary publications, official accident/inquiry reports, trial publications and formal papers are preferred. Secondary narratives may be retained only as orientation and cannot establish a decisive scientific field by themselves.

For replay, every source has an event date and knowledge-cutoff relation. Later facts remain `POST_CUTOFF` and are physically excluded from any pre-cutoff candidate packet. Famous outcome identities may never become protected confirmatory Jump/failure gold.

## 5. Required atlas fields

The annotation schema must preserve a direct mapping to #514 and add only atlas-level interpretation fields:

### #514-aligned episode fields

- `episode_id`, `domain`, `knowledge_cutoff_date`;
- `source_records` with source identity/date/kind/locator/role/event order;
- `incumbent_target_id`, `incumbent_regime_id`;
- `protocol_summary`, `attempt_summary`;
- `first_negative_evidence_summary`, `first_negative_outcome_class`, `first_negative_decisive_status`;
- `failure_detection_status`;
- `responsibility_hypothesis_ids`;
- `recognition_delay_class`;
- `response_type_ids`;
- `patch_or_replication_records`;
- `successor_state_id`, `successor_transition_id`;
- `preserved_success_ids`;
- `protected_novel_consequence_ids`;
- `visibility_status`;
- `post_cutoff_source_ids`.

### #509 atlas-level interpretation fields

- `materiality_class`;
- `responsibility_resolution_class`;
- `misstep_class_ids`;
- `failure_usefulness_class`;
- `successor_transition_class`;
- `paired_case_ids` and `pair_relation_ids`;
- `alternative_interpretations` (>=2);
- `private_cognition = CANNOT_INFER`;
- `historical_use = MECHANISM_EXTRACTION_ONLY`;
- `protected_confirmatory_gold = false`;
- `independent_domain_expert_review_status`.

Atlas-level interpretation is not scientific refutation authority. A row can say `DECISIVE_FOR_REGISTERED_CLAIM` only when the cited evidence/formal relation licenses that exact scope; otherwise it must use `NONDECISIVE`, `CONTEXT_SCOPED`, `RESPONSIBILITY_UNRESOLVED`, or equivalent fail-closed state.

## 6. Frozen pair families

At least these matched pairs/sets must exist:

1. **same dramatic anomaly, different responsibility**: OPERA (`INSTRUMENT_TIMING`) vs BICEP2 (`ASTROPHYSICAL_FOREGROUND / INFERENCE`) vs N-rays (`SUBJECTIVE/PROTOCOL_OBSERVATION`) — surface `unexpected signal` is not a common causal diagnosis;
2. **successful intermediate metric, harmful/failed endpoint**: CAST vs torcetrapib — surrogate movement cannot authorize clinical value;
3. **negative clinical endpoint, different inference scope**: semagacestat vs solanezumab vs RECOVERY — intervention/context failure does not automatically refute a whole disease mechanism or unrelated treatment context;
4. **formal counterexample vs flawed proof**: Euler/Pólya/Mertens/Borsuk/Hedetniemi counterexamples can decisively refute exact universal conjectures; Kempe/Heawood shows a proof can fail while preserving reusable lemmas/structure;
5. **same broad engineering failure symptom, different causal chain**: Ariane 501 (`CONTEXT_TRANSPORT + NUMERIC_CONVERSION`) vs Mars Climate Orbiter (`UNIT/INTERFACE CONTRACT`) vs Therac-25 (`SOFTWARE STATE + INTERLOCK/PROCESS`) vs Challenger (`PHYSICAL JOINT + DECISION PROCESS`);
6. **replication failure with/without clean successor**: cold fusion/high-dilution/GFAJ/STAP distinguish failed replication, contamination, protocol dispute and successor explanation;
7. **precursor observed but not converted into blocking knowledge**: Tacoma oscillations, Challenger O-ring erosion and Therac warning/incident history;
8. **AI syntactic/program success vs scientific failure**: programming verifier pass is not a domain-scientific verifier pass.

## 7. Nearest-work subtraction

The atlas must not rename mature failure-analysis parents:

- publication bias / file-drawer work owns visibility asymmetry for null results;
- large-scale replication work owns reproducibility-rate/corpus methodology;
- posterior predictive/model criticism owns formal model-fit diagnostics;
- severe-testing/error-statistical work owns parts of probative negative evidence;
- clinical trial methodology owns endpoint/harm/context interpretation;
- formal counterexample/proof theory owns decisive mathematical refutation;
- engineering accident/inquiry and safety analysis own multi-factor incident causation;
- current scientific-agent benchmarks own process-level AI failure taxonomies.

The ORION residual is a **typed, revision-aware, pre-cutoff-safe cross-domain corpus interface** that can feed #508/#513/#514 and prospective transfer studies without turning every failure into a global prohibition.

## 8. Independent-review gate

The schema contains reviewer annotations but this session is not an independent domain expert and cannot certify inter-reviewer agreement. Therefore:

- pilot rows set `independent_domain_expert_review_status = NOT_OBTAINED` unless an actual external review is later attached;
- validator must refuse `FAILURE_MORPHOLOGY_CORPUS_READY` while any required review gate is missing;
- disagreements, if supplied later, must be stored rather than majority-voted away;
- #509 may close at `FAILURE_ATLAS_SCHEMA_STABLE` if the schema/corpus mechanics and source/hindsight gates pass, with `CORPUS_READY` explicitly deferred.

## 9. Two post-schema saturation rounds

After the schema and 30-case sample are frozen, run two primary-source rounds from different neighborhoods. A new reusable coordinate changes the schema, resets the rounds and blocks the stable terminal. Reinforcement of already registered fields is `NO_MATERIAL_CHANGE`.

## 10. Falsifiers

Return `FAILURE_ATLAS_NOT_STABLE` or `CANNOT_CHECK` if:

- fewer than 30 frozen cases or fewer than four domains survive source review;
- an episode lacks a direct source for its negative evidence/counterexample;
- any row infers private cognition;
- historical/post-cutoff gold becomes candidate-visible;
- a formal counterexample is broadened beyond its quantified claim;
- a clinical/engineering failure is promoted to an unscoped global prohibition;
- same-symptom cases are forced into one responsibility class;
- preserved successes cannot be represented;
- patched/changed-context recurrence cannot be distinguished from exact retry;
- a new reusable coordinate appears during either post-schema round;
- the implementation reports corpus-ready without independent domain-expert review.
