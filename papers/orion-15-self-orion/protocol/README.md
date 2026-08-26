# ORION-P5 prospective self-improvement protocol

## V1 — hidden-cause fresh transfer

**Protocol:** `P5.hidden-cause-fresh-transfer.v1`  
**Status:** `DESIGN_FROZEN`  
**Outcome access:** false

Paper V requires more than a visible benchmark gain. The V1 design freezes hidden-cause development families, replay/fresh separation, protected evaluator custody, strong self-improvement baselines, governance ablations and harmful-transfer reporting before final outcomes exist.

The primary scientific target is **protected fresh-task improvement with a harmful-transfer safety guard**. Replay success alone is insufficient. A candidate that changes the evaluator, reads the holdout, erases negative history or self-certifies promotion cannot count as improved merely because a visible score rises.

PAST-Bench is reference-pinned to `Gen-Verse/PAST-Bench@f8223517ae7491e776b69793d9f11e9d074ab42e`. Final hidden-cause cases, replay/fresh splits, evaluator and subject revision remain unbound until the independent protected host can mark the protocol `EXECUTION_FROZEN`.

## V2 — staged acceptance

**Protocol:** `P5.hidden-cause-staged-acceptance.v2`  
**Status:** `DESIGN_FROZEN`  
**Outcome access:** false  
**Parent:** V1, which remains unchanged.

V2 prospectively tests whether the additive `STATIC -> REPLAY -> FRESH -> PROTECTED` non-compensatory gate reduces harmful fresh transfer and false protected acceptance without sacrificing useful protected improvement beyond the frozen non-inferiority margin.

PACE-style anytime-valid commit acceptance, SEA-style certificates and Verifier-as-Gatekeeper are nearest-work/baseline pressure, not standalone P5 novelty. See `PROTOCOL_V2.json` and `STAGED_ACCEPTANCE_POLICY_V2.md`.

V2 execution identities are intentionally `UNBOUND`. Local gate tests and a design freeze do not create an external empirical result.

## V2 execution/evidence binding

Before any V2 outcome access, the protected host must create a fully bound `orion.p5.staged-acceptance-run-manifest.v2`. `P5_RUN_MANIFEST_V2_SCHEMA.json` documents the machine-readable shape and `orion.study.p5.v2_evidence.validate_run_manifest` enforces the protocol digest, exact subject/splits, five seeds, all required study arms, PACE config/error budget, matched resource caps and independent candidate/evaluator/host custody.

Stage observations and candidate decisions are archived under `P5_RESULT_ARCHIVE_V2_SCHEMA.json`. Finalization fails closed on binding mismatches, missing arm×episode×seed coverage, V2 decisions inconsistent with the non-compensatory gate, or an accepted candidate without independent FRESH and PROTECTED audit. Comparator false acceptance remains measurable evidence rather than being discarded as invalid.

See `V2_EVIDENCE_HANDOFF.md`. Passing the validator establishes artifact integrity only; it still reports empirical authority as `CANNOT_CHECK` until the external study exists.

## Causal-repair V2 — intervention-backed diagnosis plus protected fresh transfer

**Protocol:** `P5.causal-repair.v2`  
**Status:** `DESIGN_FROZEN`  
**Outcome access:** false  
**Parent:** staged-acceptance V2, which remains unchanged.

Issue #282 freezes the three GLM-5.2 adjacent-level attribution errors (`P5-HC-002`, `P5-HC-012`, `P5-HC-018`) as discriminator seeds, then requires `STATIC -> DIAGNOSE -> DISCRIMINATE -> CANDIDATE -> REPLAY -> FRESH -> PROTECTED`. Replay gain cannot compensate fresh harm. Missing fresh transfer is `BLOCK`. The only positive terminal remains host-only `RECOMMEND_HOST_PROMOTION`.

See `PROTOCOL_CAUSAL_REPAIR_V2.json`, `CAUSAL_REPAIR_POLICY_V2.md`, and `P5_CAUSAL_DISCRIMINATORS_V1.json`. Attribution replay of the archived 21/24 result is diagnosis-only and does not close the issue.
