# #513 reviewed semantic hardening — V2 operational amendment

Date: 2026-08-19

PR review identified three fail-open edges in the original V1 substrate:

1. a `FailureKnowledge.v1` record could classify no frozen context coordinates and therefore apply its exclusions globally;
2. a simultaneous `required_same` mismatch and `reopen_on_change` change was reported as `REOPENED` instead of `NOT_APPLICABLE`;
3. a `BoundedEpistemicAtomStudy.v1` record could name the same identity as evaluator and authority owner.

The original implementations are preserved verbatim as `failure_knowledge_v1.py` and `bounded_epistemic_study_v1.py`. The public module names now expose reviewed V2 behavior while retaining the same record/report version strings for wire compatibility.

V2 rules are non-compensatory:

- frozen failure context must be non-empty;
- every frozen context key must be explicitly classified as either `required_same` or `reopen_on_change`;
- the two role sets remain disjoint;
- missing classified context => `UNRESOLVED`;
- any changed `required_same` coordinate => `NOT_APPLICABLE`, even if a reopen coordinate also changed;
- only after required-same compatibility may a changed reopen coordinate yield `REOPENED`;
- only fully compatible context may emit exclusions;
- atom-study evaluator identity must differ from scientific authority-owner identity.

This amendment changes no scientific terminal and grants no authority. It only removes fail-open applicability and self-evaluation states found during PR review.
