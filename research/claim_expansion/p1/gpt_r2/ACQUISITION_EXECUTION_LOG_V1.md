# P1-U GPT-R2 acquisition execution log V1

Campaign: #711  
PR: #714

## Attempt A — invalid for case admission

After the frozen policy/evaluator workflow passed, the 28 frozen search strings in `HELDOUT_ACQUISITION_PLAN_V1.json` were issued in four multi-query web batches.

The search interface returned merged result streams rather than a separately auditable rank list for each individual query. Therefore Attempt A cannot establish the registered selection rule `first qualifying nonexcluded source in frozen ranked snapshot` on a per-query basis.

**Disposition:** `ACQUISITION_ATTEMPT_INVALID__NO_CASES_ADMITTED`.

No dossier, gold class, probe encoding, ORION outcome, B3 outcome, or case inclusion decision was created from Attempt A. The returned sources may not be used to choose later cases.

## Corrective execution rule

Re-execute each of the same 28 frozen query strings individually, verbatim, using the same search engine and qualification rules. For each query, record the returned rank order and scan downward only until the first qualifying nonexcluded primary/publisher/official source is found. The query wording, source priority, qualification rubric, corpus target, policy, evaluator, margins, and endpoints remain unchanged.

This is an execution-observability repair, not an outcome-driven protocol change. If individual-query execution cannot expose a per-query ranked result list, the campaign terminates `CANNOT_CHECK_ACQUISITION_RANKING` rather than substituting hand-picked cases.
