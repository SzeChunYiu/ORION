# ORION-10 fibre criterion V2 — findings

**Terminal: `FIBRE_CONSTANCY_REFUTED`.**

> **Coverage correction, added 2026-09-01.** This document calls its 740 rows "the full
> census" and reports results "over all 740 instances". That overstates what was
> enumerated. `FULL_CENSUS_RESULTS_V2.json` records `cap_hit: true` for **all ten
> panels**, with `template_pair_space` running 2,873–28,090 per panel against 740
> instances evaluated in total — the rows are an early prefix of the enumeration order,
> not a complete census, and the directory name repeats the same overstatement.
>
> **The terminal is unaffected.** Refuting constancy requires only exhibiting cost-mixed
> fibres, and six of seven were exhibited; a witness found in a prefix is still a witness.
> What the caps do undermine is any statement about a *range* — see the envelope in
> `REVIVAL_PASS_V1.md`, which carries the qualification in full, and
> `../vocabulary-minimality-v3-cap-lift/PROTOCOL_V3.md`, which lifts the caps twentyfold
> to test it.

The V1 packet's `CANNOT_CHECK_FIBRE_CONSTANCY_ON_SELECTED_WITNESSES` is resolved, and
it resolves against the criterion. The uniformity V1 observed was a selection artifact,
exactly as V1's own reasoning anticipated.

## Control passed

Required before any fibre claim, and met exactly:

| | V2 census | QG-7 frozen |
|---|---|---|
| instances evaluated | **740** | 740 |
| fourth-regime candidates | **64** | 64 |
| the 64 verbatim entries | **identical** | — |
| terminal | `QG7_FOURTH_SUPPORT2_REGIME_FOUND` | same |

**740 rows serialised**, against QG-7's 64. QG-7's frozen result file was read-only
input and is unmodified.

## The result

Criterion (certificate-explanation-gap-v1, Theorem 2): an exact Psi-only explanation
exists **iff** cost is constant on every Psi-fibre.

Keyed on `f_Bprime`, over all 740 instances (every one has finite `f_Bprime`):

```
fibres:            7
cost-mixed fibres: 6
```

| `f_Bprime` | `C_Dxx` values observed | instances |
|---|---|---|
| 5 | 4, 5 | 54 |
| 6 | 3, 4, 5, 6 | 145 |
| 7 | 4, 5, 6, 7 | 219 |
| 8 | 5, 6, 7, 8 | 211 |
| 9 | 6, 7, 8, 9 | 87 |
| 10 | 9, 10 | 14 |

Offset `f_Bprime − C_Dxx` across the full census:

```
{0: 389, 1: 325, 2: 13, 3: 13}     offset uniformly 1: False
```

**Six of seven fibres are cost-mixed. Cost is not constant on `f_Bprime`-fibres, so the
named vocabulary B' does not admit an exact Psi-only explanation on the real instance
space.**

## Why V1 saw the opposite, and was right to distrust it

Restricting the identical computation to V1's selected subset reproduces V1 exactly:

```
n = 64        cost-mixed fibres = 0        offset distribution = {1: 64}
```

Uniform offset 1, zero mixed fibres — on 64 instances selected by
`C_D++ < min(C_D+, f_B')`. Conditioning on that gap *is* what produces the uniformity.
V1 stated this and declined to claim fibre-constancy from it; the full census confirms
the caution was correct. Reading the 64 naively would have asserted the exact opposite
of the truth.

This is a clean demonstration that a selection-conditioned sample can invert a
structural conclusion: 0/7 mixed fibres on the selected view, 6/7 on the space.

## What changed and what did not

The V2 runner is **10 added lines** against QG-7's generator — it records each
evaluated instance's fibre fields where the census already counts them. Nothing
computed changed; only what is written out. The control above is the evidence for that:
identical totals, identical 64, identical terminal.

## Scope

This refutes fibre-constancy for **B' keyed on `f_Bprime`, on this instance space**. It
does not speak to other vocabularies, other keys, or the abstract-space companion
result that V1 says closed the UNIVERSAL half. It does not license any claim about
ORION-10's headline terminal.

`scientific_authority_delta: NONE` — successor evidence under a new identity.
