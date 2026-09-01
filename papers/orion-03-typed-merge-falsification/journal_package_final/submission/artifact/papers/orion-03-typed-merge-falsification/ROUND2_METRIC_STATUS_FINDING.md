# ORION-03 round 2 — which numbers are measurements and which are identities

**Status:** `PRE_SUBMISSION_REPORTING_DEFECT` · authority: reporting scope only
**scientific_authority_delta:** `NONE` — no theorem is challenged and no result is withdrawn.

This records a defect in how round-2 results are *reported*, found while packaging the
reusable evaluator. The underlying science is unaffected; the framing is not.

## The identity

`ROUND2_RESULTS_V2.json` records the invariant

```json
"m5_decision_equals_parent_authorization": true
```

M5 (`M5_TYPED_WITNESS`) authorizes exactly the parent-authorized set. This is not an
accident — it is the intended content of D-C2 (a claim is authorized iff it has a finite
untainted proof tree). A "hybrid" is defined as a task that the flat union authorizes but
the parent does not:

```
parent  :=  v_A or v_B
hybrid  :=  v_union and not parent
```

Given `M5 ≡ parent`, it follows by pure propositional identity that

```
unsafe_merges[M5]        =  parent and hybrid        ≡ False
needless_rejections[M5]  =  (not parent) and parent  ≡ False
m5_flagged               =  engine_hybrids           (exactly)
precision = recall = 1.0
```

for **any** corpus whatsoever. Exhausting all eight `(v_A, v_B, v_union)` triples confirms
it; the packaged test `test_m5_optimality_is_an_identity_not_a_measurement` pins it.

The committed aggregates are consistent with the identity, as they must be — e.g. family
`PARITY_PARTITION`: `union_authorized 67 − parent_authorized 63 = 4 = engine_hybrids`, and
`M5_TYPED_WITNESS.allows = 63 = parent_authorized`, with `unsafe_merges = 0` and
`needless_rejections = 0`.

## Consequence for the manuscript

The round-2 numbers

- `obstruction_detection.precision = 1.0`
- `obstruction_detection.recall = 1.0`
- `M5.unsafe_merges = 0`
- `M5.needless_rejections = 0`

are **analytic consequences of the definitions**, not empirical findings about X.509 trust
stores. They must not be presented as measured detector performance, and they must not be
compared against baselines as if they were an experimental win. Reporting them as measured
would be an unsupported claim of the exact kind the claim ledger forbids.

## What round 2 does empirically establish

These are real measurements on real third-party data and remain fully supported:

1. **The obstruction is non-vacuous in practice.** 46 hybrid tasks arise out of 1,962
   X.509 trust-store merge tasks derived from third-party OpenSSL test material (~2.3 %).
   The phenomenon the theory describes is therefore not confined to the study-authored
   fixtures; this is not an estimate of production prevalence.
   This, not the detector's perfect score, is the empirical contribution.
2. **The naive baselines pay a measurable price.** In `PARITY_PARTITION`:
   `M1_FLAT_UNION` performs 4 unsafe merges; `M2_INTERSECTION` and `M3_REJECT_ALL` each
   incur 63 needless rejections; `M4_OURS_B` incurs 14. These differ across methods and
   across corpora, so they carry genuine empirical content.
3. **The C3/C4 invariants hold on the corpus**: `c3_violations = 0`, `c4_resurrections = 0`,
   `c4_upstream_mirrors_ok = true` — non-trivial checks that could have failed.

## Required reframe

Replace any sentence of the form "M5 detects obstructions with precision and recall 1.0"
with a statement separating the two registers, for example:

> M5 authorizes exactly the parent-authorized set by construction (D-C2), so its perfect
> agreement with the hybrid set is definitional rather than measured. The empirical result
> is that the obstruction occurs at all in real trust-store material — 46 of 1,962 tasks —
> and that the flat-union and intersection baselines incur unsafe merges and needless
> rejections respectively at rates that vary by family.

## How this was found

While extracting a domain-agnostic evaluator (`packages/typed-merge-evaluator/`), the
round-2 metrics reproduced exactly without the engine ever reading the corpus — which is
only possible if they do not depend on it. That is the signature of an identity.
