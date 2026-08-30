# ORION-08 real-domain transfer on Defects4J — findings V1

**Terminal: `THEOREM_PREDICTS_REAL_TRANSFER_D4J`.**

Theorem 2 says a refinement strictly decreases regret **exactly when** it splits an
action-impure fibre. On 12 Defects4J projects — 597 bugs, 139,500 decision rows —
the prediction computed from a training half alone matched the observed direction
on **12 of 12**, with no disagreements.

| project | tests | coarse fibres | refined | predicted | observed | regret coarse → refined |
|---|---|---|---|---|---|---|
| Chart | 137 | 15 | 24 | value | value | 0.0198 → 0.0084 |
| Cli | 74 | 10 | 19 | value | value | 0.0286 → 0.0229 |
| Closure | 233 | 8 | 16 | value | value | 0.0113 → 0.0055 |
| Codec | 23 | 6 | 13 | value | value | 0.0432 → 0.0213 |
| Collections | 25 | 11 | 22 | value | value | 0.0456 → 0.0063 |
| Compress | 68 | 20 | 28 | value | value | 0.0240 → 0.0124 |
| **Csv** | **12** | **3** | **5** | **no value** | **no value** | **0.0286 → 0.0286** |
| Gson | 84 | 8 | 14 | value | value | 0.0128 → 0.0102 |
| Lang | 77 | 10 | 22 | value | value | 0.0225 → 0.0048 |
| Math | 514 | 84 | 134 | value | value | 0.0041 → 0.0016 |
| Mockito | 289 | 67 | 93 | value | value | 0.0076 → 0.0047 |
| Time | 121 | 6 | 13 | value | value | 0.0178 → 0.0081 |

## The no-value stratum is real, and it is the point

A theorem of the form "exactly when" is only tested if something lands on the
"not" side. Csv does, and not by accident of small numbers — the mechanism is
legible.

Csv has 12 candidate tests. Its `org.apache.commons.csv` fibre splits into
`exact` (p=0.556), `prefix` (p=0.200) and `none` (p=0.060). Under the frozen
utility the optimal action is *run* whenever the catch probability exceeds
`0.05/2.05 ≈ 0.0244`, and **all three sub-fibres clear it**. The refinement
splits the fibre and every piece still says run, so regret is unchanged to the
last digit. Its other two packages have one sub-fibre each and cannot be split at
all.

Cli, the neighbouring small project, does the opposite: its `cli` fibre splits
`exact` (p=0.389, run) from `none` (p=0.014, skip) and `prefix` (p=0.000, skip).
Impure, so refinement pays.

This gives the finding a mechanism rather than a correlation. **Whether typed
state is worth anything depends on the size of the candidate set relative to the
cost of acting on it.** With twelve tests in the suite, running one is so cheap
against the chance it catches something that the answer is always run, and knowing
*which class changed* adds nothing to a decision already settled. With five
hundred, the same knowledge is what separates the two percent worth running from
the rest. The theorem does not merely survive contact with a real domain; it
identifies which real domains it has anything to say about.

## What this does not show

**Out-of-sample transfer is not implied and does not uniformly hold.** Fitting the
per-fibre actions on the training half and applying them to held-out bugs, the
refinement helps on 10 of 12 projects and fails on **Cli** and **Csv**. That is
the same pattern the CC18 leg found and it is reported here for the same reason:
the theorem is a statement about the distribution its fibres are defined on, and
carrying it to unseen data is a different claim that this study does not make.

The decision is scored on Defects4J *metadata*: modified classes, trigger tests
and relevant tests. No Java was compiled and no test was executed. That is
sufficient for the question asked — which tests catch which bugs is exactly what
`trigger_tests` records — but it means run cost is modelled as a constant per
test class rather than measured, and a real selective-testing system would face
per-test wall-clock that varies by orders of magnitude.

The candidate set is the union of `relevant_tests` over the training bugs, so this
measures typed state's value *given* the dependency analysis has already run. It
says nothing about replacing that analysis.

## Amendment

The refined binding was changed before any catch rate was computed, because the
one committed in `PROTOCOL_V1.md` produced 72.7% singleton fibres and would have
returned a meaningless pass. `AMENDMENT_V1_BINDING.md` records the measurement
that forced it and what stayed fixed. A degeneracy gate now sits in the runner;
the worst project under the replacement binding is Collections at 27%.

## Both legs

With the CC18 leg (`real-transfer-cc18-v1`, terminal
`THEOREM_PREDICTS_REAL_TRANSFER`), the successor's two structurally different
decision families are both complete: a tabular classification decision under a
cost matrix, and a selection decision over a test suite. Neither shares anything
with the other except the theorem.
