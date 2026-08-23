# RETRACTION — the QG-35 headline separation counts are null-reproducible

An internal adversarial referee pass returned **REJECT**, and its central
objection is **correct**. I verified it independently before accepting it. The
affected claims are retracted here rather than quietly reworded.

Full report: `QG_ADVERSARIAL_REFEREE_REPORT.md`. Check:
`research/extensions/orion-qg/qg_null_model_check.py`.

## Objection 1 — the counts are identities

`85 of 92` and `708 of 715` were presented as measurements of how badly
selection fails. They are **restatements of the joint class-size histogram**:

```
histogram {1:7, 2:22, 3:6, 4:6, 6:25, 8:2, 12:14, 24:8, 48:2}
92 - 7 singletons = 85        715 - 7 singleton types = 708
```

Every non-singleton class splits — verified. So the numbers are forced the
moment the histogram is known, and the QG-34 freeze **printed that histogram
before any solver ran**.

## Objection 2 — the headline numbers survive destruction of the object

Null model: keep bulk, spectrum, the 92 joint classes and every existence
quantity **exactly**; shuffle only each row's frame-index alignment. This
destroys all TARE content in the one dimension the selection claims read.

| | classes split | types | `D_*` | `F*` | `U*` | regret 0→3 |
|---|---|---|---|---|---|---|
| **real** | 85/92 | 708/715 | 3 | 4 | 5 | 5,3,2,0 |
| null seed 1 | 85/92 | 708/715 | 3 | 4 | 5 | 5,3,1,0 |
| null seed 2 | 85/92 | 708/715 | 3 | 4 | — | 5,3,1,0 |
| null seed 3 | 85/92 | 708/715 | 3 | 4 | — | 5,3,1,0 |

I reproduced the counts on all three seeds myself, with the spectrum and every
optimal value bit-identical to the real table.

**So QG-35(b)'s counts, QG-34's `D_* = 3`, QG-32c's `F* = 4`, and QG-39's
headline regret of 5 do not measure TARE.** They are generic consequences of an
index-forgetting summary over a table with these class sizes.

## Further objections I accept

- **QG-35(a) is a tautology.** `spec = sorted(row)`, so the spectrum *is* the
  achievable-cost multiset. "Every function of the multiset is determined by the
  multiset" — the 0/92 verification is a unit test of `sorted`.
- **`D_* >= 3` is forced** by the class-size histogram plus max arity 6
  (`ceil(log_6 48) = 3`). The solver was needed only for achievability.
- **QG-35(b) qualitatively is pigeonhole**: 646 distinct optimal-frame sets over
  92 classes.
- **"Sharpens QG-2" is a non-sequitur.** QG-2's target is an existence predicate
  under a reweighted objective; QG-35(a) puts that predicate among the quantities
  that split 0/92. Different predicate, different objective, opposite sign.
- **bulk+spectrum is a strawman.** C1 establishes it is index-forgetting *by
  construction*; QG-35/36 then show an index-forgetting summary cannot answer an
  index-dependent question.

## What actually survives

- **All arithmetic.** The referee rebuilt every number from base primitives with
  **zero discrepancies**. Nothing here is a computational error.
- **The depth *distribution* is genuinely non-null**: real `{0:7,1:30,2:39,3:16}`
  against null `{0:7,1:42,2:34,3:9}`, and regret at budget 2 is 2 real versus 1
  null. **That residual is the only place TARE-specific signal was demonstrated**,
  and it is not what was reported as the result.
- **`U* = 5` exactly**, by complete enumeration. The referee notes the shuffled
  table is *strictly easier to cover* (384 masks vs 168, each covering more pairs)
  and still needs 5 — which makes 5 look generic too, but the enumeration stands.
- **QG-40/41/42 cross-compiler transfer** stands as computation, but its
  interpretation weakens: if the phenomenon is generic, finding it in Qiskit,
  pytket and SixLCU confirms a generic fact rather than a shared mechanism.

## The lesson

A claim of the form "X is not determined by Y" needs a null, because
non-determination is the **generic** case. I ran shuffle-equal-`n` nulls in other
lanes and did not run one here. The referee did, in one pass, and it cost the
headline.

## Status of the affected atoms

`QG35`, `QG35b`, `QG36`, `QG39`, `QG32c` are **demoted from contributions to
internal machine-checked notes**. Their authority blocks already said
`novelty_claim: false` / `proof_authority: false`; the defect was in promoting
them past that, and this document is the correction.
