# ORION-12: the threshold the negative was measured against was not one the system could pass

**Date:** 2026-08-22
**Authority:** diagnosis of a frozen negative, not a revision of it
**Promotion:** forbidden. The frozen verdict stands exactly as issued. What
changes is what that verdict is evidence *about*.
**Gates:** `orion.programme.gate_attainability`, `orion.programme.attainable_margin`
 — both pre-existing. ORION-12 never ran either.
**Ceiling constructor:** `orion.study.p2.acquisition_ceiling`
**Tests:** `tests/unit/p2/test_p2_acquisition_ceiling.py`

## What was reported

`P2_V2_WIDE_BOUNDED_MATCHED_RESULT_2026-08-18.json` compared a route-governed
multiroute system against a single-route lexical baseline over 24
AutoResearchBench Wide tasks, under a matched budget of three provider requests
per task, and returned `BOUNDED_EXTERNAL_SIGNAL_NOT_POSITIVE`. The frozen
positive rule wanted `iou_delta >= 0.03`; the campaign measured `0.003687`.

Read alone that is a system that was tested and fell short by roughly eightfold.

## What the model reproduces first

Nothing below is trusted until the scorer is reproduced. The per-task metric is
`hits / (submitted + gold - hits)`, averaged over tasks, with a submitted set of
20 — a size not assumed but implied to four significant figures by both arms'
own published `avg_precision`. That closed form returns:

| arm | `avg_iou` recomputed | published | `avg_recall` recomputed | published |
|---|---|---|---|---|
| governed multiroute | 0.009958 | 0.009958 | 0.041005 | 0.041005 |
| lexical arXiv | 0.006271 | 0.006271 | 0.024636 | 0.024636 |

Both arms, both metrics, to six decimals. A ceiling computed from a metric you
have not reproduced is a guess with decimals on it; this one is not.

## What the stage diagnostic adds

Across the slice the answer key holds **229** gold identifiers. The governed
system's routes *returned* **7** of them — 3.06 per cent — and **6** of those 7
survived into its submitted set. Exactly **one** gold identifier across the
whole campaign was acquired and then discarded by selection. **222 of 229 were
never returned by any route at any point.**

So selection was not the binding constraint. Acquisition was, which is what the
diagnostic's own `dominant_failure: CANDIDATE_GENERATION` says in words.

## The ceiling, and what it does to the threshold

A selector cannot submit what its routes never returned. The arm's best
attainable score is therefore what it scores if a perfect selector keeps every
gold identifier it did acquire:

- governed observed `avg_iou`: **0.009958**
- governed ceiling `avg_iou`: **0.011260**
- total selection headroom in the arm: **0.0013**

Handed to `gate_attainability.assess_threshold_support`, that support returns
`THRESHOLD_UNATTAINABLE`. The frozen threshold was not a bar the system missed.
It was a bar the system could not reach:

| bound | max attainable `iou_delta` | threshold | short by |
|---|---|---|---|
| control held at its observed score | 0.004989 | 0.03 | **6.01×** |
| control conceded every point it scored | 0.011260 | 0.03 | **2.66×** |

The second row is the strong form. Concede the baseline everything — drive it to
zero, the most generous world the treatment could have been measured in — and no
query derivation, no route-governance policy, no selection rule, and no conduct
by either arm produces a pass. The rule demanded a summed per-task IoU of
**0.8705** where the measured acquisition supported at most **0.2702**.

A negative from such a rule is a measurement of the rule. The programme's own
gate says so in its verdict: `THRESHOLD_UNATTAINABLE`, which for a `HYPOTHESIS`
gate carries `FAIL` — a failure of the gate's attainability audit, not of the
system it was pointed at.

This is not a blanket excuse, and the same machinery says so: the campaign's
other frozen threshold, `recall_delta >= 0.0`, was **reachable**, and was met at
`+0.016369`. Only the IoU threshold was unreachable.

## Why the ceiling was that low

The scorer's gold is an arXiv identifier. Of the governed system's three
configured routes:

| route | raw gold identifiers returned | admissibility |
|---|---|---|
| arXiv | 7 | ADMISSIBLE |
| OpenAIRE | 0 | INADMISSIBLE |
| DBLP | 0 | INADMISSIBLE |

OpenAIRE and DBLP did not fail. All 72 requests returned `OK` carrying records;
the runner's own per-route note for both is `no_arxiv_identifier_in_response`.
Their records do not carry an identifier in the scheme the answer key is written
in, so nothing they return can match, whatever the query.

That makes `matched_provider_requests_per_task: true` the wrong matching
predicate:

| arm | requests/task | of those, on an admissible route | scoring-eligible fraction |
|---|---|---|---|
| lexical arXiv | 3 | 3 | 1.00 |
| governed multiroute | 3 | 1 | 0.33 |

The counts matched. The opportunity did not. The treatment arm was given
one-third the baseline's exposure to the only backend whose records can score —
and still returned more hits (6 vs 4), more tasks with a hit (4 vs 3), and two
tasks strictly better with none strictly worse.

## The lesson

The tempting write-up here is "we found a new failure mode and built a mechanism
for it." That is not what happened, and the true version is more useful.

The programme already had both halves.

`orion.programme.gate_attainability` — *"Preregistered gates that cannot report
a negative the protocol could not have avoided"* — is exactly the question this
campaign needed asked, and it was written for P14A, whose `0.08` gate sat 1.9×
above the ceiling of the support it was frozen against.

`orion.programme.attainable_margin` — *"Superiority margins that cannot be
reported over a baseline which could not compete"* — is exactly the second
question, arms differing in a way the claim does not name, and it was written
for P12A, whose baseline could not express two of the four allocations it was
scored on.

ORION-12 is the same two defects, in a paper that shipped a negative without running
either check. The gate was frozen against a threshold nobody bounded, and the
arms were matched on a predicate that compared the wrong quantity.

So the answer to *why we could not* is not that the harness lacked the tool. It
is that **a mechanism the programme owns does not run itself.** Reachability was
available as an import and was never called; matched exposure was available as a
concept and was replaced by a request count that looked like it.

What was genuinely missing is narrower, and is all this module adds:
`capability_from_cases` takes `ceiling_scores` as given and `StatisticSupport`
takes an infimum and supremum as given. For a retrieval benchmark nobody could
produce those numbers, because the ceiling is not in the scores — it is in what
the routes returned. `arm_ceiling` is that constructor, `as_capability` and
`delta_support` are the two adapters, and route admissibility names the specific
unnamed variable that made this arm's ceiling low.

Two preconditions follow, and both now have somewhere to run:

1. **A frozen threshold must be shown reachable before it is frozen**, against a
   pilot's measured acquisition. Unmeasured acquisition is `CANNOT_CHECK`, never
   an assumed zero — `delta_support` and `as_capability` raise rather than
   return a bound over an arm whose retrieval was never recorded.
2. **Arms are matched on admissible exposure, not on request count.** A route
   earns admissibility by being *observed* to emit the answer key's identifier
   scheme. A route that returned nothing is `UNPROBED` — an empty result convicts
   the query, not the backend — and unprobed spend blocks a matched-exposure
   claim rather than being credited.

## Negative controls

Five mutations were run against the mechanism; each failed the test that names
it, and none passed silently:

| mutation | test that caught it |
|---|---|
| ceiling collapses to the observed score | richer-acquisition flip, submission-cap |
| support supremum unbounded | richer-acquisition flip |
| support infimum raised to the supremum | richer-acquisition flip |
| `matched_exposure` compares total requests | threefold-exposure-gap |
| `as_capability` credits unmeasured acquisition | unmeasured-acquisition refusal |

The fourth is the one that matters most: substituting the campaign's *actual
shipped predicate* — `matched_provider_requests_per_task` — fails exactly the
test that says the counts matched and the opportunity did not. That is the
demonstration that the replacement is strictly stronger than what was used, and
not merely different from it.
