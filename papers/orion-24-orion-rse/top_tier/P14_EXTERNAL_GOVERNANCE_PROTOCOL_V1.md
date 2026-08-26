# ORION-24 external blinded governance protocol V1

**Programme:** #977  
**State:** `FROZEN_EXTERNAL_EXECUTION_INTERFACE`  
**Scientific state:** external agent/expert outcomes not yet executed; no top-tier promotion authority.

## Question

Holding research evidence, model/tool access and budget fixed, does ORION-RSE's scientific-promotion contract improve final scientific decisions relative to strong ordinary/reflection/multi-review/preregistration research workflows without suppressing independently judged useful discovery?

## Evaluation layers

Run two separately reported studies.

### Layer A — paired judgment intervention

For each packet, freeze one evidence-generation trace or complete evidence bundle. Every final-judgment system receives **the same evidence bytes** and the same task statement.

Compare:

1. `RAW_FINAL_JUDGMENT` — strongest ordinary research agent final decision;
2. `REFLECTION_REVIEW` — self-critique/reviewer pass;
3. `MULTI_REVIEW` — independent reviewer/debate aggregation;
4. `PREREG_CHECKLIST` — preregistration/checklist enforcement without recursive governance;
5. `ORION_RSE` — donor subtraction + protected discriminator + negative retention + authority separation + split/subsume/reopen/stop dispositions.

Layer A isolates governance from evidence-generation capability.

### Layer B — end-to-end governance

Systems may select further literature/experiments/backtracking under matched budget. This tests whether governance changes the trajectory itself. Because evidence paths differ, Layer B cannot be pooled with Layer A as if it were the same causal contrast.

## External packet families

Minimum promotion study: at least 60 blinded packets across at least three domains and all of these scientific states:

- strong supported/promotable result;
- apparent positive subsumed by nearest work/donor;
- interaction-only result;
- null result with scientifically live parent question;
- negative result that must be retained;
- leaky/corrupt benchmark yielding impossible performance;
- non-identifiable question requiring `CANNOT_CHECK`;
- regime/evidence change that reopens an earlier disposition.

### Donor sources/adapters

Use public benchmark material where licensing/format permits, without copying hidden answers into agent-visible packets:

- ReplicatorBench for replicable/non-replicable claim interpretation;
- AutoResearchBench or equivalent strong literature-discovery tasks for donor search;
- AstaBench/ResearcherBench/PaperBench-style scientific research/replication packets;
- shadow-evaluation-style unpublished/frontier questions only through original-author/expert collaboration;
- newly authored domain-expert packets to avoid benchmark overfitting.

No sibling ORION terminal/disposition may appear in an agent-visible external packet.

## Packet contract

Each packet binds:

- immutable `packet_id` and domain;
- scientific question and allowed claim language;
- visible evidence bundle identities/digests;
- allowed tools/access and total budget;
- preregistered endpoints/decision moments where applicable;
- hidden independent-gold record identity;
- adjudicator identities/roles stored separately from candidate outputs;
- leakage partition: authoring, development, protected evaluation.

Machine-readable interface: `P14_EXTERNAL_PACKET_SCHEMA_V1.json`.

## Required system output

Every system returns a structured decision record with:

- proposed final claim;
- claim width/scope coordinates;
- nearest-work/donor ownership list and residual;
- material positive/null/negative evidence retained;
- endpoint/protocol deviations detected;
- disposition: `PROMOTE`, `SUBSUMED`, `INTERACTION_ONLY`, `NEGATIVE`, `NULL_LIVE`, `NON_IDENTIFIABLE`, `CANNOT_CHECK`, `REOPEN`, `STOP`;
- confidence separated from authority;
- requested further evidence/actions;
- research cost/resource record.

Free prose may accompany the record but is not the scoring authority.

## Independent gold/adjudication

Gold must be external to the candidate workflow.

Preferred authority order:

1. deterministic verifier/known benchmark gold where scientifically faithful;
2. original paper authors/packet domain experts blinded to system identity;
3. at least two independent domain-qualified reviewers with conflict adjudication;
4. model judge only for secondary scaling after its agreement with human/expert authority is measured on the same packet family.

The candidate agent, ORION-RSE policy or this benchmark generator may not grade its own scientific correctness/novelty.

## Primary outcomes

Compute at packet level, then aggregate by domain/family rather than treating every sentence/claim atom as independent.

- `false_novelty_rate` — claims promoted as novel when hidden donor ownership subsumes them;
- `unsupported_widening_rate` — final claim exceeds independently allowed support/scope;
- `protocol_drift_rate` — post-hoc endpoint/protocol change accepted as if preregistered;
- `negative_loss_rate` — material negative/null evidence omitted or overwritten;
- `subsumption_detection_rate`;
- `cannot_check_precision/recall`;
- `reopen_accuracy` under regime/evidence change;
- `useful_discovery_recall` — fraction of independently judged useful/promotable residuals retained;
- `over_abstention_rate` — valid/promotable discoveries unnecessarily suppressed;
- evidence/reproduction completeness;
- reviewer agreement;
- resource cost.

## Co-primary promotion condition

Top-tier ORION-24 empirical promotion requires **both**:

1. material reduction in false novelty/unsupported widening relative to strongest matched comparator; and
2. useful-discovery recall no worse than a prospectively frozen non-inferiority margin.

The margin, confidence-interval method, multiplicity policy, domain weighting and missing-run policy must be frozen after pilot/development data but before protected outputs.

Blanket abstention cannot pass because it fails useful-discovery recall/over-abstention.

## Longitudinal negative-history test

A protected subset must contain at least two research rounds separated by a regime/evidence change. Compare full ORION-RSE with an ablation that does not retain negative/subsumed history.

Primary question: does retained negative history improve later experiment/claim decisions without incorrectly freezing a result whose invalidating assumptions have changed?

## Strong hostile attacks

- ORION terminology appears in packet/gold and becomes a label leak;
- ORION-24 gets stronger web/data access than comparators;
- adjudicators infer system identity from output style;
- ORION wins by `CANNOT_CHECK`/abstention everywhere;
- packet authoring encodes ORION rules rather than scientific reality;
- hidden gold is itself contestable novelty judgment with no expert authority;
- Layer A and Layer B are pooled despite different evidence paths;
- reviewer model equals candidate model without measured independence;
- domain weighting selected after outcomes;
- negative-history tasks are recycled from ORION-24's own development examples.

## Top-tier evidence threshold

The external result may support the broad ORION-24 claim only after:

- >=60 protected packets / >=3 domains;
- strong matched frontier research workflows;
- independent blinded adjudication;
- co-primary safety + useful-discovery condition passes;
- longitudinal negative-history subset closes;
- exact output/resource archive and reproducible scoring;
- immediate pre-submission literature refresh.

Until then ORION-24 retains `READY_FOR_EXTERNAL_REVIEW_AS_CONTROLLED_GOVERNANCE-CONFORMANCE_RESULT`, not `P14_TOP_TIER_SUBMISSION_READY`.
