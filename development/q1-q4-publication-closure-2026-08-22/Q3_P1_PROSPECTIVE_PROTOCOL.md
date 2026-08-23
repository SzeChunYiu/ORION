# Q3-P1 provider-verifiable dual-instrument prospective protocol

Protocol identifier: `Q3-P1`

Protocol version: `1.0`

Instrument-generation version: `2.0` (the first Q3-P1 protocol, carrying the
post-historical successor instrument rather than revising any Q3-P1 protocol)

`EXECUTION_STATUS=NOT_STARTED`

This protocol evaluates a repaired successor instrument. The `P1` identifier is
new and does not reuse the retired contaminated historical `Q3-V2/QG-15c`
slot. It does not rescore
V0, Q3-R1, Q3-R2, contaminated slots, or historical D2/D3 receipts.

## Primary question

Does a predeclared combined model/controller system reduce deferred scientific
decision loss relative to the strongest matched comparator under
provider-verifiable and prospectively separated execution?

Agreement rate is not the primary endpoint and agreement is not assigned a
causal effect by this comparison. Improvement may arise from extraction,
controller logic, or the combination rule. False consensus remains a key
secondary risk: both instruments agree before the outcome but their shared
forecast or decision is wrong under later protected evidence. A future causal
claim about consuming agreement would require a separately randomized
agreement-use intervention.

## Eligible question universe

Before any Lane-A or Lane-B output, freeze a complete universe of unresolved
questions from at least four domains. Outcome-blind simulation must determine
the minimum independent programme clusters and questions needed for the primary
contrast and target precision; an arbitrary question count cannot unlock
superiority. Eligibility uses result-blind metadata:

- the answer is not known to either lane or the study authors at freeze;
- a protected outcome can be generated later by proof, experiment, exhaustive
  analysis, or independent adjudication;
- both instruments can operate from a bounded packet without domain-specific
  answer branches;
- the question permits at least two mutually exclusive outcome events and an
  abstention option;
- shared packet, outcome custody, and permissible tools can be hashed.

The protocol also freezes an outcome-authority hierarchy. Exact proof, complete
exhaustive analysis, physical experiment, and subjective adjudication form
separate estimand strata. For every stratum, report its own `Delta`, uncertainty,
coverage, invalidity rate, and false-consensus rate. No pooled primary estimate
is allowed unless outcome-blind weights and a heterogeneity rule are frozen
before allocation; subjective adjudication is never promoted to proof-level
authority.

Every eligible question remains in the series. Do not require disagreement or a
positive candidate outcome for inclusion.

## Measurement coordinates

Each instrument must emit separate fields:

1. **Current epistemic status:** what is established, open, or not checkable at
   freeze time. This is not scored as a forecast.
2. **Forecast event:** one member of a mutually exclusive, exhaustive event set
   defined in the question packet.
3. **Probability:** calibrated probability for every forecast event.
4. **Action:** one move from a predeclared general action ontology, plus
   `ABSTAIN` and `CANNOT_CHECK`.
5. **Expected decision value:** predicted utility or loss under the frozen
   scoring rule.

The outcome map scores only the exact forecast event and decision value. A
recommendation to retest cannot be declared false merely because a finite retest
returns a null.

## Instruments

### Lane A: provider-verifiable model instrument

- provider, model family/version, endpoint, response ID, and executor identity
  are recorded from provider-returned metadata and bound to a provider-signed or
  provider-retrievable receipt that an independent auditor can verify;
- the raw request, raw response, tool calls, tool results, timestamps, and
  termination state are content-addressed;
- any change to provider/model, endpoint, system or prompt text, sampling
  parameters, tool set, controller, ontology, extractor, combination rule, or
  execution environment creates a new instrument version;
- no outcome path or Lane-B output is readable at execution time.

If independent provider verification is unavailable, the unit is labelled
`HOST_ATTESTED_ONLY` and excluded from model-attribution estimands while
remaining a prespecified failure/abstention in the primary intention-to-treat
system comparison.

### Lane B: fixed general typed controller

One ontology, extraction schema, rule set, and action map are frozen before the
cohort. Question IDs and domain-specific answer branches are forbidden.
Independent blinded annotators extract typed state from the packet. Extraction
disagreements and `CANNOT_CHECK` are retained. The controller receives neither
Lane-A output nor protected outcome information.

Annotator labor, expertise, and latency are charged to Lane B and the combined
system. A matched all-information model baseline receives the same extracted
state, and an extraction ablation measures whether human preprocessing rather
than controller logic creates the observed difference.

The D2/D3 successor repair is bound to an exact commit and exercised by locked
tests before the cohort. A malformed successful response maps fail-closed and
cannot be silently retried under the same identity.

## Comparator arms

For every question, freeze outputs under matched context, tool, time, and cost
budgets from:

1. one Lane-A model;
2. a confirmatory homogeneous ensemble of two executions with the identical
   provider, model version, system/prompt text, tools, and sampling settings,
   differing only in independently frozen execution seeds and response IDs;
3. Lane-B controller alone;
4. Lane A plus Lane B with the predeclared combination rule;
5. independent expert review or an expert consensus baseline.
6. a matched all-information model receiving the same extracted typed state and
   charged the same extraction labor, expertise, latency, context, tools, and
   compute.

A same-family/different-version ensemble is a separately frozen secondary arm;
it is not substituted for the confirmatory homogeneous definition.

A different-provider heterogeneous two-model ensemble is mandatory as the
strongest structural alternative to the model/controller pair. Expert
comparators are disjoint from outcome adjudicators. The combination rule is
fixed before the cohort and cannot select an answer after seeing the protected
outcome.

## Primary endpoint

Before allocation, external evidence selects one
`STRONGEST_COMPARATOR_ID` from the single model, homogeneous model ensemble,
heterogeneous two-model ensemble, controller alone, and expert baseline. The
matched all-information model is also eligible. The comparator cannot be
selected from cohort outcomes. With lower loss better, the single primary
estimand is

```text
Delta = L_STRONGEST_COMPARATOR - L_COMBINED_SYSTEM.
```

It is estimated with programme-clustered uncertainty at matched budget. All
remaining contrasts use a predeclared simultaneous multiplicity procedure.

## Key secondary endpoints

- unconditional false-consensus rate over every eligible unit;
- forecast accuracy and proper scoring rule;
- calibration and abstention calibration;
- action utility and regret;
- unconditional correlated-error rate over every eligible unit;
- invalid-receipt and contamination rate;
- cost, latency, and tool use;
- performance conditional on actual disagreement, without excluding agreement
  units from the denominator.

False consensus and correlated error use the complete eligible-universe
denominator. Abstentions, invalid receipts, unauthenticated executions, and
failures receive prespecified outcome codes and cannot be dropped after freeze.
No reliability percentage is released until the predeclared independent-unit
and uncertainty requirements are met.

Before allocation, outcome-blind simulation freezes the minimum number of
independent programme clusters, smallest effect of interest, target interval
precision, task-local utilities, cross-domain standardization, invalid-unit
loss, cost accounting, and multiplicity procedure. If the cluster or precision
gate is unmet, the cohort remains a registered pilot and cannot support
superiority regardless of question count.

## Custody sequence

1. Protocol, ontology, controller, models, tools, and scoring rule freeze.
2. Complete eligible-universe and allocation digest freeze.
3. Shared packets are authored by a custodian blind to lane outputs.
4. Lane A and Lane B run under separate custodians and release simultaneously.
5. Preoutcome agreement/disagreement record freezes.
6. Protected scientific analyzer or experiment runs.
7. Blinded independent adjudication and score generation occur.
8. All valid, invalid, contaminated, abstained, and failed units are published.

Each step has a distinct Git commit, or a content hash bound to a trusted
timestamp/signature in an append-only store. The protocol commit must be a
strict ancestor of all result-bearing commits; a timestamp claim without a
verifiable content binding is insufficient.

## Release rule

Superiority requires the lower confidence bound for the frozen primary
contrast `Delta = L_comparator - L_candidate` to exceed the prespecified
smallest effect of interest, with no disqualifying
excess in invalid receipts or cost under frozen margins. A null or reversal
remains a valid result. If executor authentication, generic-controller, custody,
or exclusive-event gates fail, the affected units are retained under their
prespecified failure codes but cannot support the dual-instrument claim.
