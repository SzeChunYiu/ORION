# ORION-P1 prospective external protocol

**Protocol:** `P1.hidden-formulation.v1`  
**Status:** `DESIGN_FROZEN`  
**Outcome access:** false

This directory freezes the scientific design for the external Paper-I study before final outcomes exist. The protocol binds the primary/secondary hypotheses, task families, strong baselines, ORION ablations, metrics, resource/exclusion rules, statistical analysis and figure/table definitions.

It does **not** yet bind the final subject commit, case-set hash, baseline configuration hashes, evaluator/adjudication artifact or model/provider versions. Those must be supplied prospectively before the protocol may become `EXECUTION_FROZEN`.

`HIDDEN_SHIFT_CASE_SCHEMA_V1.json` defines the minimum case contract. Gold cause/reframe/reopen labels are protected from evaluated systems. Evidence-only and execution-only negative controls are mandatory, because a system that reframes everything is not successful.

Any change to the scientific design after final outcome access creates `v2`; this V1 remains immutable evidence.
