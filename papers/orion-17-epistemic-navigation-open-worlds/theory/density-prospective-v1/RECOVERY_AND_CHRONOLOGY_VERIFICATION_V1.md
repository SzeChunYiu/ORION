# ORION-17 density-prospective-v1 — recovery and chronology verification

The packet was on six branches and on **none of `main`**. `1db5eaa46`, the commit
that stamps the predictions, is **not an ancestor of `main`** either: every merge
here is a squash, so the branch commit was replaced and the packet never landed.
That is why this paper's recovery and verification boxes were open — not because
the work was missing, but because it was unreachable from the default branch.

Recovered path-by-path from `origin/shadow/orion17-density-v2-recovery-20260829`,
nine files, no rewriting.

## What was verified, and how

**Chronology.** The predictions and the outcomes are separate commits, in the
right order, four minutes apart:

| | commit | timestamp |
|---|---|---|
| `STAMPED_PREDICTIONS.md`, `HELD_OUT_DENSITY.json`, `o17_density.py` | `1db5eaa46` | 2026-08-28 **21:22:36** +0200 |
| `HELD_OUT_RESULT.json`, `RESULT.md` | `9841b15c4` | 2026-08-28 **21:26:46** +0200 |

Taken from the first commit that added each file across all refs, so the ordering
is a property of the history rather than of the files' own text.

**Threshold fixed before outcomes.** Read out of `STAMPED_PREDICTIONS.md` *at the
prediction commit*, before any outcome file existed: "The threshold is fixed here
at `1.5` and will not be moved after outcomes."

**Held-out set.** Five packages from five distinct organizations, all named
pre-outcome: `psf/requests` (0.84), `networkx/networkx` (2.14), `django/django`
(3.68), `tornadoweb/tornado` (5.57), `sympy/sympy` (8.70).

**The disambiguator was named in advance.** The packet registers `tornado` before
running it as the case that separates the density rule from a size-based
explanation — small at 74 modules but dense at 5.57 — and states the falsifier
plainly: "If `tornado` comes out sound, the density attribution" fails. It came
out unsound, as the density rule predicted and a size rule would not have.

**Independent checker.** Runs on the recovered packet and passes 8 of 8, including
two negative controls that are the reason this is worth more than 5/5 alone:

```
ok  all_five_predictions_correct
ok  tornado_the_disambiguator_is_correct
ok  tornado_is_small_but_dense
ok  exact_containment_never_falsely_retains
ok  both_outcome_classes_occur_in_the_held_out_set
ok  an_inverted_rule_would_score_worse
ok  training_domains_are_separated_by_the_same_threshold
ok  size_rule_would_mispredict_at_least_one
```

## What this does not do

It does not reopen the density route, and it makes no new claim. The result, its
scope and its terminal are exactly what the packet froze; this recovers those
bytes onto `main` and checks the chronology they depend on. `RESULT.md`'s own
limit stands unedited: "the disambiguation rests on `tornado` alone."
