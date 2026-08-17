# Local Closure Report — V2 Adoption Freeze

This wave closes the **locally solvable** tasks added to issues #97–#102 after PR #149.

## Closed locally

- adoption disposition recorded for P1–P5;
- parent-domain nearest-work contraction recorded;
- five immutable incremental protocol designs created;
- V1-vs-V2 primary hypotheses frozen;
- practical margins and non-compensatory safety guards frozen;
- negative controls, baselines, ablations, metrics, plots and tables frozen;
- exact canonical SHA-256 digest recorded for every protocol;
- execution bindings deliberately remain `UNBOUND`;
- executable decision rules return `PASS`, `FAIL`, or `CANNOT_CHECK`;
- synthetic known-answer fixtures test both practical success and safety-guard failure;
- V1 mutation, premature outcome access, fake design-as-execution freeze, P4 authority escalation and P5 self-promotion are hostile-test targets.

## Not closed locally

These require real evidence and therefore remain open in #98–#102:

- P1 live/fresh external V1/V2 comparison under bound provider/model identities;
- P2 actual complete-gold/Wide/Deep V1/V2 execution and any live-provider companion;
- P3 real multi-discipline expert/adjudicated gold;
- P4 independent protected-host hostile campaign;
- P5 real hidden-cause fresh/protected self-improvement campaign and #8/#76 dependencies;
- final result-populated manuscripts, independent reproduction, archive/DOI and journal submission gates.

No synthetic fixture in this directory carries scientific authority.

## Local hostile check before repository integration

An isolated reconstruction of the new protocol/validator layer ran:

```text
PYTHONPATH=src python -m pytest -q tests/test_paper_v2_adoption_protocols.py
13 passed
```

This validates protocol/digest/adoption consistency and known-answer decision-rule behavior only. Full repository CI is still required before merge.
