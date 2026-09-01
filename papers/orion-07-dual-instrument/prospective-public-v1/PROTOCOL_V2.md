# ORION-07 public prospective series — protocol V2

**Committed with every item frozen and no outcome in existence.**
**Scientific authority delta: `NONE`.** No score is computed here; `FINAL_SCORE.json`
does not exist for any item and cannot until the horizon.

## The gap this closes

`JOURNAL_READINESS.md` states the paper's own blocker plainly: *"Run at least 2–3
additional prospectively frozen frontier-question instances using the same benchmark
contract… Until then, [it] must not be labeled `PEER_REVIEW_READY` or presented as an
evaluation of instrument reliability."* Its terminal is
`MANUSCRIPT_REVIEW_PASS / EVIDENCE_GATE_BLOCKED`, and only two instances existed —
`Q3-R1-QG19` and `Q3-R2-QG20`.

A hostile review reached the same verdict independently: *"the real experiment has not
happened: one prospective case cannot support the scientific story the machinery
suggests."* This series is that experiment, at **n = 24**.

## The change that matters more than n

The two existing instances bind to *internal* ORION frontier questions, whose outcomes
ORION itself later produces. That is self-scored evidence, and no amount of it answers
the objection.

Here **the outcome is produced by people who have never heard of this study.** Each item
is an open pull request in a public repository; it resolves when its maintainers merge
it, close it, or leave it open. `DEFERRED_OUTCOME_BINDING.json` records
`outcome_produced_by_q3_instruments: false` and names the upstream project. This is the
same external-authority substitution used elsewhere in the programme — ORION-04's
calibration suite takes its ground truth from published closed forms — and it needs no
second researcher.

## Instruments

Unchanged in kind from the internal series, so results are comparable.

- **Lane A** — LLM host research diagnosis. Executor recorded per item:
  Claude Opus 5, Anthropic, `LLM_HOST_RESEARCH_DIAGNOSIS`.
- **Lane B** — the deterministic rule set `q3_public_controller_v1.py::decide`, over
  typed observations only.

Both receive the **identical** `SHARED_PACKET`, and each receipt records its
`shared_packet_sha256`. Any disagreement is therefore an instrument difference, not an
information difference.

**Lane B was frozen first, in commit `dd191b8a5`, before a single packet was built or a
single Lane A verdict written.** Lane A is the session host, so had the rule set been
authored afterwards it would have been the same judgement wearing a deterministic
costume rather than a second instrument. The ordering is the control.

## Frozen inclusion rule

Ten repositories named in advance: `python/cpython`, `numpy/numpy`, `pytest-dev/pytest`,
`scikit-learn/scikit-learn`, `pallets/flask`, `psf/requests`, `tornadoweb/tornado`,
`networkx/networkx`, `sympy/sympy`, `django/django`. First 8 non-draft open PRs per
repository, sorted by `(repo, pr_number)`, first 24 taken.

No item was inspected for how likely it looked before selection. Selecting on apparent
outcome is the failure this rule exists to prevent, and it would be undetectable
afterwards.

## Three-valued outcome, and why the third value is not optional

```
MERGED                  merged on or before the horizon
CLOSED_UNMERGED         closed without merge on or before the horizon
UNRESOLVED_AT_HORIZON   still open at the horizon
```

**Horizon: 2026-11-30T09:15:29Z**, ninety days from freeze.

A pull request still open at the horizon has not falsified a merge prediction; it is a
distinct outcome. Collapsing it into "not merged" would manufacture signal out of
silence — the same error ORION-23 records as load-bearing, where `UNKNOWN` is a third
outcome that *"cannot be coerced into reuse/revoke"*.

## Pre-outcome agreement, recorded before any resolution

| | Lane A | Lane B |
|---|---|---|
| `PREDICT_MERGED` | 11 | 19 |
| `PREDICT_UNRESOLVED_AT_HORIZON` | 11 | 5 |
| `PREDICT_CLOSED_UNMERGED` | 2 | 0 |

**AGREE 14/24 · DISAGREE 10/24.**

That the instruments disagree on 42% of items is what makes the series informative.
Instruments that agree everywhere measure nothing about each other, and the internal
series' `AGREE` on every relation is exactly the degenerate case a referee would
challenge.

The disagreements are principled rather than noisy. Lane B has no variable for project
culture, so it reads `psf/requests#7499` as a small fresh patch and predicts merge; Lane
A knows the project is in maintenance mode with a near-zero community-merge rate and
predicts it will simply sit. On Django, Lane B sees small diffs and predicts merge while
Lane A weights the ticket-plus-review pipeline. Whether that domain knowledge is worth
anything is precisely what the horizon will settle.

## A declared weakness in Lane B

**Lane B produced only two of its three verdicts: no rule can emit
`PREDICT_CLOSED_UNMERGED`.** The verdict is reachable in the type but not in the rule
graph, so on this item set Lane B is effectively two-valued while Lane A used all three.

This was found by inspecting the frozen predictions and is recorded rather than patched.
Amending the controller now would be tuning the instrument against the item set it is
about to be judged on, and no outcome exists yet to justify the change. It is a real
limitation of V1 and belongs in the results.

## Scoring, and what may not happen before the horizon

At the horizon, each item is resolved with the recorded `observation_command`, and only
then may `FINAL_SCORE.json` be written. Until then every item carries
`scientific_outcome_accessed: false`, `aggregate_accuracy_computed: false`, and
`scored: false`.

No item may be added retroactively, no verdict revised, and no historical outcome scored
as prospective — the board is explicit that historical outcomes must never be counted in
prospective `n`.
