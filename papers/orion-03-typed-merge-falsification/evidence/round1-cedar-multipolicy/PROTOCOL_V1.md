# ORION-03 Round 1 — frozen Cedar multi-policy protocol

Protocol freeze date: 2026-08-27  
ORION event base: `27ea5e1b04dbed853b7ddba60c8bf736ef087bf5`  
Round: canonical ORION-03 breakthrough Round 1 of at most 3  
Protected Task-3 / ORION-19 paths: excluded

## 1. Scientific question

Does the typed origin/nonpromotion layer add an independently adjudicated
authorization distinction on a real permission-bearing multi-policy corpus, or
does the native policy representation already preserve every distinction that
this corpus can adjudicate?

The Cedar engine remains authoritative for Cedar syntax, validation and policy
semantics after a request and policy set have been fixed. ORION may earn a
real-domain positive only for an upstream target/source-authority distinction
that the pinned corpus itself independently labels and that the native target
representation does not already carry.

## 2. Frozen source and complete selection

Use the public official repository
`cedar-policy/cedar-integration-tests` at the GitHub-verified commit
`75989795c75d861270ce6cac38ef9d9e5b220a0c`, tree
`3aed7b26a11a3b85bd29a4b2156437be74c33333`.

The source is Apache-2.0 and carries `Copyright Cedar Contributors` in its
NOTICE. The vendored bytes are unmodified and are individually bound in
`SOURCE_BINDING_V1.json`.

Selection is the complete handwritten `tests/multi` family at that commit:

- fixtures `tests/multi/1.json` through `tests/multi/5.json`;
- policies `tests/multi/policies_1.cedar` through
  `tests/multi/policies_5.cedar`;
- every referenced entity and schema file.

No fixture, request or policy may be added or removed after execution.

The native engine is the `cedar` submodule pinned by that repository at
`bcb8bd93a292b59ae8f1dcf53b9b4176a2d3405d` (Cedar 4.1.0). The Rust runner
must execute the upstream `cedar-testing` integration-test API against all five
fixtures and therefore checks decision, reason-policy IDs, errors and schema
validation, rather than treating the public JSON labels as engine output.

## 3. Frozen systems

1. **Native Cedar.** Evaluate each official fixture with the pinned Cedar
   engine and require exact agreement with the official decision, reason and
   error fields.
2. **Flat projection.** Retain the native decision/error state while erasing
   reason-policy origin IDs. This is an origin-erased response projection, not
   a second Cedar implementation and not a superiority baseline.
3. **Typed projection.** Retain the same native decision/error state and the
   exact native reason-policy IDs as policy-level origin witnesses. Empty
   reason sets on default deny are recorded as `DEFAULT_DENY`, which is a
   decision fallback and never promoted to an evidence origin.

The comparison asks whether the official corpus contains an independently
adjudicated *upstream evidence/source licence, retraction or provenance field*.
Policy IDs in Cedar reasons are policy-level provenance and must not be
mislabeled as upstream source-authority metadata.

## 4. Frozen primary measurements

- all five native integration fixtures pass at the pinned engine commit;
- request-level native/official decision, reason and error agreement;
- typed/native and flat/native decision agreement;
- exact retention of every nonempty native reason set by the typed projection;
- presence or absence of upstream authority/origin/licence/retraction fields in
  the official fixtures;
- counts of default denies, single-reason decisions and multi-reason decisions.

No accuracy or significance claim is made from response projection alone.

## 5. Required hostile and safe controls

The independently implemented Rust adjudicator must exercise:

1. spliced foreign-origin requirements: flat positive, typed blocked;
2. retracted evidence: retraction-erased flat positive, typed blocked;
3. unsupported positive cycle: neither system may self-seed;
4. two individually valid partial sources whose union makes a stronger target:
   flat positive, typed blocked;
5. alternative complete origin: typed accepted, preventing a false alarm;
6. explicit bridge licence: typed accepted and not mislabeled splicing;
7. single-origin complete record: typed accepted;
8. multiple complete origins: typed accepted even though a mixed proof exists.

These are injected mechanism controls. They cannot satisfy the real-domain
positive terminal because the Cedar corpus does not independently adjudicate
their added provenance labels.

The already-bound `agentgateway` result
`AGENTGATEWAY_RULESETS_ORIGIN_WITNESS_SAFE` remains a required real safe
control. This round must not relabel same-field RuleSets merge, the one-token
JWT slot, or any other bound safe control as a vulnerability.

## 6. Independent-language checks

- **Rust:** the upstream Cedar Rust engine adjudicates all five fixtures; a
  separate Rust origin-witness implementation checks all eight hostile/safe
  controls.
- **Lean:** a pure Lean 4 file proves typed construction implies flat
  construction, exhibits a flat-but-not-typed two-origin witness, proves an
  alternative complete origin is accepted, and proves an unsupported two-node
  cycle remains empty in the frozen positive closure.
- **Python:** source binding, corpus census, result assembly and cross-language
  receipt equality only. Python is not the native Cedar authority.

## 7. Terminal precedence

Evaluate in this order:

1. Source binding failure, native Cedar mismatch, Rust/Lean failure, or missing
   durable cross-language receipt:
   `CANNOT_CHECK_INDEPENDENT_DOMAIN_ADJUDICATION`.
2. A corpus-labelled upstream source-authority error that flat construction
   promotes, typed construction blocks for the registered reason, and native
   target semantics do not already distinguish:
   `D_R11_REAL_AUTHORITY_PROMOTION_ERROR_PREVENTED`.
3. The corpus contains the required upstream authority semantics and the native
   representation already distinguishes every tested case:
   `D_R11_NATIVE_VERIFIER_ALREADY_SUBSUMES_RESIDUAL`.
4. The corpus supplies native multi-policy decisions/reasons but no upstream
   source-authority/licence/retraction semantics needed to adjudicate the
   residual:
   `D_R11_POLICY_REQUIRES_RICHER_SEMANTICS`.
5. Otherwise, if typed and untyped construction are extensionally equal on the
   fully adjudicated scope:
   `D_R11_TYPED_UNTYPED_EQUIVALENT`.

Hostile injected controls alone can never trigger terminal 2.

## 8. Prospectivity and authority boundary

This protocol and its executables are committed before the ORION transformation
and cross-language execution. The official fixtures are public and their
expected labels were visible during source binding, so this is not a blinded or
externally independent study. A null/adverse result is still retained, but a
positive real-domain claim requires a later untouched corpus with independent
upstream provenance adjudication.

The round grants no deployed-vulnerability, whole-system-security, novelty,
journal, submission or production-safety authority.
