# P5 V2 execution/evidence handoff

**Protocol:** `P5.hidden-cause-staged-acceptance.v2`  
**Authority:** artifact-integrity handoff only; empirical status remains `CANNOT_CHECK`.

## 1. Freeze the run manifest before outcome access

Construct one `orion.p5.staged-acceptance-run-manifest.v2` object and validate it with `orion.study.p5.v2_evidence.validate_run_manifest`.

The manifest must content-bind:

- the exact V2 protocol digest and final 40-character subject revision;
- the hidden-cause suite plus motivating, replay, fresh and protected split hashes;
- the exact five stochastic seeds;
- provider/model revisions;
- every required V2 subject, baseline and ablation configuration;
- evaluator artifact + epoch and independent candidate/evaluator/host custody lineages;
- PACE/e-process rule, configuration hash and fixed error budget;
- matched maximum candidate/model/tool/time/evaluator budgets;
- access-policy and initial negative-history roots.

Any `UNBOUND` value fails. Mandatory V1/PACE/greedy/direct-self-edit/evaluator-only baselines cannot be deferred as non-executable. SEA/VaG-like arms may be marked `NOT_EXECUTABLE_WITH_JUSTIFICATION` only with a content-bound justification; all registered ablations must execute.

The manifest digest becomes the identity every result/decision record cites.

## 2. Archive raw stage evidence and decisions separately

Each `orion.p5.staged-result-record.v2` binds one candidate/stage observation to the exact run manifest, subject, evaluator and epoch. Preserve the raw artifact hash, negative-history digest and a non-negative per-candidate `sequence_index`.

Candidate decisions are separate records with `decision_sequence_index` and a `decision_artifact_hash` recomputed from the exact decision fields. This separation is intentional: a comparator may accept a candidate that the protected evaluator later fails. That is a measurable false acceptance, not malformed data.

For full Self-ORION V2, the archived decision must agree with the merged non-compensatory gate:

- known harm/FAIL -> `REJECT`;
- else known `CANNOT_CHECK` -> `CANNOT_CHECK`;
- else missing stage -> no final decision / `IN_PROGRESS`;
- all four PASS -> `ACCEPT` as a host-promotion recommendation only.

A V2 `ACCEPT` additionally requires the frozen chronology `STATIC < REPLAY < FRESH < PROTECTED < decision`. Rejected/blocked hostile evidence may arrive out of normal stage order; known late harm still vetoes rather than being hidden behind a missing earlier stage.

## 3. Finalization is fail-closed

A finalized `orion.p5.staged-result-archive.v2` must:

- contain a decision for every retained candidate and no decision without stage evidence;
- cover every executable arm × frozen episode × frozen seed at least once;
- retain FRESH and PROTECTED evaluation for every candidate an arm accepted;
- bind the final negative-history root;
- retain harmful, null, rejected and `CANNOT_CHECK` candidates rather than filtering them from the archive.

`validate_result_archive(...)` re-derives V2 candidate verdicts and reports integrity blockers plus raw counts for harmful fresh transfer and false acceptance. `result_archive_digest(...)` returns a stable content address only for a structurally valid archive. The validator deliberately returns `empirical_authority: CANNOT_CHECK`; statistical/scientific interpretation belongs to the separately frozen analysis layer and protected evidence, not to the validator.

## 4. Publication boundary

Passing this validator means the execution/evidence artifact is structurally bound. It does **not** mean V2 outperforms V1, PACE or any baseline. #8/#76, real external runs, matched analyses, harmful-tail reporting and the journal-readiness terminal remain open.
