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
