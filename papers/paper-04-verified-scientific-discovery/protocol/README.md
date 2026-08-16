# ORION-P4 prospective authority protocol

**Protocol:** `P4.protected-authority.v1`  
**Status:** `DESIGN_FROZEN`  
**Outcome access:** false

This directory turns issue #59/#101 into a prospective protected evaluation contract. The headline question is not generic factual accuracy: it is whether full ORION reduces false **scientific-authority promotion** under source/checker/evaluator attacks while retaining useful clean-case authority coverage.

`THREAT_MODEL_V1.md` freezes the attack surface, `ATTACK_CASE_SCHEMA_V1.json` freezes the case object, and `CUSTODY_POLICY_V1.md` separates candidate, evaluator/holdout and host-verifier authority.

Final attack labels, evaluator hash, clean/hostile splits, baseline configurations and subject revision remain unbound until an independent host can make the protocol `EXECUTION_FROZEN`. A refusal-only system is not a valid win; clean-positive coverage is a safety guard.
