# ORION-17 rule-disagreement study v1 — executed

**Terminal: `NO_DISCRIMINATION`.** All 20 repositories measured, zero `CANNOT_CHECK`.

## Verdict

| rule | correct (all 20) | correct (16 informative) |
|---|---|---|
| density (`edges/modules >= 1.5`) | 14/20 (0.70) | 10/16 (0.625) |
| module count (`>= 49`) | 6/20 (0.30) | 6/16 (0.375) |
| edge count (`>= 216`) | 6/20 (0.30) | 6/16 (0.375) |

The protocol's gate **fails**: density needed `>=15/20` overall and `>=7/10` in each
stratum, and took **14/20** with only **4/10** in `large_manyedge_sparse`. Neither
rival passes the same gate either (6/20 each), so `ABSOLUTE_SIZE_OUTPERFORMS_DENSITY`
is equally unsupported.

Paired exact tests (every pair is discordant by construction, so McNemar exact
reduces to a two-sided binomial sign test at p=0.5):

- all 20: density 14 vs rival 6, **p = 0.115**
- informative 16: density 10 vs rival 6, **p = 0.454**

Neither is significant. The statistical model is confirmed against the protocol's own
constant: P(A>=7, B>=7, A+B>=15) for independent Binom(10, 0.5) is
`0.01580810546875`, matching `null_joint_probability` exactly.

**Density is not refuted either.** On the 16 informative repositories the outcome is
**constant — all unsound** — so the cohort carries no outcome variation for any rule
to be scored against. The design could not discriminate. That is a different result
from density losing, and it is the honest one.

## The outcome definition, and where it came from

The protocol names the terminals and the gate but **does not define the outcome**; it
only refers to "donor-coarse policy outcomes". I did not choose one. The definition
is read off the campaign's own instrument,
`transitions/measure_p7_closure_retention_v1.py`, which I invoked through its
documented CLI so that no policy logic was retranscribed:

> **`donor-coarse` is UNSOUND on a repository iff `false_closure_retention > 0`** —
> it preserved a certificate whose premises had moved.

`n_changes = 700` was **recovered, not chosen**. In the campaign's own
`HELD_OUT_RESULT.json`, tornado and sympy both saturate at `commits_examined = 700`,
and the five domains sum to 2,265 changes and 1,671,821 certificate decisions —
reproducing the manuscript exactly. Fetch depth 800 matches the campaign's
`o17_density.py`. Instrument fidelity was then confirmed on the campaign's own data:
`requests` reproduced `changes_used = 79` (recorded: 79) and `tornado` reproduced
`changes_used = 619` (recorded: 619) with 12,787 false retentions against a recorded
12,773, the difference being 14 newer commits.

Nothing was re-fitted: 1.5 / 49 / 216 are used exactly as frozen.

## Why the test could not discriminate

`donor-coarse` buckets a module by `m.split(".")[1]`. For a `src/` layout, every
module of package `P` is named `src.P.x`, so that component is `P` for **all** of
them: the bucket set collapses to `{P}`, the policy reopens everything, and it has
degenerated to **always-reopen** — which cannot falsely retain. Such a repository is
"sound" for a reason unrelated to density, module count or edge count.

Verified directly:

| repo | layout | preserve | outcome | degenerate |
|---|---|---|---|---|
| requests | `src/requests` | **0** | sound | yes (reproduces the campaign's own held-out row) |
| flask | `src/flask` | **0** | sound | yes (campaign calibration) |
| tornado | `tornado` | 32,285 | unsound | no (flat control — the effect is layout-specific) |

In the cohort, 4 repositories are `src`-layout (`openai`, `anthropic`, `cohere`,
`llama-cloud`), all in stratum B, and all four measured `preserve = 0`. **Every one
of density's stratum-B wins is a degenerate repository.** On the 6 informative flat
repositories of stratum B, density is **0/6** (p = 0.031 against it), while in
stratum A it is 10/10 (p = 0.002 for it). A rule that is perfectly right in one
stratum and perfectly wrong in the other is tracking the stratum, not the outcome.

A degenerate case is uninformative for **every** rule symmetrically — it scores
"sound" whatever any rule predicts, so it simply credits whichever rule happens to
predict "sound" in that stratum, which here is density. I kept all four in and
reported both cuts rather than dropping them.

## Post-hoc diagnosis (not a validated rule)

Marked explicitly: this was found **after** outcome access, and the protocol forbids
a new threshold after outcome access. It is offered as a diagnosis of why the
prespecified test failed, **not** as a rule that wins.

Degeneracy predicts the outcome **20/20**: all 4 degenerate repositories are sound,
all 16 non-degenerate ones are unsound. Equivalently, layout does: 4/4 `src` sound,
16/16 flat unsound. The only outcome variation anywhere in this cohort is produced by
the policy's own degeneracy, not by any structural property the three rules measure.

## Adverse finding about the campaign's foundation

This follows from the verification measurements alone and needs no further run.

The campaign's 8 projects contain exactly **two** "sound" observations — flask
(calibration) and requests (held-out) — and **both are degenerate**, verified here at
`preserve = 0`. The other six (numpy, scipy, networkx, django, tornado, sympy) are
all flat and unsound.

So the campaign has **no informative sound example at all**. The 1.5 density
threshold separates a set whose only "sound" points are sound for a mechanical
reason, and the frozen rival cutpoints — which the protocol derives as integer
cutpoints "strictly between max observed sound and min observed unsound counts" —
take their `max observed sound` end (flask's 24 modules / 19 edges) from one of those
same degenerate packages. All three rules' boundaries rest on it.

The published 5/5 held-out result is not thereby wrong: four of its five predictions
are unsound calls on flat packages and stand on their own. But its single sound
prediction, and the load-bearing claim that the threshold *separates* two classes,
rest on a case that carries no information about dependency structure.

## Corrections to my own earlier artifact

`NOTE_V1.md` previously said this layout hypothesis was "tested and refuted" and that
"the frozen thresholds are unaffected". Both statements are **withdrawn** and have
been corrected in place. The refutation was correct only about the *graph builder*
(re-rooting flask and requests gives identical counts, because they use relative
imports). The confound lives one level down, in the `donor-coarse` policy's
bucketing, which I could not see until I read the outcome code.

## What this does not claim

- No constant was re-fitted, and no repository was dropped.
- Density is **not** shown to be wrong; the cohort is shown to be unable to tell.
- The post-hoc degeneracy observation is **not** a validated rule and must not be
  promoted into one without a fresh prospective design.
- A successor that wants to identify the mechanism needs repositories where
  `donor-coarse` is non-degenerate **and** the outcome actually varies. Every
  non-degenerate repository in this cohort came out unsound, so a sound,
  non-degenerate example is the missing case — and none of the 8 campaign projects
  supplies one either.
