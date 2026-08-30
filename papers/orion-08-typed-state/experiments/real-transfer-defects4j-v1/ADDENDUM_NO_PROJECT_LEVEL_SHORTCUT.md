# There is no project-level shortcut for the fibre-level test

**Post-hoc analysis of an already-reported result. No parameter is fitted and no
terminal is changed.** `FINDINGS_V1.md` explains the Csv no-value case by the size
of the candidate set relative to the cost of acting on it. That explanation
suggests a shortcut worth testing, because if it held it would let a practitioner
decide whether typed state can help *before* computing any fibre.

## The shortcut, and why it is attractive

The theorem's criterion needs the catch rate of every sub-fibre. The cheap
substitute is a project-level statistic: does the frozen threshold
`0.05/2.05 ≈ 0.0244` lie between a project's smallest and largest sub-fibre rate?
If it does not, every fibre agrees and refinement cannot pay.

## It fails, and it fails exactly where it matters

| | brackets threshold | value observed |
|---|---|---|
| 11 projects | yes | yes |
| **Csv** | **yes** | **no** |

Eleven of twelve is not the number to read. The single error is on **the only
no-value project in the study**, so the shortcut's false-positive rate on the
class it exists to identify is 100%. A test that is right whenever the answer is
"yes" and wrong whenever it is "no" carries no information.

## Why it fails

Csv's project-level range is `[0.0000, 0.5556]`, which brackets the threshold. But
the range pools sub-fibres across different coarse fibres, and a threshold can only
be *crossed* inside one:

| Csv coarse fibre | sub-fibre rates | sub-fibres | straddles 0.0244 |
|---|---|---|---|
| `org.apache.commons.csv` | 0.060, 0.200, 0.556 | 3 | **no — all above** |
| `…csv.bugs` | 0.000 | 1 | no — cannot, n=1 |
| `…csv.issues` | 0.000 | 1 | no — cannot, n=1 |

The `0.0000` that made the project-level range bracket the threshold comes from two
fibres that have **one sub-fibre each** and therefore cannot disagree with anything.
Pooling them with the `csv` fibre's rates manufactures a crossing that exists in no
fibre.

Applied per coarse fibre — does any fibre with at least two sub-fibres have rates
straddling the threshold — the rule is right on **12 of 12**. But that is the
theorem's own criterion restated in rate terms, not a cheaper substitute for it.

## What this adds

The fibre-level computation is **necessary**, not merely sufficient. The natural
aggregate that a practitioner would reach for first is not a conservative
approximation of it: it is wrong in the one direction that costs something, and it
is wrong because pooling across fibres destroys the very structure the theorem is
about.

This is stated as a negative about a shortcut, not as support for the theorem. The
theorem's transfer result stands on `RESULTS_V1.json` and is unaffected.
