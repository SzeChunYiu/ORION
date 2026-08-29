# ORION-03 current-main Round-2 evidence revalidation V1

**Terminal:** `BOUNDED_R2_EVIDENCE_REMAINS_BOUND__NO_NATIVE_ENGINE_RERUN`  
**Scientific authority delta:** `NONE`

This packet answers the bounded-paper maintenance question that does **not**
require another OpenSSL campaign: do the committed Round-2 X.509 evidence and
its current publication boundary still describe the same frozen object on
current `main`?

The answer is yes, subject to the original authority ceiling.

## What is checked without the native toolchain

`check_orion03_round2_binding_v1.py` fail-closes unless all of the following
remain true:

- all **269** source-binding digests in `SOURCE_BINDING_V2.json` match current
  bytes (252 vendored certificates plus recipe/exclusion/frozen/result
  artifacts);
- the three duplicate-run receipt pairs are byte-identical;
- the frozen result still contains **1,962** tasks and **46** engine-adjudicated
  hybrids;
- family totals reconcile to those same 1,962/46 counts;
- the independent model-based reproduction still carries 46 unique hybrid task
  IDs, reproduces the flat-union 46 unsafe merges, and gives the typed witness
  zero unsafe merges;
- the independent reproduction still explicitly excludes C1--C6 and structural
  localization from its authority;
- external peer review, journal authority, and submission authority remain
  false;
- the publication freeze still says
  `CURRENT_EARNED_CEILING_FROZEN__EXTERNAL_POLICY_VALIDATION_SUCCESSOR_ONLY` and
  preserves the analytic/empirical boundary.

## What is not re-run

This is deliberately **not** a native OpenSSL 3.6.4 re-execution. The repository's
own reproduction contract says that recomputing the 1,962 task aggregates, C1,
C3, and C4 from the engine requires the pinned OpenSSL build, and that per-task
verdicts for the 46 hybrid cases are not serialized. This packet does not turn
those `CANNOT_CHECK` boundaries into passes.

The bounded paper can therefore treat the existing Round-2 object as
current-main bound evidence. A broader successor across cosign/TUF/in-toto is a
separate top-tier question and remains external work; it is not a prerequisite
for preserving the current bounded result.
