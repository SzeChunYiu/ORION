# A benchmark repair that closed one shortcut and shipped another

**Observed:** 2026-08-21, tracing the one row P4's V3 claim ledger marks
`V2 NEGATIVE RESULT` — H3, "not supported / non-discriminating because all
systems saturated the eligible `CANNOT_CHECK` family" — back to the
construction that produced it, on the way to P4-U-T2 (#652), "identifiability
audit shows the benchmark measures the intended competence".

## Failure

P4's protected V2 campaign reports three hypotheses. H3 is abstention
competence: correct `CANNOT_CHECK` on the 30 cases whose gold terminal is
`CANNOT_CHECK`. `PUBLICATION_METRICS_V2.json` records

```json
"H3": {"orion_minus_baseline_correct_cannot_check": 0.0,
       "ci95_low": 0.0, "ci95_high": 0.0, "status": "NOT_SUPPORTED"}
```

with `"correct_cannot_check_rate": 1.0` for all eleven panel systems. The
repository already treats that as an instrument problem rather than a
comparative finding — `tests/unit/p4/test_p4_metric_headroom.py` pins the
saturation language, and the case generator carries a comment naming the cause:
under the V1 construction the `INSUFFICIENT_EVIDENCE` family emitted an **empty
evidence list**, so `len(evidence) == 0` classified the family at 420/420.

The generator on disk has since been repaired against exactly that cue. This
record is about what the repair produced.

### The published campaign, reconstructed

`host/generate_protected_cases.py` is deterministic in its seed, so the battery
can be regenerated and the frozen panel re-run against it. Restoring the empty
evidence list for the one repaired family and running
`run_baselines_v2.py` + `run_candidate.py` over 420 cases reproduces
`PUBLICATION_METRICS_V2.json` **exactly, for every system**:

| system | measured false promotions | published `false_promotion_rate` | measured correct `CANNOT_CHECK` |
| --- | --- | --- | --- |
| ORION | 0 / 360 | 0.000 = 0/360 | 30 / 30 |
| `provenai-citation-fidelity-influence` | 180 / 360 | 0.500 = 180/360 | 30 / 30 |
| `deepsciverify-abstract-to-full-escalation` | 210 / 360 | 0.583 = 210/360 | 30 / 30 |
| `provenanceguard-style-source-routing` | 210 / 360 | 0.583 = 210/360 | 30 / 30 |
| `rewardhackingagents-search-contamination` | 210 / 360 | 0.583 = 210/360 | 30 / 30 |
| `attributionbench-multisource-attribution` | 240 / 360 | 0.667 = 240/360 | 30 / 30 |
| `claim-level-auditability-provenance` | 240 / 360 | 0.667 = 240/360 | 30 / 30 |
| `fire-iterative-retrieve-or-verify` | 300 / 360 | 0.833 = 300/360 | 30 / 30 |
| `citation-presence-format` | 330 / 360 | 0.917 = 330/360 | 30 / 30 |
| `claimbench-sciclaimhunt-scientific-evidence` | 330 / 360 | 0.917 = 330/360 | 30 / 30 |
| `pooled-evidence-nli-support` | 330 / 360 | 0.917 = 330/360 | 30 / 30 |

The published `correct_cannot_check_rate` is 1.0 for every row.

Read the `citation-presence-format` row. It promoted 330 of the 360 hostile
cases and abstained on exactly the 30 whose evidence list was empty:
330 + 30 = 360. A system whose entire scientific judgement is "is there a
citation" scored **1.0 on abstention competence**, tying ORION, because the
abstention cases were the ones with nothing to count. That is what the
published H3 tie is made of.

Every number in the table is also invariant under the seed. Rerunning with a
completely unrelated seed gives the same eleven pairs. The host's secret seed
protects the case ids; it protects nothing the panel is scored on.

### The repair, measured with the same instrument

The repaired construction keeps the terminal and changes what must be reasoned
about: subtype A presents a non-supporting record with no corroboration
anywhere in the pool, subtype B presents support whose provenance attestation is
withheld. Its comment says separating them "requires inspecting the pool rather
than counting objects."

Counting objects is indeed dead. Counting *characters* is not.

Fitting judgement-free probes on the 150 `PUBLIC_*` cases the custody policy
lets a candidate see, and scoring them on the 270 `PROTECTED_*` cases it does
not (informedness = TPR + TNR − 1, which is 0 for any constant predictor):

| probe | cues read | V1 | V2 (on disk) |
| --- | --- | --- | --- |
| `evidence-object-count` | how many evidence / pool / used objects | **1.0** | 0.0 |
| `declared-hash-missingness` | which declared hash fields are null | 1.0 | **0.5** |
| `evidence-content-length` | `len(evidence[0]["content"])` | 1.0 | **1.0** |

The three V1 columns are one leak seen three ways, not three leaks: with no
evidence object present, every per-evidence cue collapses to the empty tuple,
which is unique to the family. The V2 columns are the informative ones.

`evidence-content-length` scores 20/20 of the protected `CANNOT_CHECK` cases
with **0 false positives over the other 250**. Across the whole 420-case battery
the evidence body takes five lengths — 86 (330 cases), 78 (30), 108 (30),
107 (15), 122 (15) — and `{107, 122}` is exactly the `CANNOT_CHECK` set. The
content templates are fixed strings with seed-derived tokens interpolated into
them, so those five lengths are the same for every campaign the generator will
ever emit. The null-hash pattern leaks the other half of the family on its own:
15 cases carry `declared_content_hash: null`, all 15 `CANNOT_CHECK`, no false
positives.

And the repair works, in the sense that matters least. Running the panel on the
repaired construction, H3 acquires headroom for the first time: ORION 30/30,
`deepsciverify` 15/30, the other nine **0/30**. A campaign run today would
report H3 strongly supported, with a 1.0-vs-0.0 margin, and that margin would
be a measurement of who compared a character count.

## Failure class

`LABEL_RECOVERABLE_FROM_CONSTRUCTION_CUE`

A benchmark label is separable by a feature of how the case was built rather
than of what the case is about. Every score computed on it — including a score
with a real denominator, a real spread across the panel, and correct
arithmetic — is a measurement of the cue.

This completes a progression with the two records beside it:

- `2026-08-unreachable-operator-inert-ablation/` — the **independent** variable
  never varied: the arm never reached the operator it ablated.
- `2026-08-vacuous-guard-zero-denominator/` — the **dependent** variable never
  varied: the guard was never pressed, so its zero had no denominator.
- here — **both varied, and the correlation is with the construction.** This is
  the strictly harder case, because the previous two are detectable by asking
  the artifact a question about itself: did this path run, what was this
  denominator. Nothing in a receipt distinguishes a benchmark that measures a
  competence from one that measures a template, since both produce a spread of
  rates over honest denominators.

Two things let it survive, and both are worth naming.

1. **The repair was scoped to the cue, not to the property.** V1's leak was
   found, described precisely, and fixed. What was never done — because there
   was no instrument for it — was to ask the repaired construction the same
   question. A fix aimed at one shortcut has no reason to produce a construction
   free of shortcuts, and here it did not.
2. **The saturation was the only symptom, and the repair removed the symptom.**
   Eleven identical 1.0s are conspicuous. A clean 1.0-vs-0.0 margin is not. The
   repair converted a visibly broken instrument into an invisibly broken one,
   and would have been recorded as a success.

## Correct response

1. Ask the question as a type. `orion.programme.benchmark_identifiability`
   fits declared judgement-free probes on the split a candidate may legitimately
   see and scores them on the split it may not; a probe that separates the label
   above the stated ceiling makes the audit `FAIL`. It keeps the word
   `identifiability` deliberately: `orion.study.p9.identifiability` already asks
   the mirror question — whether a view carries too *little* to determine the
   gold — with the same majority-vote-per-fingerprint construction. Too little
   and too much are one property measured from opposite ends, and both are
   properties of the benchmark rather than of any system scored on it.
2. Report informedness, not accuracy. P4's protected split is 20 `CANNOT_CHECK`
   in 270, so a rule that never predicts it is already 92.6% accurate. `ProbeResult.recovery`
   is `TPR + TNR − 1`, which is 0 for every constant predictor and 1 only for
   exact separation, and it is `None` — never `0.0` — when the split has no
   positives or no negatives to separate.
3. Make every way of not running the audit block. No probe registered, no eval
   cases, no fit cases, a constant label on the eval split, a probe whose cue is
   absent from every case, a ceiling finer than the split can express: each is a
   named `IdentifiabilityReason`, each returns `Outcome.CANNOT_CHECK`, and
   `IdentifiabilityAudit` refuses at construction to pair any of them with
   `PASS`. An audit nobody ran must not read as an audit that found nothing.
4. Refuse to hold the number. `AuditedScore` cannot be constructed with a
   blocking audit, so reporting `correct_cannot_check_rate` on this battery
   requires deleting the type rather than forgetting a check.
5. Join it to the guard verdict. `AuditedGuardVerdict` pairs a
   `GuardAssessment` with an audit: ORION's 0 false promotions in 360
   opportunities is a genuine `PASS` by exercise — P4 is the well-behaved case
   for `guard_exercise`, it carries its denominator — and the joined outcome is
   `CANNOT_CHECK` while the battery leaks. A `FAIL` still dominates, because a
   leak would only have made passing easier.
6. Register P4's probes where they can be re-run. `orion.study.p4.promotion_cues`
   declares the three above and requires each to state, in a sentence, why its
   cues carry none of the competence; `extract_promotion_cues` returns only
   counts and booleans, so no probe can read a support token, a hash, a lineage
   or an integrity status. That every P4 obligation is defined over a string is
   what makes "this probe does not implement the task" checkable.
7. Repair the construction so the length and missingness cues carry no signal.
   That is the campaign lane's call and is **not** done here. The diagnosis and
   the instrument are.

## Repaired, 2026-08-21

Item 7 was carried out the same day, under a protocol frozen before the repair
and before any panel outcome was seen:
`research/campaigns/2026-08-21-p4-battery-v3-identifiable/`.

The generator now carries all three constructions behind `--construction` --- v1
and v2 stay reproducible so the record of what they measured stays checkable ---
and defaults to `v3`, in which every case is shape-identical and families differ
only in the values of fields a hard gate is defined over. The register grew from
three probes to fourteen first, so the repair was measured against the property
rather than against the two cues named above. On the audit seed all fourteen
probes report informedness 0.0 on all three terminals; on v2 five of them report
1.0. The seed the panel actually ran on, `p4-v3-panel-20260821`, audits clean at
the same strict ceiling on all three terminals, so the reported H3 rests on an
audited battery.

**The 13-seed sweep is not uniformly clean, and saying so matters.** Three of the
thirteen fail the 0.0 ceiling: `v3-invariance-02` (`PROMOTE` 0.083, `BLOCK`
0.050), `v3-invariance-03` (`PROMOTE` 0.017) and `v3-invariance-06` (`BLOCK`
0.012). Every one is the `digest-prefix` probe, which the freeze registers as a
*noise control on the instrument* rather than a probe of the construction: it
buckets cases by the leading nibble of a SHA-256 over seed-derived content, so
with sixteen buckets over 270 eval cases a strict 0.0 ceiling fails on any seed
where a bucket happens to be dominated by a minority label. The sweep exists to
expose exactly this, and a first draft of this record reported it as thirteen
clean seeds, which it is not. What the sweep supports is the narrower statement
that no *content-shape* probe recovers the label on any seed, and that the
residual sensitivity is confined to the one probe that reads a digest.

The frozen panel, re-run on the repaired battery, reports H3 supported at 1.0:
ORION 30/30, `deepsciverify` 15/30, the other nine 0/30. The pre-registered
reading of that number, fixed before it was produced, is that it measures
terminal expressiveness under a non-compensatory gate lattice --- ten of the
eleven panel systems have no `CANNOT_CHECK` path at all once the empty-evidence
case is gone --- and not a finer-grained scientific judgement.

None of this restates V2. `PUBLICATION_METRICS_V2.json` is untouched and its H3
remains the correct record of what the v1 construction produced.

## General lesson candidate

**A benchmark score is a claim about a competence only for as long as nothing
cheaper explains the label.** Denominators, spreads, confidence intervals,
digests and independent reproduction all survive a leaking construction intact —
the V1 numbers here reproduce to the case, from a different seed, on a second
implementation — because none of them is a statement about what the label is
made of.

The sharper form, and the one that generalizes past this repository: **fixing a
shortcut is not the same as establishing there is no shortcut, and only the
second is a property of the benchmark.** A repair aimed at a named cue should be
treated as a new construction requiring a fresh audit, not as a discharged
obligation — because the repair changes the case, and what it changes is exactly
the thing the cue was made of.

Note what this costs and what it does not, because the audit was run on all
three terminals and only one of them is being condemned.

- `PROMOTE` **passes** at informedness 0.0. No probe tells a clean positive from
  anything else, on either construction. The instrument is capable of clearing
  an axis, which is what makes its verdict on `CANNOT_CHECK` worth acting on.
- `CANNOT_CHECK` **fails** at 1.0, on both constructions, by a different cue in
  each.
- `BLOCK` **fails** at 0.4, and the 0.4 is the same leak seen through a
  one-vs-rest lens rather than a second one. On the protected split the probe's
  20 true negatives are exactly the 20 `CANNOT_CHECK` cases and its 30 false
  positives are all 30 protected clean positives — it cannot separate `BLOCK`
  from `PROMOTE` at all. Remove the `CANNOT_CHECK` leak and this number goes
  with it.

So H1 — 0/360 false promotions against 180/360 for the strongest comparator — is
not shown here to rest on a shortcut: the discrimination it depends on, hostile
case from clean case, is precisely the one none of these probes achieves. It is
also not shown to be free of one. Three probes that clear an axis are three
probes, and the honest reading of a passing audit is "no registered cue
recovered this label", which is a statement about the probes as much as about
the benchmark. The register is the artifact; it should grow every time a new
cue is thought of, and every campaign should be re-audited against it.
