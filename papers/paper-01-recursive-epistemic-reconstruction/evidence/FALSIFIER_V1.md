# Paper I falsifier V1

Local deterministic evidence is frozen in `research/paper-programme-v1/FLAGSHIP_FALSIFIER_RESULTS_V1.md`.

**Local status:** PASS at branch commit `8a8a7feed588363f8e2cd820d3399a33b7af3074`, CI run `31933432314`.

The suite directly exercises `ReframeOperator` and `ReopenOperator` on hidden-domain, hidden-representation, missing-evidence and execution-only worlds. It exposed and repaired an over-broad local-reframe gate: evidence/execution failures can no longer rewrite the formulation merely because responsibility is singular.

**External status:** `CANNOT_CHECK`. Paper I still requires fresh hidden-formulation cases against matched static-workflow and agent/tree-search baselines with resource and label controls.
