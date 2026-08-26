# ORION P1-P15 anomaly audit

## Audit rule

An anomaly is not automatically a software defect, nor is it automatically a
failed scientific hypothesis. It is a recorded mismatch, adverse terminal,
missing authority condition, invalid denominator, or honest boundary that can
change interpretation. The response is to preserve it, bind it to its receipt,
and run the next frozen discriminator—not to select a more favorable metric or
historical proxy.

## Mandatory retained findings

| Paper | Observation | Why it matters | Allowed interpretation | Next discriminator |
|---|---|---|---|---|
| P2 | Overall terminal is `FAIL` despite an nDCG coordinate. | The study is governed by a multi-endpoint frozen rule, not by its most favorable scalar. | Report nDCG descriptively and report the overall `FAIL` in the same view. | Execute only a newly frozen protocol that specifies all endpoints and its terminal before outcomes are seen. |
| P5 | Requested model `glm-5.2`; served model `glm-5.3`. | The executed system is not the registered requested-model condition. | Evidence may describe the served-model run under its exact identity; it cannot validate `glm-5.2`. | Obtain an identity-bound execution of the requested model, or prospectively amend and re-freeze the question as a different condition. |
| P7 | 738 cases planned; 736 observed. | The exact coverage residual is 2, so the frozen run denominator is incomplete. | Preserve the run as invalid. Do not call it a near-pass or drop two planned cases. | Explain and recover the two missing cases, then execute the complete frozen set with denominator checks. |
| P9 | Digits status is `CANNOT_CHECK`; a replay discrepancy is recorded. | Conflicting/replay evidence cannot be resolved by choosing the favorable side. | Retain both the discrepancy and `CANNOT_CHECK`. | Re-freeze exact bytes, environment, command, expected outputs, and adjudication rule; obtain a clean bound replay. |
| P10 | The prospective experiment was not executed. | Protocol text and code contain no prospective observations. | Report “not executed”; do not substitute historical results or implementation tests. | Supply all frozen inputs and execute the prospective protocol under its registered gate. |
| P11 | 30 query results; support counts `LINEAR=3`, `RBF=5`, `KNN=5`; terminal `GATE_NOT_MET`. | Available rows and nonzero counts do not imply the registered criterion passed. | Display the counts as diagnostics beside `GATE_NOT_MET`. | Run the preregistered next comparison or repair only under a newly frozen gate; do not redefine success post hoc. |
| P12 | The receipt has 32 families across sigma values 0.2, 0.4, 0.6, and 0.8; forward-time authority is `CANNOT_CHECK`; historical evidence was withheld. | Historical or in-sample evidence cannot answer a forward-time question. Withholding prevents leakage rather than creating a missing-data success. | Report the family grid descriptively, the forward-time result as unavailable, and preserve the withheld boundary. | Execute the registered forward-time split after required inputs and temporal identities are available. |
| P13 | Bounded finite five-arm/four-corruption-world evidence coexists with historical adverse evidence. | Later bounded evidence does not erase a prior adverse result, and 20 arm-world cells do not imply population-wide safety. | State both results with their exact identities and scopes. | Use a prospectively frozen transfer/expansion study whose worlds and stopping rule are fixed in advance. |
| P14 | 28 cases are internally authored; external-pilot authority is `NOT_AUTHORITY`. | Internal construction cannot supply independent external pilot authority. | Use the 28 cases as internal bounded evidence only. | Obtain an externally authored, identity-bound pilot with independent execution/adjudication. |
| P15 | Full key-set compromise recorded 0/6 signature-layer detections and is outside that layer's observational power. | A genuine-key signature can authenticate a false statement when custody is compromised; signature validity is not fact truth or scientific authority. | Report the bounded signature/tamper results and the compromise failure together. | Evaluate explicit custody/HSM/KMS and production threat-model premises; retain independent scientific admission above attestation. |

## Cross-cutting anomaly classes

### 1. Terminal-versus-coordinate conflict

P2 and P11 illustrate why a visible positive-looking coordinate must not replace
the registered vector gate. Plot terminals next to metrics and avoid winner
labels unless the receipt itself authorizes them.

### 2. Execution-identity drift

P5 is a direct requested/served mismatch. P9's replay discrepancy is a related
identity/reproduction warning. Figures must show the exact executed identity and
must not silently relabel a run as the requested object.

### 3. Denominator and coverage failure

P7's denominator residual is exact:

$$738-736=2.$$

The scientific response is invalidation and repair, not normalization to the
observed denominator unless a new protocol is frozen.

### 4. Prospective and temporal absence

P10 has no prospective execution; P12 has no authorized forward-time result.
Historical or local evidence can remain useful under its original scope but
cannot answer the missing prospective question.

### 5. Internal/external authority separation

P14's internal cases and external pilot are different evidence objects. Hashes,
clean replays, and internally independent code paths still do not manufacture an
external author.

### 6. Honest mechanism boundary

P15's full-key-compromise outcome is a load-bearing negative, not an anomaly to
clean away. It establishes the boundary of what the signature layer observes:
verification under a key does not establish custody or truth.

## Plotting safeguards

- Display exact status strings and source identifiers in tables/tooltips.
- Never impute a missing metric, uncertainty interval, authority, or denominator.
- Do not mix incompatible units in a density or aggregate score.
- Label binary status/presence heatmaps as categorical, not ordinal performance.
- Print the unfiltered anomaly count even when interactive selectors narrow the
  visible subset.
- Keep adverse/null/`CANNOT_CHECK` rows in exported figures and reports.

## Current audit conclusion

The atlas can make the framework and its bounded mechanics legible, while also
showing why several stronger conclusions are not yet authorized. The listed
findings are not repaired by visualization. They remain active interpretation
constraints until their exact next discriminators are executed and bound.
