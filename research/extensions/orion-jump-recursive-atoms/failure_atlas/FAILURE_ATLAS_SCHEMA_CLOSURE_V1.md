# Failure atlas schema closure V1

Date: 2026-08-19  
Issue: #509  
Feeds: #508  
Dependencies: #513 / #514

## Bounded candidate terminal

`FAILURE_ATLAS_SCHEMA_STABLE`

The stronger terminal `FAILURE_MORPHOLOGY_CORPUS_READY` is **not earned**. The pilot has no independent domain-expert annotation agreement, and this branch deliberately contains no mechanism by which a session can self-issue that evidence.

This is therefore a schema/corpus-engineering result, not a claim that the historical failure morphology is scientifically saturated or validated by external reviewers.

---

## 1. Frozen 30-episode pilot

The pilot was frozen before the executable closure checker and spans five domains:

| domain | count |
| --- | ---: |
| science / measurement | 8 |
| clinical / biomedical | 6 |
| mathematics / formal | 6 |
| engineering / safety | 6 |
| AI / autonomous science | 4 |
| **total** | **30** |

Every row contains at least two source records and at least two explicit alternative interpretations. Private cognition is always `CANNOT_INFER`, historical use is always `MECHANISM_EXTRACTION_ONLY`, and protected confirmatory-gold use is always false.

Two evaluator-side post-cutoff examples are intentionally explicit rather than silently backfilled into history:

- the 2025 GFAJ-1 retraction is post-cutoff for the 2012 replay;
- the 1967 equal-sums follow-up is post-cutoff for the 1966 Lander–Parkin episode.

The atlas is therefore compatible with #514's central separation:

`DOCUMENTED != STRUCTURAL_INTERPRETATION != CANNOT_INFER != POST_CUTOFF`.

---

## 2. Why a binary FAIL field is insufficient

The pilot contains materially different negative-evidence relations.

### Null/non-identifying result

Michelson–Morley is represented as a scoped negative on the registered expected interferometric signal, not as an automatic global disproof of every ether formulation.

### Measurement/instrument anomaly

OPERA's early-arrival anomaly is stored separately from the timing-system responsibility that later invalidated the superluminal inference.

### Foreground/model inadequacy

BICEP2 preserves the measured B-mode signal while revising the primordial interpretation after dust/foreground evidence.

### Non-replication / provenance failure

Cold fusion, high-dilution basophil degranulation, GFAJ-1 and STAP share a broad `replication/validation failure` surface label while their responsibility structures differ: calorimetry/protocol uncertainty, assay reproducibility, chemical assignment/trace phosphate, and cell-line provenance/contamination respectively.

### Harm despite a favorable surrogate

CAST and ILLUMINATE both preserve the fact that an intermediate biomarker moved in the intended direction while the registered clinical strategy caused worse hard outcomes. This blocks the shortcut `surrogate success => clinical value` without erasing the true surrogate observation.

### Exact formal refutation

Euler/Pólya/Mertens/Borsuk/Hedetniemi cases demonstrate when `DECISIVE_FOR_REGISTERED_CLAIM` is legitimate: a rigorous counterexample/disproof targets the exact quantified conjecture.

### Failed proof with preserved success

Heawood's diagnosis of Kempe is deliberately different. The proof fails, but the four-colour theorem remains logically live and a five-colour result survives. `failed proof != theorem false` is a first-class atlas invariant.

### Multi-factor engineering causation

Tacoma, Comet, Challenger, Ariane 501, Mars Climate Orbiter and Therac-25 cannot share a single reusable `root cause` coordinate. The atlas retains distinct physical, software, interface, context-transport, precursor-recognition and organizational/validation responsibility hypotheses.

### Process/scientific evaluator mismatch

The AI rows preserve the distinction between final-output/program success and scientific validity. Process, source, protocol, domain and verifier failures can be separately material.

---

## 3. Eight paired-case obligations

The manifest freezes eight cross-case discriminators:

1. same unexpected physical signal, different responsibility;
2. favorable surrogate, harmful clinical endpoint;
3. negative clinical endpoint, different inference scope;
4. exact formal refutation versus failed proof;
5. engineering failure, distinct causal chain;
6. replication failure, distinct responsibility;
7. precursor observed but not converted into blocking knowledge;
8. final/program AI success versus scientific validity.

The closure checker verifies the required episode membership and, where registered, distinct responsibility signatures, preserved successes, still-live alternatives, or the exact precursor-detection state.

---

## 4. Revision-aware schema

`FailureAtlasSchema.v1` separates:

- `first_negative_outcome_class` from `first_negative_decisive_status`;
- `materiality_class` from `responsibility_resolution_class`;
- excluded scope from still-live alternatives;
- preserved success from the negative lesson;
- response action from successor transition;
- exact retry from changed-context patch/replication;
- visibility/publication status from scientific truth;
- pre-cutoff source use from evaluator-only post-cutoff knowledge;
- atlas interpretation from #513 scientific/refutation authority.

A decisive negative must name the exact excluded scope. Nondecisive or responsibility-unresolved evidence cannot manufacture a global prohibition.

The schema maps directly onto #514 `FailureEpisode.v1` concepts for identity/domain/cutoff, sources, regime, attempts, visible negative evidence, responsibility hypotheses, retry/patch/replication records, visibility and successor state. Atlas-only fields add materiality/responsibility/scope/pair/reviewer interpretations rather than replacing the episode evidence type.

---

## 5. Pilot normalization is not hidden schema drift

Annotation exposed a few wording-level values that were more specific than the frozen common enum (`AUTHORITY_OR_VALIDATION_REPAIR`, `NARROW_CLAIM_OR_DOMAIN`, `OPEN_SUCCESSOR_SEARCH`, `REDESIGN_INTERFACE_OR_SYSTEM`).

`FailureAtlasNormalization.v1` explicitly maps these into existing common coordinates and records `material_schema_change = false`.

The reopen rule is strict: if a future value cannot be mapped without losing a load-bearing scientific distinction, that is **not** an alias; it is a material schema change and saturation resets.

---

## 6. Two post-schema no-material-change rounds

### Round 1 — replication / visibility / model checking

The Open Science Collaboration, Franco–Malhotra–Simonovits publication-bias study, Gelman–Meng–Stern posterior-predictive checking and the Reproducibility Project: Cancer Biology all pressure already frozen coordinates:

- replication/patch context;
- visibility/publication status;
- non-identifying negative evidence;
- responsibility uncertainty;
- still-live alternatives.

Result: `NO_MATERIAL_CHANGE`.

### Round 2 — deployment / clinical harm / industrial accident

The SEC Knight Capital order, the APPROVe rofecoxib trial and the Deepwater Horizon commission report pressure:

- execution/deployment defects;
- hard clinical harm with scoped inference;
- multi-factor technical/decision responsibility;
- response/remediation;
- successor transition.

Result: `NO_MATERIAL_CHANGE`.

No new revision-aware schema coordinate was required in either round.

---

## 7. Executable closure and hostile checks

`build_failure_atlas_closure_report()` recomputes:

- exact 30-case / 3-shard corpus;
- exact 8/6/6/6/4 domain counts;
- source identity/cutoff bookkeeping;
- enum validity after explicit normalization;
- private-cognition/historical-gold boundaries;
- all eight pair-family obligations;
- exact formal-counterexample versus failed-proof scope;
- external-review counts;
- normalization material-change state;
- two saturation rounds / seven challenge sources / zero material-change rounds.

Hostile tests require failure when:

- private cognition is invented;
- a famous case is promoted to historical protected gold;
- post-cutoff bookkeeping is removed;
- Kempe's failed proof is rewritten as a counterexample to the theorem;
- an annotation self-claims external reviewer agreement;
- a new post-schema coordinate appears.

The report grants no scientific refutation, global prohibition, historical causal truth, corpus-ready authority or issue-closure authority.

---

## 8. Independent-review gate

All 30 pilot rows currently say:

`independent_domain_expert_review_status = NOT_OBTAINED`.

That is intentional. The expert-panel roles used during construction are analytic lenses inside this research session, not independent external reviewers.

Therefore:

- `external_review_agreement_count = 0` is the expected V1 state;
- `corpus_ready_eligible = false` in the frozen pilot;
- `FAILURE_MORPHOLOGY_CORPUS_READY` remains unearned;
- a future external review must be attached as evidence and disagreements retained, not rewritten as agreement.

---

## 9. Consequence for #508

#509 now supplies a stable revision-aware annotation interface and 30-case pilot that #508 can use to design prospective failure-transfer experiments. It does **not** finish #508.

#508 still needs protected prospective tests asking whether the scoped failure knowledge:

- prevents recurrence under the same context;
- does not over-block changed contexts;
- preserves old successes;
- transports/reopens correctly across representation/interface changes;
- improves the next inquiry relative to no-memory and strong-parent controls;
- survives independent validation.

The historical atlas is mechanism extraction and benchmark design input, not confirmatory evidence for those prospective efficacy claims.

---

## 10. Bounded conclusion

The defensible result is:

> Across the frozen 30 source-grounded pilot failures and two post-schema challenge rounds, one revision-aware schema can represent materially different negative-evidence, responsibility, preservation, visibility, retry and successor relations without collapsing them into global prohibition or leaking post-cutoff hindsight.

That supports `FAILURE_ATLAS_SCHEMA_STABLE`.

It does **not** support `FAILURE_MORPHOLOGY_CORPUS_READY` until independent domain-expert agreement is actually obtained.
