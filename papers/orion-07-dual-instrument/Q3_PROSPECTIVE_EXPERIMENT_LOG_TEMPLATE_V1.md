# ORION-03 prospective frontier-instance experiment log template V1

Purpose: `nature-experiment-log`-style record for each additional ORION-03 dual-instrument benchmark instance. This template is frozen before Lane A/Lane B result entry. It must not be retroactively edited to fit an outcome.

```yaml
schema: ORIONQ.Q3ProspectiveExperimentLog.v1
experiment_id: ORION-03-<instance-id>-<YYYYMMDD>-001
paper: ORION-03-dual-instrument
status: PLANNED_UNEXECUTED
protocol: Q3_ADDITIONAL_PROSPECTIVE_INSTANCES_PROTOCOL_V1.md
publication_evidence_cut: ca7df1055a43f97eaf8d142a62011c4c261af368
frontier_question_id: <QG-7d-or-QG-15c-or-authorized-replacement>
frontier_question_text: <exact frozen question>
scientific_outcome_known_before_instrument_freeze: false
contamination_check_timestamp: <UTC ISO8601>
contamination_search_scope: <refs/branches/result prefixes checked>
contamination_result: CLEAN | CONTAMINATED | CANNOT_CHECK
lane_a_input_digest: null
lane_b_input_digest: null
lane_a_receipt_digest: null
lane_b_receipt_digest: null
lane_a_frozen_before_frontier_outcome: false
lane_b_frozen_before_frontier_outcome: false
deferred_outcome_receipt: null
independent_replay_receipt: null
final_scoring_status: NOT_SCORED
publication_authority: NONE_UNTIL_ALL_GATES_PASS
```

## 1. Frontier-question custody

- **Exact question:**
- **Why unresolved at freeze:**
- **Authority-bearing source showing unresolved state:**
- **Outcome prefixes/paths that would contaminate this instance:**
- **Branches/refs searched immediately before instrument freeze:**
- **Search result:** `CLEAN / CONTAMINATED / CANNOT_CHECK`

### Hard rule
If a result-bearing scientific outcome is already visible before *both* instrument outputs are frozen, set:

`status: CONTAMINATED__INSTANCE_INELIGIBLE_FOR_Q3_PROSPECTIVE_SERIES`

Do not run it as a prospective ORION-03 instance and do not replace the timestamp/digest after the fact. Freeze a different unresolved frontier question under a new experiment ID.

## 2. Immutable shared question packet

Record exactly what both instruments receive:
- repository ref/commit;
- question statement;
- permitted evidence sources;
- excluded outcome-bearing paths;
- resource/access budget;
- terminology/vocabulary;
- scoring coordinate definitions.

**Packet digest:**

No hidden gold/outcome may be present in this packet.

## 3. Lane A — research-harness diagnosis

- execution start/end:
- exact host/model/provider identity:
- capability receipt IDs:
- raw responsibility diagnosis:
- raw proposed next move:
- revision/abstention state:
- confidence/uncertainty if natively emitted:
- receipt digest:
- replay status:

Do not summarize away disagreement; preserve raw labels and the receipt.

## 4. Lane B — typed controller diagnosis

- execution start/end:
- exact controller code/ref:
- exact manifest digest:
- typed observations:
- responsibility state:
- candidate moves:
- revision-gate disposition:
- selected next move / abstention:
- receipt digest:
- replay status:

Manifest construction is not claimed LLM/human-free; record who/what constructed it and when relative to outcome custody.

## 5. Pre-outcome instrument comparison

This section may be completed **only after both instrument receipts are frozen but before the frontier scientific outcome is opened**.

| Coordinate | Lane A | Lane B | Relation |
|---|---|---|---|
| responsibility layer | | | AGREE / PARTIAL / DISAGREE / CANNOT_CHECK |
| next move | | | AGREE / PARTIAL / DISAGREE / CANNOT_CHECK |
| revision/abstention | | | AGREE / PARTIAL / DISAGREE / CANNOT_CHECK |

No aggregate accuracy/reliability value is computed here.

## 6. Deferred frontier outcome

Complete only when an independently produced outcome becomes authority-bearing.

- outcome source/receipt:
- outcome date:
- outcome produced by ORION-03 instruments? `NO` required for clean deferred scoring unless protocol explicitly permits otherwise:
- exact scientific disposition:
- evidence/proof boundary:
- result digest:

## 7. Frozen scoring map

Apply only the scoring rules frozen in `Q3_ADDITIONAL_PROSPECTIVE_INSTANCES_PROTOCOL_V1.md`.

- responsibility-layer alignment:
- next-move alignment:
- revision/abstention alignment:
- outcome relation:
- unresolved/ambiguous coordinates:

If the frontier outcome itself remains `CANNOT_CHECK`, preserve that; do not force a binary score.

## 8. Independent replay

- reproducer identity/context:
- exact code/ref:
- receipt set replayed:
- byte/digest equality:
- material discrepancies:
- adjudication:

## 9. Defect register

Record any D2/D3 or new instrument defect encountered:
- defect ID:
- discovered before/after instrument outputs:
- could it change a diagnosis/move?
- protocol disposition:
- repair allowed prospectively? yes/no:
- successor run needed? yes/no:

Never repair an outcome-bearing defect in place without a new protocol/experiment identity.

## 10. Final instance terminal

One of:
- `Q3_INSTANCE_PROSPECTIVE_COMPLETE__AGREEMENT_RECORDED__DEFERRED_OUTCOME_SCORED`
- `Q3_INSTANCE_PROSPECTIVE_COMPLETE__DISAGREEMENT_RECORDED__DEFERRED_OUTCOME_SCORED`
- `Q3_INSTANCE_CANNOT_CHECK__DEFERRED_OUTCOME_INSUFFICIENT`
- `Q3_INSTANCE_CONTAMINATED__OUTCOME_VISIBLE_BEFORE_INSTRUMENT_FREEZE`
- `Q3_INSTANCE_INVALID__INSTRUMENT_OR_PROTOCOL_DEFECT`

A completed instance grants **no paper-level reliability/generalization claim**. Paper-level evidence is by frontier question, and ORION-03's publication gate remains the prospectively frozen multi-instance series.

## Raw-material archive rule

Archive the exact input packet, raw receipts and replay records under an instance-specific directory. Do not overwrite earlier material; corrections create additive successor records. Any audio/images/manual notes used to construct the question packet must be retained with source provenance rather than summarized into an untraceable prompt.
