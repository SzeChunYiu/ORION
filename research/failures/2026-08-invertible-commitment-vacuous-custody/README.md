# A protected answer key whose commitment opens to the case number

**Observed:** 2026-08-21, tracing what P5's one populated empirical result — GLM-5.2
at 21/24 on hidden-cause attribution — is a measurement of, on the way to P5-U-T4
(#653), "at least one learned or invented mechanic causes a replicated gain".

## Failure

P5 publishes nine evidence tables. Seven are `CANNOT_CHECK` and say so honestly:
`evidence/tables/INDEX.json` records `empirical_authority_h1: CANNOT_CHECK`,
`live_campaign: CANNOT_CHECK`, and each blocked table carries
`do_not_impute_from: "glm-5.2-attribution 21/24 accuracy"`. The two populated
tables both come from a single 24-case run against
`evidence/hidden-cause-suite/PROTECTED_SUITE_V1.json`, and #653 makes that run the
programme's next move: "the retained 21/24 attribution result is a research map.
Study the three errors mechanically."

The three errors are not a research map. They are three points on a battery whose
protected label is the case number.

`protocol/PROTECTED_SUITE_FREEZE_V1.md` states the threat model itself, correctly
and in advance:

> **Low-entropy truth commitment.** A raw SHA-256 of `protected_root_cause` would
> be unsafe because the label has only eight possible values and can be
> enumerated. The manifest therefore commits to `{protected_root_cause, nonce}`.
> The nonce remains only in protected custody until any authorized post-study
> opening.

`orion.study.p5.freeze` repeats it at the point of use:

```python
def _root_commitment(root: str, nonce: str) -> str:
    # The nonce stays only in the protected opening material. Hashing one of eight
    # public enum labels without a nonce would be brute-force disclosure.
    return sha256_json({"protected_root_cause": root, "nonce": nonce})
```

Every protection the scheme has therefore lives in the nonce. The suite on disk
ships 24 of them, and `int(root_cause_nonce, 16)` is `[1, 2, 3, … 24]`.

### The commitment opens to the case number

Rebuilding the root-cause commitments a freeze of the shipped suite would publish
and running four declared cheap attacks against them
(`python -m orion.study.p5.hidden_cause_custody`):

| probe | nonces it tries | commitments opened | SHA-256 evaluations |
| --- | --- | --- | --- |
| `ordinal-nonce` | the case's 1-based position, in hex | **24 / 24** | **108** |
| `small-integer-nonce` | integers 0–4095 | **24 / 24** | 2 508 |
| `constant-nonce` | all-zero, all-`a`, all-`f`, `SHA256("")` | 0 / 24 | 768 |
| `case-id-digest-nonce` | two derivations from the published case id | 0 / 24 | 384 |

108 is not a bound, it is the count: sorted over the eight-family enum, each
case's label sits on average 4.5 candidates in. The worst case is 192. A blind
dictionary that assumes nothing about the scheme beyond "the nonce might be a
small integer" — 100 000 nonces × 8 labels, 800 000 precomputed digests, 3.1
seconds — also recovers 24 of 24.

The last two rows are the reason the first two count. A probe set that opens
everything cannot tell a leaking manifest from an over-eager instrument.

`validate_protected_suite` accepts those nonces. It fails closed on nine
documented conditions, one of which is "a hidden root label has no unique nonzero
256-bit nonce" — and that check rejects exactly one value, `"0" * 64`, out of
2^256. `0…01` is unique, non-zero, 64 lowercase hex characters, and passes. The
unit test pins this: a suite whose nonces are `0…01`…`0…08` freezes cleanly.

### The label is the case number

The commitment is the *planned* protection. It is not needed. The suite is emitted
as eight consecutive blocks of three, and the block order is the order the eight
families are printed, numbered 1–8, in the attribution prompt inside
`scripts/run_p5_glm_attribution.py`:

```text
cases 001-003  RETRIEVAL_MISS                       prompt family 1
cases 004-006  ROUTING_PLANNING_MISS                prompt family 2
cases 007-009  IMPLEMENTATION_BUG                   prompt family 3
cases 010-012  ENVIRONMENT_DEPENDENCY_TOOL_FAILURE  prompt family 4
cases 013-015  EVALUATOR_METRIC_BUG                 prompt family 5
cases 016-018  REPRESENTATION_GAP                   prompt family 6
cases 019-021  MEASUREMENT_SPECIFICATION_GAP        prompt family 7
cases 022-024  METHOD_BASIS_GAP                     prompt family 8
```

`prompt_families[(n - 1) // 3]` is the gold label on **24 of 24** cases, and the
prompt hands the model both halves: the numbered list, and `Case P5-HC-007` above
the symptom.

Fitted as a shortcut probe on the split a candidate can obtain and scored on the
rest (`orion.programme.benchmark_identifiability`, informedness = TPR + TNR − 1,
which is 0 for any constant predictor):

| fit split | eval | probe | informedness | false positives |
| --- | --- | --- | --- | --- |
| one case per family (8) | 16 | `case-id-ordinal-block` | **1.0 on all 8 labels** | 0 / 14 each |
| one case per family (8) | 16 | `nonce-ordinal-block` | **1.0 on all 8 labels** | 0 / 14 each |
| one case per family (8) | 16 | `visible-context-key-count` | 0.0 | 0 |
| the 3 golds P5 publishes | 21 | `case-id-ordinal-block` | **1.0** on all 3 blocks | 0 / 4 each |

The second fit split is the honest one. P5 does not merely leak one label per
family; `evidence/tables/P5-ATTRIBUTION_RESIDUAL_ERRORS.json` names three golds
outright, and `evidence/glm-5.2-attribution/report.json` publishes
`per_family_metrics[family]["cases"]`, which is the entire answer key in plaintext
and recovers 24 of 24 with no hashing at all. Three published labels are enough to
fit a rule that is exactly right on every other case in their blocks.

Interleaving the families off the ordinal and re-running the same probes drops the
worst informedness to **0.0**. The instrument clears the axis when the axis is
clean, which is what makes its verdict here worth acting on.

So the scoreboard for this battery reads:

| predictor | reads | correct |
| --- | --- | --- |
| `prompt_families[(n-1)//3]` | the case number | **24 / 24** |
| GLM-5.2 | the symptom and context | 21 / 24 |
| keyword predictor over `visible_symptom` | the symptom | 15 / 24 |
| majority family | nothing | 3 / 24 |

The model reasoned. Its three errors read as reasoning — `P5-HC-002` argues from
"embeddings were generated but cosine search fails" to `REPRESENTATION_GAP` and
loses to gold `RETRIEVAL_MISS` on a distinction the symptom does not settle. That
is the point. The battery cannot distinguish a system that diagnosed from a system
that counted, and on this battery counting wins.

### The suite never passed its own validator

`validate_protected_suite` refuses the shipped file on the first case:

```text
ValueError: case P5-HC-001.fresh_tasks[0].content_hash must be a 64-character
lowercase SHA-256 hex digest
```

`fresh_task_payloads` and `negative_variant_payloads` are both `{}`, every
`content_hash` is the literal string `placeholder_hash_for_fresh_task_NNN`, and
`evaluator_hash` is 64 `a` characters. The freeze that would have produced the
candidate packet and the commitment manifest was therefore never run on this
suite, and no manifest for it exists. The disclosure above is what publishing one
*would* do, measured before it is published rather than after.

## How it survived

Three properties, and each is worth naming because none of them is negligence.

1. **The known discrepancy is real, and the obvious repair does not close it.**
   `research/verification/records/P5.glm-5.2-attribution-21-24.json` already
   records `P5.protected-label-colocated-in-suite-json` — "`PROTECTED_SUITE_V1.json`
   stores `protected_root_cause` beside `visible_symptom`". The repair that
   discrepancy implies is the one `freeze.py` is built for: strip the protected
   fields, publish the candidate packet, publish the commitment. Doing exactly
   that leaves the ordinal in the packet and puts an openable digest in the
   manifest. Verified: the emitted packet carries no `protected_root_cause` field
   and still determines all 24 labels. This is P4's lesson arriving one step
   earlier — a repair aimed at a named cue is a new construction needing a fresh
   audit — except that here the audit can be run *before* the repair ships.

2. **A leakage layer existed, ran, and returned `PASS`.** `research/verification/audit.py`
   scores a `leakage_shortcut` layer for P5 and computes two real things: whether
   an exact gold token appears in the symptom (0 cases) and how well a keyword
   predictor over the symptom does (15/24). Both look only at the symptom text.
   Nothing looks at the case's position, and the layer's status is the literal
   constant `layer_result("PASS", …)` — the verdict does not depend on either
   measurement. The accompanying discrepancy fires only at `keyword_correct >= 18`,
   so 15 is silent. A shortcut check that enumerates the cues it knows about
   cannot notice the one nobody wrote down.

3. **The commitment reads as the strong step.** Nine fail-closed conditions,
   unique 256-bit nonces, a documented threat model that names brute-force
   enumeration by name. Everything in that list is true. None of it is a
   statement about whether the nonce was guessable, and a nonce is the one field
   whose quality is invisible on inspection: `0…01` and a CSPRNG draw are both
   64 hex characters, both unique across the suite, both non-zero. The only thing
   that separates them is whether somebody ran the attack.

## Failure class

`INVERTIBLE_COMMITMENT_VACUOUS_CUSTODY`

A result is reported as prospective because its answer key was committed before
the run. The commitment is invertible from what was published, so the key was
never withheld, and "committed in advance" and "hidden from the candidate" come
apart while every integrity property holds.

This is the fifth variance an experiment has to establish, and the four beside it
are the reason it is a distinct one:

- `2026-08-unreachable-operator-inert-ablation/` — the **mechanism** never ran.
- `2026-08-vacuous-guard-zero-denominator/` — the **dependent** variable could not vary.
- `2026-08-unapplied-treatment-vacuous-null/` — the **independent** variable did not vary.
- `2026-08-label-recoverable-from-construction-cue/` — both varied and the
  correlation is with the **construction**.
- here — the construction is clean *by assumption*, because the label was sealed;
  and the seal opens. The **blind was not blind.**

The four before it are all questions about a run: did this path execute, what was
this denominator, did this input differ, does this cue separate. This one is a
question about an artifact that was published on purpose, whose whole function is
to be safe to publish. Every previous instrument would clear it. Operator coverage
sees a freeze that ran. `GuardExercise` sees a real denominator of 24. Treatment
contrast sees genuinely different inputs per case. And `benchmark_identifiability`
would clear a properly stripped candidate packet on any cue that reads the case
*content*, because the leak is in the case's address.

The two halves share one cause, which is why they belong in one record: the suite's
entire protection budget is a single integer, spent three times. The ordinal is the
case id, the ordinal is the nonce, and the ordinal divided by three is the label.

## Correct response

1. Attack the commitment before publishing it, as a type.
   `orion.programme.commitment_custody` takes the published digests, the enumerable
   domain the secret is drawn from, and the scheme, and runs declared cheap
   adversaries against them. `SealedSecret` requires a written `domain_rationale`
   and `DisclosureProbe` a written `cost_rationale`, for the reason
   `GuardExercise.opportunity_definition` is required: an attack nobody can argue
   is affordable neither condemns nor clears a commitment.
2. Return three values. An unattacked commitment is `Outcome.CANNOT_CHECK`, which
   blocks a promotion exactly as `FAIL` does. `CustodyAudit` refuses at
   construction to pair `PASS` with any vacuity reason, and every way of not
   running the attack is a named one: no probe registered, nothing sealed, a probe
   that produced no nonce candidate, a budget exhausted mid-sweep, a ceiling finer
   than the manifest's resolution. An attack that ran out of money did not
   establish that the commitment holds.
3. Prove the attack could have worked. `SchemeCanary` is a `(secret, nonce, digest)`
   triple the real freeze emitted; an audit whose modelled scheme cannot reproduce
   it returns `SCHEME_NOT_DEMONSTRATED` rather than "no secret disclosed". This is
   the P1 failure — an unreachable path counted as a comparison — applied to the
   adversary instead of to the system under test, and it is the one check here
   with no analogue in the other instruments. `FREEZE_CANARY` is re-derived from a
   live `freeze_protected_suite` run by the unit tests, so a refactor of
   `_root_commitment` turns the audit red instead of quietly turning it green.
4. Refuse to hold the number. `ProspectiveScore` cannot be constructed with a
   blocking custody audit, so reporting `attribution_accuracy = 0.875` as a
   prospective result requires deleting the type rather than forgetting a check —
   the same refusal `AuditedScore` makes about a leaking benchmark. "Prospective"
   is a claim about custody, not about chronology, and no timestamp repairs a key
   that was recoverable from what was published.
5. Register P5's cues where they can be re-run. `orion.study.p5.hidden_cause_custody`
   declares the four disclosure probes and three shortcut probes above, each with
   the sentence saying why it carries none of the diagnostic competence, and
   `python -m orion.study.p5.hidden_cause_custody` audits the shipped suite and
   exits 3. An instrument that only ever runs on its own fixture is the failure it
   was written to catch.
6. Regenerate the suite so the ordinal carries nothing: draw each nonce from a
   CSPRNG, and emit the cases in an order independent of the family. Both are one
   line in the generator and neither is done here — that is the campaign lane's
   call. Measured on the shipped cases with the families interleaved off the
   ordinal, the shortcut probes drop to informedness 0.0; measured with
   high-entropy nonces, the custody audit passes at 0 of 24 disclosed. The
   diagnosis and the instrument are what this record delivers.
7. Give `validate_protected_suite` the check it is missing, or stop implying it
   has one. Rejecting `"0" * 64` is not an entropy requirement, and a document
   that names brute-force enumeration as its threat model should not leave the
   only defence against it unverified.

## General lesson candidate

**A commitment proves when a value was fixed. It does not prove that the value was
kept.** Those are different properties and only the first is established by
publishing a digest: the second depends entirely on the entropy behind it, which
is not visible in the artifact, not checkable by a schema, and not implied by any
number of fail-closed conditions on everything else. Every hash-based
pre-registration in a repository should be asked what its secret's domain is and
whether a declared cheap enumeration opens it, and the answer has to be a run, not
an argument.

The sharper form, and the one that generalizes past this repository: **an
experiment must verify that what it withheld was actually withheld.** A protocol
can be designed prospectively, executed in the right order, receipted, digest-bound
and independently replayed, and still be a test in which the system under
evaluation could have read the answer. Nothing downstream detects this — a leaked
key produces the same receipts as a kept one, and it usually produces a *better*
score, which is the direction nobody audits.

Note what this costs P5 and what it does not, because the paper is careful and the
carefulness should be preserved. `P5-3_cause_confusion.json` is marked
`empirical_authority: DESCRIPTIVE_ONLY`; seven of nine tables are `CANNOT_CHECK`
and refuse to impute from the 21/24; the README says plainly that no governed
self-improvement claim is authorized. None of that is overturned. What this record
removes is the next step: 21/24 cannot be mined for which discriminator the three
errors are missing, because the battery does not require a discriminator, and the
`PROTECTED_SUITE_FREEZE_V1` workflow cannot be reused for the multi-generation
P5-U campaign until the ordinal stops being the secret. The strongest thing that
remains true of the run is that a model reading symptoms scored 21/24 where a
model reading nothing scores 24/24 — which is a fact about the suite, and now
a measured one.
