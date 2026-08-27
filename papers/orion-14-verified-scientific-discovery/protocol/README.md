# ORION-14 prospective authority protocol

**Protocol:** `ORION-14.protected-authority.v1`  
**Status:** `DESIGN_FROZEN`  
**Outcome access:** false

This directory turns issue #59/#101 into a prospective protected evaluation contract. The headline question is not generic factual accuracy: it is whether full ORION reduces false **scientific-authority promotion** under source/checker/evaluator attacks while retaining useful clean-case authority coverage.

`THREAT_MODEL_V1.md` freezes the attack surface, `ATTACK_CASE_SCHEMA_V1.json` freezes the case object, and `CUSTODY_POLICY_V1.md` separates candidate, evaluator/holdout and host-verifier authority.

`SCIFACT_LABEL_STATE_MAP_V1.json` (frozen 2026-08-24, before any SciFact scoring) is the only sanctioned adapter from external SciFact gold labels into ORION-14 semantic-support/terminal states, and binds Crossref/Retraction Watch to DOI-update, evaluation-epoch and revocation-conformance uses only; `check_scifact_label_state_map_v1.py` enforces it.

Final attack labels, evaluator hash, clean/hostile splits, baseline configurations and subject revision remain unbound until an independent host can make the protocol `EXECUTION_FROZEN`. A refusal-only system is not a valid win; clean-positive coverage is a safety guard.
